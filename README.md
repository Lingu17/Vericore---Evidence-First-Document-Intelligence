# DocuPilot

> **"Ask your documents. Verify every answer."**

> *Evidence-First Document Intelligence for Business Teams.*

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat-square)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_18_%2B_Vite-61DAFB.svg?style=flat-square)](https://react.dev/)
[![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB_Local-FF6F00.svg?style=flat-square)](https://www.trychroma.com/)
[![Sentence-Transformers](https://img.shields.io/badge/Embeddings-MiniLM--L6--v2_Local-blue.svg?style=flat-square)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![Groq](https://img.shields.io/badge/LLM-Groq_API-F55036.svg?style=flat-square)](https://groq.com/)
[![Tests](https://img.shields.io/badge/Tests-18_Passed-16A34A.svg?style=flat-square)]()

---

## Overview

**DocuPilot** is an evidence-first document intelligence workspace designed for business documents and knowledge workflows.

Rather than functioning as an unconstrained chat wrapper, DocuPilot answers questions using retrieved and verified document context. Every grounded answer is coupled with a transparent, clickable **Evidence Trail** showing the source file, page number, section title, and stored evidence passage used for the answer.

When supporting information does not exist in the uploaded documents, DocuPilot deterministically responds with:

> **"Information not available in the uploaded documents."**

This prevents the system from confidently inventing unsupported information.

![DocuPilot Architecture](docs/architecture.png)

---

## Problem

Business users often spend significant time searching through lengthy documents such as PDF policies, employee handbooks, SOPs, benefits documents, and internal agreements.

Traditional AI document assistants can introduce several problems:

1. **Hallucinations & Confabulation:** LLMs may generate plausible-sounding information when the required information is missing.

2. **Untraceable Answers:** Answers may not clearly identify the document, page, section, or evidence used to generate them.

3. **Unnecessary Cloud Costs:** Sending complete documents or large contexts to external embedding and LLM APIs can increase token consumption and API usage.

4. **Limited Evidence Inspection:** Simple document chat interfaces may provide answers without giving users a convenient way to inspect the supporting evidence.

---

## Solution

DocuPilot provides an **Evidence-First RAG Architecture**:

- **Local Embeddings (`all-MiniLM-L6-v2`) & ChromaDB:** Embeddings and vector storage run locally, avoiding external embedding API costs.

- **Hybrid Retrieval & Relevance Gating:** Semantic similarity is combined with keyword coverage to improve retrieval. Queries with insufficient evidence are rejected before unnecessary LLM generation.

- **Verified Attribution:** The LLM receives and returns internal `[SOURCE_ID=...]` identifiers. The backend resolves these identifiers against stored document metadata before displaying evidence.

- **Grounded Generation:** Only selected document evidence is provided to the LLM instead of sending complete uploaded documents.

- **B2B Workspace:** A desktop-first 3-column layout containing Document Manager, Grounded Chat Timeline, and an inspectable Evidence Drawer.

---

## Key Features

- **Document Ingestion (PDF & TXT):** Page-by-page PDF extraction using PyMuPDF with text normalization and heading detection.

- **SHA-256 Deduplication:** Duplicate document uploads are detected using content hashing, preventing unnecessary re-processing and embedding.

- **Intelligent Page-Aware Chunking:** Text is split along paragraph, sentence, and section boundaries while preserving `document_id`, `filename`, `page`, `section`, and `chunk_id`.

- **Local Embeddings:** Fast local embeddings using `sentence-transformers/all-MiniLM-L6-v2` with a 384-dimensional vector representation.

- **Persistent ChromaDB Vector Store:** Persistent local vector storage with similarity search and document-level deletion.

- **Hybrid Retrieval:** Combines semantic similarity with keyword coverage and reranking to improve retrieval for both natural-language queries and precise policy terms.

- **Adaptive Context Sizing:** Dynamically selects a small number of relevant chunks based on retrieval relevance.

- **Answer Caching:** In-memory hashing avoids repeated LLM calls for identical questions with the same document scope and evidence.

- **Evidence Confidence Badging:** Deterministic High / Medium / Low evidence confidence based on retrieval and grounding signals rather than fabricated probability percentages.

- **Smart Suggested Questions:** Generates useful document questions from section headings and document structure without requiring LLM calls during ingestion.

- **Evidence Trail Side Drawer:** Click any source badge to inspect the source filename, page, section, match information, exact stored excerpt, and chunk identifier.

- **Information Not Found Cards:** Clear visual states for unsupported questions instead of fabricated answers.

- **Multi-Document Reasoning:** Retrieves and synthesizes evidence across multiple uploaded documents when relevant.

- **Lightweight Conversation Memory:** Supports contextual follow-up questions while limiting the amount of previous conversation passed to the LLM.

---

## Architecture

```text
User
 │
 ▼
React + TypeScript UI
 │
 ▼
FastAPI Backend
 │
 ├──────────────────────────────────────┐
 │                                      │
 ▼                                      ▼
Document Processing                Query Processing
 │                                      │
 ├── PDF → PyMuPDF                      ├── Normalize Query
 └── TXT → Text Parser                  │
                                        ▼
                                MiniLM Query Embedding
 │                                      │
 ▼                                      ▼
Section-Aware Chunking            ChromaDB Search
 │                                      │
 ▼                                      ▼
MiniLM Document Embeddings         Candidate Pool
 │                                      │
 └───────────────► ChromaDB ◄───────────┘
                         │
                         ▼
                Hybrid Re-ranking
                 │              │
                 │              ├── Keyword Coverage
                 │              │
                 └── Semantic Similarity
                         │
                         ▼
                Relevance / Grounding Gate
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
     Insufficient Evidence    Sufficient Evidence
              │                     │
              ▼                     ▼
     Deterministic           Evidence Selection
       NOT_FOUND                    │
                                    ▼
                              Answer Cache
                                    │
                          ┌─────────┴─────────┐
                          │                   │
                       Cache HIT          Cache MISS
                          │                   │
                          │                   ▼
                          │            Grounded Prompt
                          │                   │
                          │                   ▼
                          │            Groq GPT-OSS 20B
                          │                   │
                          │                   ▼
                          │          Source ID Validation
                          │                   │
                          └─────────┬─────────┘
                                    ▼
                         Verified Answer + Evidence
                                    │
                                    ▼
                            React Evidence Trail
Retrieval Pipeline

DocuPilot follows this retrieval flow:

User Question
      │
      ▼
Query Normalization
      │
      ▼
Local Query Embedding
      │
      ▼
ChromaDB Semantic Search
      │
      ▼
Candidate Pool
      │
      ▼
Hybrid Re-ranking
      │
      ├── Semantic Similarity
      │
      └── Keyword Coverage
      │
      ▼
Evidence / Relevance Gate
      │
      ├── Insufficient Evidence
      │        │
      │        ▼
      │   Deterministic NOT_FOUND
      │
      └── Sufficient Evidence
               │
               ▼
        Adaptive Evidence Selection
               │
               ▼
          Answer Cache
               │
               ▼
        Grounded Prompt
               │
               ▼
          Groq GPT-OSS 20B
               │
               ▼
      Backend Source Validation
               │
               ▼
      Answer + Evidence Trail

Hallucination Prevention

Hallucination prevention is handled through multiple layers.

1. Retrieval Before Generation

The LLM does not receive complete uploaded documents.

Only selected retrieved evidence chunks are passed to the generation step.

2. Hybrid Retrieval

Retrieval combines:

Semantic similarity
Keyword coverage
Candidate reranking

This improves retrieval for questions containing important policy terms, dates, numbers, and specific terminology.

3. Relevance / Grounding Gate

If retrieved evidence is not sufficiently relevant, the system returns the deterministic unknown response instead of asking the LLM to guess.

4. Grounded Prompting

The LLM is instructed to answer using only the supplied evidence.

5. Source Validation

Each retrieved chunk contains an internal source identifier.

The LLM returns source identifiers, and the backend resolves those identifiers against stored document metadata.

This prevents generated responses from independently fabricating:

Page numbers
File names
Section names
Evidence references
6. Concise Structured Answers

Answers are intentionally short and direct to reduce unnecessary generation and keep the response focused on the retrieved evidence.

Token Optimization

DocuPilot is designed to minimize unnecessary LLM usage.

Local Embeddings: Uses all-MiniLM-L6-v2 locally, avoiding external embedding API calls.
Retrieval Before Generation: Only a small number of top-scoring, deduplicated chunks are sent to Groq. Complete documents are never sent to the LLM.
Relevance Gating: Questions with insufficient evidence are rejected before unnecessary LLM generation.
Adaptive Evidence Selection: Highly relevant questions can use fewer evidence chunks, while moderately relevant questions can use additional supporting chunks.
Duplicate Evidence Removal: Near-duplicate chunks are filtered before context assembly.
Trimmed Context Payloads: Only required source metadata and extracted evidence are passed to the LLM.
Minimal System Prompt: A short instruction-focused prompt enforces factual grounding and structured output.
Minimal User Prompt: Clean QUESTION: and EVIDENCE: blocks reduce redundant prompt text.
Pruned Conversation History: Standalone questions do not require previous turns. Follow-up questions retain only the most recent conversation context.
Short Structured Output: Generation is capped at MAX_OUTPUT_TOKENS = 250 with TEMPERATURE = 0.
Backend Confidence Calculation: Evidence confidence is calculated in Python from retrieval signals rather than asking the LLM to self-rate confidence.
Zero-Token Suggested Questions: Suggested questions are generated deterministically from document structure without LLM calls.
SHA-256 Ingestion Deduplication: Duplicate uploads are detected using file hashes before unnecessary re-embedding.
Identical Query Caching: Repeated identical questions can return cached results without another LLM generation request.
Technology Stack
Backend
Language: Python 3.10+
Framework: FastAPI, Uvicorn
Validation: Pydantic v2, Pydantic Settings
Document Processing: PyMuPDF (pymupdf) for PDF, native text decoding for TXT
Embeddings: sentence-transformers
Embedding Model: all-MiniLM-L6-v2
Vector Database: ChromaDB persistent local storage
LLM Provider: Groq API
LLM Model: openai/gpt-oss-20b
Testing: Pytest, HTTPX
Frontend
Framework: React 18 with TypeScript
Build Tool: Vite
Styling: Tailwind CSS
Icons: Lucide React
Project Structure
DOCUPILOT/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py              # Grounded chat & RAG endpoints
│   │   │   ├── documents.py         # Upload, list, delete, suggestions
│   │   │   └── health.py            # Diagnostic & health endpoint
│   │   │
│   │   ├── core/
│   │   │   ├── config.py             # Settings & environment configuration
│   │   │   └── logging.py            # Structured logging
│   │   │
│   │   ├── models/
│   │   │   └── schemas.py            # Pydantic request/response models
│   │   │
│   │   ├── prompts/
│   │   │   └── qa_prompt.py          # Grounded QA prompt builder
│   │   │
│   │   ├── services/
│   │   │   ├── chunker.py            # Section-aware chunking
│   │   │   ├── confidence.py         # Evidence confidence calculator
│   │   │   ├── document_parser.py    # PDF & TXT extraction
│   │   │   ├── embeddings.py          # Local MiniLM embeddings
│   │   │   ├── llm.py                # LLM provider abstraction
│   │   │   ├── retriever.py          # Hybrid retrieval & reranking
│   │   │   ├── suggestions.py        # Suggested question generator
│   │   │   └── vector_store.py       # ChromaDB storage & metadata
│   │   │
│   │   ├── utils/
│   │   │   ├── hashing.py            # SHA-256 deduplication
│   │   │   └── text.py               # Text cleaning & keyword utilities
│   │   │
│   │   └── main.py                   # FastAPI application
│   │
│   ├── sample_documents/
│   │   ├── generate_samples.py       # Sample document generator
│   │   ├── NovaTech_Benefits_Policy.pdf
│   │   ├── NovaTech_Employee_Handbook.pdf
│   │   ├── NovaTech_Leave_Policy.pdf
│   │   └── NovaTech_Remote_Work_FAQ.txt
│   │
│   ├── tests/
│   │   ├── test_api.py
│   │   ├── test_chunker.py
│   │   ├── test_parser.py
│   │   └── test_retriever_confidence.py
│   │
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/                 # Chat UI components
│   │   │   ├── common/               # Shared UI components
│   │   │   ├── documents/            # Document management
│   │   │   ├── evidence/             # Evidence Trail components
│   │   │   └── layout/               # Application layout
│   │   │
│   │   ├── hooks/                    # React custom hooks
│   │   ├── lib/                      # Frontend utilities
│   │   ├── services/                 # API client
│   │   ├── types/                    # TypeScript interfaces
│   │   ├── App.tsx                   # Root application
│   │   ├── index.css                 # Global styling
│   │   └── main.tsx
│   │
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── docs/
│   └── architecture.png              # System architecture diagram
│
├── .env.example
└── README.md
Installation
Prerequisites
Python 3.10+
Node.js v18+
npm

Git
1. Clone the repository
git clone https://github.com/YOUR_GITHUB_USERNAME/docupilot.git
cd DOCUPILOT

Replace YOUR_GITHUB_USERNAME with the actual GitHub repository owner before publishing this README.

2. Backend Setup
cd backend

# Create virtual environment
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux / macOS
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
3. Frontend Setup
cd ../frontend
npm install
Environment Variables

Configure backend/.env:

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
USE_MOCK_LLM=false

# Generation
MAX_OUTPUT_TOKENS=250
TEMPERATURE=0
MAX_HISTORY_MESSAGES=2

# Vector Database
CHROMA_PATH=./chroma_db

# Local Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Retrieval
TOP_K=5
FINAL_CONTEXT_CHUNKS=3
SIMILARITY_THRESHOLD=0.48
STRONG_RELEVANCE_THRESHOLD=0.54
HIGH_RELEVANCE_THRESHOLD=0.62

# Chunking
CHUNK_SIZE=1200
CHUNK_OVERLAP=150

# Upload Limits
MAX_FILE_SIZE_MB=10

# Server
ENV=development
PORT=8000
HOST=0.0.0.0

Never commit .env or real API keys to Git.

Running Locally
Terminal 1: Start Backend Server
cd backend

# Make sure .venv is activated
uvicorn app.main:app --reload --port 8000

Backend:

http://localhost:8000

API documentation:

http://localhost:8000/docs
Terminal 2: Start Frontend Application
cd frontend
npm run dev

Frontend:

http://localhost:5173
API Endpoints
Method	Endpoint	Description
GET	/health	Application health and system information
GET	/api/documents	List indexed documents with metadata
POST	/api/documents/upload	Upload and index PDF/TXT documents
GET	/api/documents/{document_id}	Fetch metadata for a document
GET	/api/documents/{document_id}/suggestions	Get suggested questions
DELETE	/api/documents/{document_id}	Delete document and associated vectors
DELETE	/api/documents	Clear all indexed documents
POST	/api/chat	Submit a grounded document question
Testing
Run Tests
python -m pytest backend/tests -v
Test Suite Summary
18 passed

The final test suite covers:

✓ Health check endpoint
✓ Document upload
✓ Duplicate document detection
✓ Grounded question answering
✓ Unknown-question anti-hallucination behavior
✓ Empty question validation
✓ Chunking metadata preservation
✓ Section detection
✓ PDF parsing with page preservation
✓ TXT parsing
✓ Empty file rejection
✓ Unsupported file extension rejection
✓ Corrupt PDF rejection
✓ High-confidence retrieval
✓ Medium-confidence retrieval
✓ Low-confidence retrieval
✓ Grounding-aware confidence
✓ Hybrid retrieval / relevance behavior
Example Demo Questions

The following questions can be used with the sample employee handbook:

What are the normal working hours?

How many days per week can employees work remotely?

When does an employee receive their first performance review?

How many hours per week must an employee work to be considered full-time?

What should an employee do if they expect to arrive late?
Hallucination Test

Ask:

What is the company's annual performance bonus?

Expected behavior:

Information not available in the uploaded documents.

The system should not invent a bonus amount or generate unsupported information.

AI Tools Used

AI-assisted development tools were used during implementation for:

Exploring implementation approaches for RAG, retrieval, chunking, and grounding.
Debugging retrieval behavior and edge cases.
Reviewing code structure and generating test ideas.
Refining prompts and response behavior.
Improving documentation and README content.

AI-generated suggestions were reviewed, tested, debugged, and adapted before being included in the final implementation.

Design Decisions
Why Local Embeddings?

all-MiniLM-L6-v2 runs locally and avoids requiring a separate external embedding API.

This keeps the embedding pipeline simple and reduces external API dependency.

Why ChromaDB?

ChromaDB provides lightweight persistent vector storage suitable for a focused RAG application without requiring additional external infrastructure.

Why FastAPI?

FastAPI provides a clean API layer with request validation, automatic API documentation, and straightforward integration with the retrieval and LLM services.

Why React + TypeScript?

React provides a flexible interface for document management, chat, evidence inspection, and application state.

TypeScript improves type safety and maintainability across the frontend.

Why Hybrid Retrieval?

Pure semantic similarity can sometimes miss exact policy terminology, dates, numbers, and important keywords.

DocuPilot combines semantic similarity with keyword coverage and reranking to improve retrieval quality.

Why Deterministic Unknown Handling?

A document assistant should not treat every question as answerable.

If sufficient evidence cannot be retrieved, the system returns a deterministic unknown response instead of asking the LLM to infer or invent an answer.

Why Backend Source Validation?

Source attribution should not depend entirely on generated text.

The backend stores document metadata alongside each chunk and resolves returned source identifiers against those stored records before displaying the Evidence Trail.

Limitations

The current implementation is intentionally scoped for the take-home assignment.

Known limitations include:

Scanned/image-only PDFs require OCR support, which is not currently included.
PDF extraction quality depends on document structure.
Complex tables may require specialized table extraction.
The current upload size limit is configured for lightweight document workflows.
ChromaDB runs locally rather than as a distributed production vector service.
The application depends on the configured Groq API for LLM generation.
Authentication and multi-user access control are not implemented.
The current application is not designed for distributed production deployment.
Retrieval thresholds may require tuning for different document collections.
Large-scale document evaluation and retrieval benchmarking are not included.
Future Improvements

With additional development time, the following improvements could be added:

OCR support for scanned PDFs.
DOCX, CSV and XLSX ingestion.
Cross-document comparison mode.
Improved table-aware retrieval.
BM25 + vector hybrid retrieval.
Dedicated cross-encoder reranking.
Streaming LLM responses.
Authentication and role-based access control.
Cloud-based vector storage for larger deployments.
Automated retrieval evaluation datasets and metrics.
Document versioning and change tracking.
Production observability and monitoring.
Security

The project follows several basic security practices:

API keys are stored in environment variables.
Real secrets are excluded from Git.
.env files are not committed.
Uploaded documents are processed locally for extraction and embeddings.
Only retrieved evidence is passed to the LLM rather than entire document contents.
Backend validation is applied to document and API inputs.
Source metadata is resolved by the backend instead of trusting generated citation text.
Development Time

The implementation was completed within the assignment's requested time constraint.

## Development Time

DocuPilot was developed within the assignment's specified 8-hour time constraint.

| Activity | Time |
| :--- | ---: |
| Problem understanding & architecture | Included within the 8-hour development window |
| Core development & RAG implementation | Included within the 8-hour development window |
| Retrieval tuning, testing & debugging | Included within the 8-hour development window |
| UI, documentation & final submission preparation | Included within the 8-hour development window |
| **Total** | **8 hours** |

DocuPilot implements the core requirements of the Smart Document Assistant assignment:

Requirement	Implementation
PDF upload	PyMuPDF-based parser
TXT upload	Native TXT parser
Text extraction	Document parser
Chunking	Section / paragraph / sentence-aware chunker
Embeddings	Local MiniLM embeddings
Searchable store	Persistent ChromaDB
Question answering	FastAPI + RAG + Groq
Grounded answers	Retrieved evidence only
Source attribution	Backend-verified source IDs
Unknown questions	Deterministic NOT_FOUND handling
Creative feature	Evidence Trail + suggestions + confidence
Multi-document reasoning	Document-scope retrieval
Architecture	docs/architecture.png
Testing	18 automated tests
Documentation	README + setup + design decisions
License

MIT License.

Developed as a GenAI take-home project focused on grounded document intelligence, retrieval-augmented generation, source attribution, and hallucination-aware question answering.


### Final checks before you commit

Only **one placeholder** remains intentionally:

```text
https://github.com/YOUR_GITHUB_USERNAME/docupilot.git

Replace that with your real repository URL.

Also keep:

GROQ_API_KEY=your_groq_api_key_here