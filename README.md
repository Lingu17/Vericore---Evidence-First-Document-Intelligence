# DocuPilot

> **"Ask your documents. Verify every answer."**  
> *Evidence-First Document Intelligence for Enterprise Teams.*

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat-square)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_18_%2B_Vite-61DAFB.svg?style=flat-square)](https://react.dev/)
[![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB_Local-FF6F00.svg?style=flat-square)](https://www.trychroma.com/)
[![Sentence-Transformers](https://img.shields.io/badge/Embeddings-MiniLM--L6--v2_(Local_%E2%82%B90)-blue.svg?style=flat-square)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![Groq](https://img.shields.io/badge/LLM-Groq_API-F55036.svg?style=flat-square)](https://groq.com/)
[![Tests](https://img.shields.io/badge/Tests-15_Passed-16A34A.svg?style=flat-square)]()

---

## Overview

**DocuPilot** is an enterprise-grade, evidence-first document intelligence workspace. Rather than functioning as an unconstrained chat wrapper, DocuPilot is purpose-built to answer business questions strictly from verified document context. Every answer is coupled with a transparent, clickable **Evidence Trail** showing the exact source file, 1-indexed page number, section title, and verbatim text passage.

When supporting information does not exist in the uploaded documents, DocuPilot deterministically responds with a distinct **"Information Not Found"** notification—never confabulating or hallucinating facts.

![DocuPilot Architecture](docs/architecture.png)

---

## Problem

Enterprise knowledge workers lose countless hours searching through lengthy PDF policies, employee handbooks, SOPs, and legal agreements. Traditional AI document chatbots suffer from critical enterprise flaws:
1. **Hallucinations & Confabulation:** Generic LLMs extrapolate or invent plausible-sounding details when answers are missing.
2. **Untraceable Answers:** Answers lack granular citations, forcing staff to manually cross-reference entire multi-page documents.
3. **Runaway Cloud Costs:** Uploading full documents to paid embedding and LLM APIs incurs high per-token and recurring vector database costs.
4. **Cluttered Toy Interfaces:** Many RAG tools look like prototype ChatGPT clones rather than high-density B2B productivity software.

---

## Solution

DocuPilot provides an **Evidence-First RAG Architecture**:
- **100% Local Embeddings (`all-MiniLM-L6-v2`) & ChromaDB:** Vector embeddings and indexing run on-premise at **₹0 cost**.
- **Deterministic Relevance Gating:** Low-relevance questions are rejected before reaching the LLM, eliminating hallucinations and conserving Groq API tokens.
- **Tamper-Proof Attribution:** The LLM receives and returns `[SOURCE_ID=...]` tokens. The backend resolves these tokens to verified, immutable chunk metadata so page numbers and citations can never be fabricated.
- **B2B SaaS Workspace:** A desktop-first 3-column layout (Document Manager, Grounded Chat Timeline, and Inspectable Evidence Drawer).

---

## Key Features

- **Document Ingestion (PDF & TXT):** Page-by-page text extraction with layout and heading detection via PyMuPDF (`fitz`).
- **SHA-256 Deduplication:** Duplicate document uploads are detected instantly by content hash, preventing redundant embedding compute.
- **Intelligent Page-Aware Chunking:** Text is split along natural paragraph and section boundaries while preserving `document_id`, `filename`, `page`, `section`, and `chunk_id`.
- **Zero-Cost Local Embeddings:** Fast local embeddings via `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional vector space).
- **Persistent ChromaDB Vector Store:** Persistent vector storage with cosine similarity metrics and instant document-level purge.
- **Adaptive Context Sizing:** Dynamically selects 1–3 chunks based on semantic retrieval relevance.
- **Answer Caching:** In-memory hash cache eliminates duplicate LLM calls for repeated identical questions.
- **Evidence Confidence Badging:** Deterministic categorization (**High**, **Medium**, **Low**) based on semantic distance—never fake probability percentages.
- **Smart Suggested Questions:** Extracts high-signal business questions from document section headers on ingestion with zero LLM overhead.
- **Evidence Trail Side Drawer:** Click any source badge to inspect the verbatim snippet, page number, and section in a dedicated audit panel.
- **Information Not Found Cards:** Clear, non-error visual states for unsupported queries with suggested alternatives.
- **Multi-Document Reasoning:** Seamlessly synthesizes evidence across multiple uploaded business policies in a single query.

---

## Architecture

```
User Query
    │
    ▼
[Deterministic Query Normalization] (Lowercase, strip punctuation)
    │
    ▼
[SentenceTransformer: all-MiniLM-L6-v2] ──► Local Query Embedding (₹0 Cost)
    │
    ▼
[ChromaDB Local Vector DB] ──► Top-5 Vector Cosine Search (with Doc Scope Filter)
    │
    ▼
[Deduplication & Overlap Filter] ──► Drops near-duplicate chunks (>75% overlap)
    │
    ▼
[Relevance Gate (Threshold = 0.48)]
    ├── Similarity < 0.48 ──► Deterministic NOT_FOUND (0 Groq calls, 0 tokens)
    └── Similarity ≥ 0.48 ──► Adaptive Evidence Selection:
                                 ├── Score ≥ 0.62 ──► 1 Chunk (Ultra-compact)
                                 ├── Score ≥ 0.54 ──► 2 Chunks
                                 └── Score ≥ 0.48 ──► Max 3 Chunks
                                       │
                                       ▼
                     [Answer Cache Check] (hash(q + scope + source_ids))
                     ├── Cache HIT  ──► Return cached result (0 tokens)
                     └── Cache MISS ──► Grounded Prompt Construction
                                           │
                                           ▼
                     [LLMProvider: Groq (Llama 3.3 / GPT-OSS)]
                     (temp=0, max_tokens=250, direct JSON schema)
                                           │
                                           ▼
                     [Token Usage Logger (prompt / completion / total)]
                                           │
                                           ▼
                     [Local Source ID Validator & Citation Resolver]
                                           │
                                           ▼
                     [Verified Grounded Answer + Evidence Trail]
```

---

## Token Optimization

DocuPilot is engineered for **Maximum Quality with Minimum LLM Tokens**:

1. **Local Embeddings (₹0 Cost):** Uses `all-MiniLM-L6-v2` locally on CPU/GPU. Zero tokens sent to external embedding APIs.
2. **Retrieval Before Generation:** Only 1–3 top-scoring, deduplicated chunks are ever sent to Groq. Entire documents or raw PDF bodies are **NEVER** sent to the LLM.
3. **Strict Similarity Gating:** Queries with similarity below `0.48` are rejected before reaching Groq, guaranteeing 0 tokens wasted on out-of-scope questions.
4. **Adaptive Evidence Selection:** Very high relevance (`≥ 0.62`) sends **1 chunk**, strong relevance (`≥ 0.54`) sends **2 chunks**, and moderate relevance sends at most **3 chunks**.
5. **Duplicate Evidence Removal:** Near-duplicate chunks with `> 75%` text overlap are filtered out before context assembly.
6. **Trimmed Context Payloads:** Only `SOURCE_ID`, `filename`, `page`, `section`, and the extracted passage are passed—internal DB metadata, timestamps, and hashes are omitted.
7. **Minimal System Prompt:** Short, instruction-dense prompt (~45 words) enforcing factual grounding and valid JSON.
8. **Minimal User Prompt:** Clean `QUESTION:` and `EVIDENCE:` blocks without redundant instruction preamble.
9. **Pruned Conversation History:** Standalone questions pass **0 previous turns**; follow-up questions retain only the last 1–2 turns (`MAX_HISTORY_MESSAGES = 2`).
10. **Short Structured Output:** Generation is capped at `MAX_OUTPUT_TOKENS = 250` with `TEMPERATURE = 0`. No verbose reasoning, chain-of-thought, or fluff.
11. **Backend Confidence Calculation:** Evidence Confidence (**High / Medium / Low**) is computed purely via mathematical distance in Python—never prompting the LLM for self-rated confidence.
12. **Zero-Token Suggested Questions:** Derived deterministically from section headings and regex patterns during document parsing—no LLM calls on ingestion.
13. **SHA-256 Ingestion Caching:** Duplicate document uploads are identified via file hash and skipped immediately without re-embedding.
14. **Identical Query Caching:** In-memory answer caching keyed by `hash(normalized_query + scope + source_ids)` returns instant responses for repeated identical questions with 0 Groq calls.

---

## Technology Stack

### Backend
- **Language:** Python 3.10+ / Python 3.14
- **Framework:** FastAPI, Uvicorn, Pydantic v2, Pydantic-Settings
- **Document Processing:** PyMuPDF (`pymupdf`) for PDF, native decoders for TXT
- **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Vector Database:** `chromadb` (Persistent on-disk)
- **LLM Provider:** `groq` (Llama-3.3 / GPT-OSS) with abstract provider architecture
- **Testing:** `pytest`, `httpx`

### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS (Custom enterprise color tokens & keyframe animations)
- **Icons:** Lucide React

---

## Project Structure

```
DOCUPILOT/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py             # Grounded chat & RAG endpoints
│   │   │   ├── documents.py        # Upload, list, delete, suggestions
│   │   │   └── health.py           # Diagnostic & system health endpoint
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic Settings & environment config
│   │   │   └── logging.py          # Structured logger
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic request & response models
│   │   ├── prompts/
│   │   │   └── qa_prompt.py        # Strict grounded QA prompt & builder
│   │   ├── services/
│   │   │   ├── chunker.py          # Section-aware semantic chunker
│   │   │   ├── confidence.py       # Evidence confidence calculator
│   │   │   ├── document_parser.py  # PyMuPDF & TXT extraction
│   │   │   ├── embeddings.py       # Local MiniLM SentenceTransformer singleton
│   │   │   ├── llm.py              # LLMProvider interface & GroqProvider
│   │   │   ├── retriever.py        # Vector search & similarity thresholding
│   │   │   ├── suggestions.py      # Zero-token suggested questions generator
│   │   │   └── vector_store.py     # Persistent ChromaDB client & metadata registry
│   │   ├── utils/
│   │   │   ├── hashing.py          # SHA-256 deduplication
│   │   │   └── text.py             # Unicode cleaner & heading detector
│   │   └── main.py                 # FastAPI application & lifespan
│   ├── sample_documents/           # Realistic fictional NovaTech test documents
│   │   ├── generate_samples.py     # PDF & TXT generator script
│   │   ├── NovaTech_Benefits_Policy.pdf
│   │   ├── NovaTech_Employee_Handbook.pdf
│   │   ├── NovaTech_Leave_Policy.pdf
│   │   └── NovaTech_Remote_Work_FAQ.txt
│   ├── tests/                      # Pytest test suite (15 unit & integration tests)
│   │   ├── test_api.py
│   │   ├── test_chunker.py
│   │   ├── test_parser.py
│   │   └── test_retriever_confidence.py
│   ├── requirements.txt            # Minimal Python dependencies
│   └── .env.example                # Backend environment template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/               # ChatArea, MessageCard, QueryInput, UnknownQuestionCard
│   │   │   ├── common/             # Badge, Button, ConfidenceBadge, Skeleton, Toast
│   │   │   ├── documents/          # DocumentList, DocumentRow, DocumentUpload
│   │   │   ├── evidence/           # EvidenceCard, EvidenceDrawer, EvidencePanel
│   │   │   └── layout/             # Header, Sidebar, MainWorkspace
│   │   ├── hooks/                  # useChat, useDocuments custom hooks
│   │   ├── lib/                    # utils & className merger
│   │   ├── services/               # api.ts fetch client
│   │   ├── types/                  # TypeScript domain interfaces
│   │   ├── App.tsx                 # Root application component
│   │   ├── index.css               # Tailwind design tokens & typography
│   │   └── main.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
├── docs/
│   └── architecture.png            # High-resolution system architecture diagram
├── .env.example                    # Root environment template
└── README.md
```

---

## Installation

### Prerequisites
- Python 3.10+ (tested through Python 3.14)
- Node.js v18+ & npm
- Git

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/docupilot.git
cd DOCUPILOT
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

---

## Environment Variables

Configure `backend/.env`:

```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
USE_MOCK_LLM=false

# Token-Saving Limits & Generation
MAX_OUTPUT_TOKENS=250
TEMPERATURE=0
MAX_HISTORY_MESSAGES=2

# Vector Database (Local ChromaDB)
CHROMA_PATH=./chroma_db

# Local Embedding Model (Runs 100% locally at ₹0 cost)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Adaptive Retrieval & Relevance Gating
TOP_K=5
FINAL_CONTEXT_CHUNKS=3
SIMILARITY_THRESHOLD=0.48
STRONG_RELEVANCE_THRESHOLD=0.54
HIGH_RELEVANCE_THRESHOLD=0.62

# Ingestion & Chunking (Character-based)
CHUNK_SIZE=1200
CHUNK_OVERLAP=150

# Upload Limits
MAX_FILE_SIZE_MB=10

# Server
ENV=development
PORT=8000
HOST=0.0.0.0
```

---

## Running Locally

### Terminal 1: Start Backend Server
```bash
cd backend
# Make sure .venv is activated
uvicorn app.main:app --reload --port 8000
```
Backend will be available at: `http://localhost:8000` (API Docs: `http://localhost:8000/docs`)

### Terminal 2: Start Frontend Application
```bash
cd frontend
npm run dev
```
Frontend workspace will open at: `http://localhost:5173`

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Application health, loaded models & vector store count |
| `GET` | `/api/documents` | List all indexed documents with page and chunk metadata |
| `POST` | `/api/documents/upload` | Upload & index PDF/TXT document with SHA-256 deduplication |
| `GET` | `/api/documents/{document_id}` | Fetch metadata for a specific document |
| `GET` | `/api/documents/{document_id}/suggestions` | Get smart suggested questions for a document |
| `DELETE` | `/api/documents/{document_id}` | Delete document and purge vector embeddings from ChromaDB |
| `DELETE` | `/api/documents` | Clear all documents from knowledge base |
| `POST` | `/api/chat` | Submit question for Evidence-First RAG answering |

---

## Testing

### Run tests:
```bash
python -m pytest backend/tests -v
```

### Test Suite Summary:
```
backend/tests/test_api.py::test_health_check_endpoint PASSED             [  6%]
backend/tests/test_api.py::test_document_upload_and_deduplication PASSED [ 13%]
backend/tests/test_api.py::test_grounded_question_answering PASSED       [ 20%]
backend/tests/test_api.py::test_unknown_question_anti_hallucination PASSED [ 26%]
backend/tests/test_api.py::test_empty_question_rejected PASSED           [ 33%]
backend/tests/test_chunker.py::test_chunking_metadata_preservation PASSED [ 40%]
backend/tests/test_chunker.py::test_chunker_section_detection PASSED     [ 46%]
backend/tests/test_parser.py::test_pdf_parsing_preserves_pages_and_sections PASSED [ 53%]
backend/tests/test_parser.py::test_txt_parsing PASSED                    [ 60%]
backend/tests/test_parser.py::test_empty_file_rejected PASSED            [ 66%]
backend/tests/test_parser.py::test_unsupported_file_extension_rejected PASSED [ 73%]
backend/tests/test_parser.py::test_corrupt_pdf_rejected PASSED           [ 80%]
backend/tests/test_retriever_confidence.py::test_confidence_high_with_strong_similarity PASSED [ 86%]
backend/tests/test_retriever_confidence.py::test_confidence_medium_with_moderate_similarity PASSED [ 93%]
backend/tests/test_retriever_confidence.py::test_confidence_low_when_below_threshold_or_empty PASSED [100%]

======================= 15 passed, 1 warning in 13.03s ========================
```

---

## License

MIT License. Developed for enterprise document intelligence.
