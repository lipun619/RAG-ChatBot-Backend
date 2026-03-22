import logging
from collections.abc import AsyncGenerator
from typing import TypedDict

logger = logging.getLogger(__name__)


# --- State ---


GREETINGS = {"hi", "hello", "hey", "yoo", "Hi Lipun", "Hello Lipun", "greetings", "good morning", "good afternoon", "good evening", "howdy", "what's up", "sup"}


class ChatState(TypedDict):
    question: str
    context: list
    answer: str
    is_valid: bool
    is_greeting: bool


# --- Nodes ---


def validate_query(state: ChatState) -> dict:
    """Check if the question is valid (non-empty and reasonable length)."""
    question = state["question"].strip()
    is_valid = bool(question) and len(question) >= 2
    is_greeting = question.lower().rstrip("!?., ") in GREETINGS
    if not is_valid:
        logger.warning("Invalid query rejected: '%s'", state["question"])
    return {"is_valid": is_valid, "is_greeting": is_greeting}


def retrieve_context(state: ChatState) -> dict:
    """Retrieve relevant documents from the ChromaDB vector store."""
    from app.rag.retriever import get_retriever

    retriever = get_retriever()
    docs = retriever.invoke(state["question"])
    logger.info("Retrieved %d documents for query: '%s'", len(docs), state["question"])
    return {"context": docs}


def check_relevance(state: ChatState) -> dict:
    """Use LLM to verify that retrieved context is relevant to the question."""
    if not state["context"]:
        logger.warning("No context retrieved — marking as irrelevant")
        return {"context": []}

    context_text = "\n".join(doc.page_content[:200] for doc in state["context"])

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = ChatPromptTemplate.from_template(
        "Given the question: '{question}'\n\n"
        "And the following context snippets:\n{context}\n\n"
        "Is this context relevant to answering the question? "
        "Reply with only 'yes' or 'no'."
    )
    chain = prompt | llm
    result = chain.invoke(
        {"question": state["question"], "context": context_text}
    )

    is_relevant = "yes" in result.content.lower()
    if not is_relevant:
        logger.warning("Context deemed irrelevant for: '%s'", state["question"])
        return {"context": []}

    return {"context": state["context"]}


def generate_answer(state: ChatState) -> dict:
    """Generate an answer using the LLM with retrieved context."""
    if not state["context"]:
        return {
            "answer": (
                "I don't have enough relevant information to answer that question. "
                "Please ask something about Lipun Patel's skills, experience, or projects."
            )
        }

    context_text = "\n\n".join(doc.page_content for doc in state["context"])

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    prompt = ChatPromptTemplate.from_template(
        "You are a helpful assistant that answers questions about Lipun Patel. "
        "Use ONLY the following context to answer. If the context doesn't contain "
        "enough information, say so honestly.\n\n"
        "Format your response in clean, readable Markdown:\n"
        "- Use bullet points or numbered lists for multiple items.\n"
        "- Use **bold** for key terms or highlights.\n"
        "- Use headings (###) only when the answer covers multiple distinct topics.\n"
        "- Keep paragraphs short and scannable.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )
    chain = prompt | llm
    result = chain.invoke(
        {"question": state["question"], "context": context_text}
    )

    return {"answer": result.content}


# --- Graph ---


def _route_after_validation(state: ChatState) -> str:
    """Route based on query validation result."""
    if not state["is_valid"]:
        return "invalid_response"
    if state["is_greeting"]:
        return "greeting_response"
    return "retrieve_context"


def greeting_response(state: ChatState) -> dict:
    """Return a friendly greeting."""
    return {
        "answer": (
            "Hello! 👋 I'm Lipun's AI assistant. "
            "Feel free to ask me about his skills, experience, or projects!"
        )
    }


def invalid_response(state: ChatState) -> dict:
    """Return a message for invalid queries."""
    return {"answer": "Please provide a valid question."}


def build_graph():
    """Build and compile the LangGraph workflow."""
    from langgraph.graph import END, StateGraph

    workflow = StateGraph(ChatState)

    # Add nodes
    workflow.add_node("validate_query", validate_query)
    workflow.add_node("retrieve_context", retrieve_context)
    workflow.add_node("check_relevance", check_relevance)
    workflow.add_node("generate_answer", generate_answer)
    workflow.add_node("greeting_response", greeting_response)
    workflow.add_node("invalid_response", invalid_response)

    # Set entry point
    workflow.set_entry_point("validate_query")

    # Add edges
    workflow.add_conditional_edges(
        "validate_query",
        _route_after_validation,
        {
            "retrieve_context": "retrieve_context",
            "greeting_response": "greeting_response",
            "invalid_response": "invalid_response",
        },
    )
    workflow.add_edge("retrieve_context", "check_relevance")
    workflow.add_edge("check_relevance", "generate_answer")
    workflow.add_edge("generate_answer", END)
    workflow.add_edge("greeting_response", END)
    workflow.add_edge("invalid_response", END)

    return workflow.compile()


# Compiled graph (lazy singleton)
_graph = None


def _get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


async def run_graph(question: str) -> AsyncGenerator[str, None]:
    """Invoke the LangGraph workflow and yield the answer in chunks for streaming."""
    initial_state: ChatState = {
        "question": question,
        "context": [],
        "answer": "",
        "is_valid": False,
        "is_greeting": False,
    }

    result = await _get_graph().ainvoke(initial_state)
    answer = result.get("answer", "Sorry, I could not generate a response.")

    # Yield answer in chunks for SSE streaming
    chunk_size = 20
    for i in range(0, len(answer), chunk_size):
        yield answer[i : i + chunk_size]


async def run_graph_sync(question: str) -> str:
    """Invoke the LangGraph workflow and return the full answer as a string."""
    initial_state: ChatState = {
        "question": question,
        "context": [],
        "answer": "",
        "is_valid": False,
        "is_greeting": False,
    }

    result = await _get_graph().ainvoke(initial_state)
    return result.get("answer", "Sorry, I could not generate a response.")
