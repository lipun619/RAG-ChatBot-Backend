# Projects Portfolio

---

## RAG ChatBot Backend

- **Description:** A LangGraph-based Retrieval-Augmented Generation (RAG) chatbot backend that answers questions using knowledge ingested from multiple sources including GitHub repos, portfolio website, resume PDF, and local markdown files.
- **Work/Functionality:**
  - 4-node LangGraph StateGraph workflow: validate query → retrieve context → check relevance → generate answer
  - Automated ingestion pipeline with APScheduler (runs every 24 hours)
  - SSE streaming responses via FastAPI
  - ChromaDB vector storage with SentenceTransformers embeddings (all-MiniLM-L6-v2)
  - Rate limiting (5 req/min per IP) and CORS support
- **Technologies:** Python, FastAPI, LangGraph, LangChain, ChromaDB, OpenAI GPT-4o-mini, SentenceTransformers, APScheduler, PyGithub, BeautifulSoup

---

## RAG Chatbot

- **Description:** A RAG-powered AI chatbot application built for intelligent conversational interactions using document retrieval and natural language understanding.
- **Work/Functionality:**
  - Multi-turn dialogue handling for seamless conversations
  - Retrieval-Augmented Generation for context-aware responses
  - Customizable response patterns and configurable parameters
  - Integration-ready architecture for various platforms
- **Technologies:** Python, LangChain, Streamlit, OpenAI

---

## ShoppingCartBackend

- **Description:** A backend API for a shopping cart system built with ASP.NET Core, following N-Layer architecture with clean separation of concerns.
- **Work/Functionality:**
  - RESTful CRUD API endpoints for product management (`GET`, `POST`, `PUT`, `DELETE`)
  - Repository Pattern and Unit of Work Pattern for data access abstraction
  - Dependency Injection for loose coupling and testability
  - N-Layer architecture: Presentation, Business, and Data Access layers
- **Technologies:** C#, ASP.NET Core, .NET

---

## ShoppingCartFrontend

- **Description:** An Angular frontend application providing a user-friendly interface for managing a shopping cart with product browsing, cart management, and checkout.
- **Work/Functionality:**
  - Product listing with add-to-cart functionality
  - Shopping cart with quantity updates and item removal
  - User authentication with secure login
  - Step-by-step checkout process
- **Technologies:** Angular, TypeScript, HTML, SCSS, Bootstrap, RxJS

---

## GlobalExceptionHandling

- **Description:** Demonstrates Global Exception Handling in ASP.NET Core using a custom middleware component for centralized, clean error management.
- **Work/Functionality:**
  - Centralized error handling middleware for the request pipeline
  - Configurable error response structures
  - Support for multiple logging strategies
  - Keeps business logic free from error-handling clutter
- **Technologies:** C#, ASP.NET Core

---

## KitchenRoutingSystem

- **Description:** A console application demonstrating a Kitchen Routing System that manages task allocation and order routing across multiple POS terminals.
- **Work/Functionality:**
  - Task allocation to kitchen staff based on expertise and availability
  - Multi-POS terminal support for order routing
  - Real-time task status tracking and notifications
  - Performance metrics for workflow optimization
- **Technologies:** C#, .NET Console Application

---

## ChatbotLibrary

- **Description:** An Angular-based AI Chatbot library designed as a reusable, embeddable component for integrating conversational agents into web applications.
- **Work/Functionality:**
  - NLP-powered chatbot with customizable responses
  - Bottom-right positioning with minimize functionality
  - Multi-platform deployment support (web, mobile, messaging)
  - Built as an Angular library for easy integration
- **Technologies:** Angular, TypeScript, HTML, SCSS

---

## ANGULAR-LIFECYCLE-HOOKS

- **Description:** An educational Angular application that demonstrates all 8 Angular lifecycle hooks with practical, interactive examples viewable in the browser console.
- **Work/Functionality:**
  - Implements all 8 lifecycle hooks: `ngOnChanges`, `ngOnInit`, `ngDoCheck`, `ngAfterContentInit`, `ngAfterContentChecked`, `ngAfterViewInit`, `ngAfterViewChecked`, `ngOnDestroy`
  - Parent-child component interaction to trigger `ngOnChanges`
  - Console-based logging for real-time hook observation
- **Technologies:** Angular 14, TypeScript, Bootstrap 5

---

## Lazy-Load-Standalone-Component-Angular

- **Description:** An Angular project demonstrating lazy loading of standalone components for optimized application performance and reduced initial bundle size.
- **Work/Functionality:**
  - Lazy loading implementation for standalone Angular components
  - Route-based code splitting for performance optimization
  - Demonstrates modern Angular architecture patterns
- **Technologies:** Angular, TypeScript, JavaScript, HTML, SCSS

---

## Blazor App

- **Description:** A Blazor WebAssembly application deployed on Azure Static Web Apps, featuring a client-server architecture with shared models.
- **Work/Functionality:**
  - Blazor client-side SPA with C# in the browser
  - ASP.NET Core backend API layer
  - Shared models between client and server
  - Azure Static Web Apps deployment via GitHub Actions CI/CD
- **Technologies:** Blazor, C#, ASP.NET Core, HTML, CSS, Azure Static Web Apps

---

## Learning App 1995

- **Description:** An ASP.NET Core Razor Pages web application showcasing modern web development fundamentals with responsive design and built-in security features.
- **Work/Functionality:**
  - Razor Pages architecture with master layout templates
  - HTTPS enforcement with HSTS headers (30-day default)
  - Built-in CSRF protection and form validation (client + server)
  - Static asset management with bundling support
  - Integrated error handling and structured logging
- **Technologies:** ASP.NET Core (.NET 9.0), C#, Razor Pages, Bootstrap 5, jQuery, HTML, CSS

---

## Expense Tracker MCP Server

- **Description:** A Model Context Protocol (MCP) server application for tracking expenses with categorization, reporting, and API integration capabilities.
- **Work/Functionality:**
  - Expense CRUD operations with category management
  - Monthly, quarterly, and yearly expense reporting
  - User authentication and secure access
  - RESTful API endpoints for third-party integration
- **Technologies:** Python

---

## JWTRefreshTokens

- **Description:** An ASP.NET Core Web API project implementing JWT authentication with refresh token support for secure, stateless API authorization.
- **Work/Functionality:**
  - JWT token generation and validation
  - Refresh token issuance and rotation for extended sessions
  - Secure token validation pipeline
- **Technologies:** C#, ASP.NET Core, JWT

---

## HSPA (Housing Sales & Property Advertising)

- **Description:** A full-stack property trading application covering various Angular features with a .NET Web API backend, deployed to Firebase.
- **Work/Functionality:**
  - Property listing and management features
  - Angular frontend with multiple feature modules
  - .NET Web API backend for data operations
  - Firebase deployment for hosting
- **Technologies:** Angular, TypeScript, C#, ASP.NET Core Web API, HTML, CSS, JavaScript, Firebase

---

## UIAngularAdDemoOrExcelReport

- **Description:** An Angular frontend demonstrating Azure Active Directory authentication using MSAL and Excel report template generation.
- **Work/Functionality:**
  - Azure AD integration with MSAL (Microsoft Authentication Library)
  - SSO (Single Sign-On) authentication flow
  - Excel report template generation and download
- **Technologies:** Angular 11, TypeScript, MSAL, HTML, SCSS, JavaScript

---

## WebApiAngularAdDemoOrExcelReport

- **Description:** The ASP.NET Core Web API backend companion for Azure AD authentication and Excel report generation, implementing business logic and data access layers.
- **Work/Functionality:**
  - Azure AD token validation and authorization
  - Excel report generation via backend services
  - N-Layer architecture with Business Component and Data Component layers
- **Technologies:** C#, ASP.NET Core Web API, MSAL

---

## Portfolio Website

- **Description:** A personal portfolio website showcasing professional profile, skills, and projects, hosted on Firebase.
- **Work/Functionality:**
  - Responsive personal portfolio with project showcase
  - Firebase hosting for fast, reliable delivery
  - Clean, modern UI with custom styling and interactivity
- **Technologies:** HTML, CSS, JavaScript, Firebase
