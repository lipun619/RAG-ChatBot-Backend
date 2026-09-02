import unittest
from unittest.mock import patch

import app.rag.graph as graph
import app.rag.retriever as retriever


class RetrieverEnvironmentTests(unittest.TestCase):
    def test_get_retriever_reports_python_and_venv_fix(self):
        with patch.object(retriever, "HuggingFaceEmbeddings", side_effect=ImportError("torch missing")):
            with self.assertRaises(RuntimeError) as ctx:
                retriever.get_retriever()

        message = str(ctx.exception)
        self.assertIn("Python 3.12", message)
        self.assertIn("recreate the virtual environment", message)
        self.assertIn("torch", message.lower())


class OpenAIQuotaHandlingTests(unittest.TestCase):
    def test_check_relevance_handles_quota_exhaustion(self):
        class DummyPrompt:
            def __or__(self, other):
                return DummyChain()

        class DummyChain:
            def invoke(self, payload):
                raise RuntimeError("Error code: 429 - {'error': {'code': 'credit_balance_exhausted'}}")

        with patch("langchain_core.prompts.ChatPromptTemplate.from_template", return_value=DummyPrompt()), \
             patch("langchain_openai.ChatOpenAI"):
            state = {"question": "Tell me about Lipun", "context": [type("Doc", (), {"page_content": "Lipun works in AI"})()]}
            result = graph.check_relevance(state)
            self.assertEqual(result["context"], state["context"])

    def test_generate_answer_handles_quota_exhaustion(self):
        class DummyPrompt:
            def __or__(self, other):
                return DummyChain()

        class DummyChain:
            def invoke(self, payload):
                raise RuntimeError("Error code: 429 - {'error': {'code': 'credit_balance_exhausted'}}")

        with patch("langchain_core.prompts.ChatPromptTemplate.from_template", return_value=DummyPrompt()), \
             patch("langchain_openai.ChatOpenAI"):
            state = {"question": "Tell me about Lipun", "context": [type("Doc", (), {"page_content": "Lipun works in AI"})()]}
            result = graph.generate_answer(state)
            self.assertIn("no remaining credits", result["answer"].lower())
            self.assertIn("billing", result["answer"].lower())


if __name__ == "__main__":
    unittest.main()
