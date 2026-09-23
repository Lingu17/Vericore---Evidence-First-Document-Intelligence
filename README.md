🚀 Vericore

<p align="center">
  <strong>Evidence-First Document Intelligence for Grounded Business Q&A, Retrieval, and Source Verification.</strong>
</p>

<p align="center">
  Upload business documents, ask questions in natural language, and inspect the exact evidence behind every grounded answer.
</p>

<p align="center">
  <a href="https://github.com/Lingu17/Vericore---Evidence-First-Document-Intelligence">💻 GitHub</a> •
  <a href="#-quick-start">⚡ Quick Start</a> •
  <a href="#-architecture">🏗 Architecture</a> •
  <a href="#-product-preview">📸 Product Preview</a>
</p>

<p align="center">










</p>

✨ Overview

Vericore is an evidence-first document intelligence workspace designed for business documents and knowledge workflows.

Instead of acting as an unconstrained chat interface, Vericore retrieves relevant information from uploaded documents before generating an answer.

Every grounded response can be inspected through the Evidence Trail, which exposes the source document, page, section, match information, stored excerpt, and chunk identifier used to support the response.

When the required information is not sufficiently supported by the uploaded documents, Vericore returns:

Information not available in the uploaded documents.

Built for:

HR & People Operations

Operations Teams

Finance Teams

Legal & Compliance

Knowledge Management

Document-heavy business workflows

📸 Product Preview

Landing Page



Document Workspace



Evidence Trail



Architecture



🎯 The Problem

Business information is often spread across lengthy documents such as:

Employee handbooks

Company policies

Benefits documents

Standard operating procedures

Internal agreements

Operational documentation

Business reports

Finding a specific answer manually can require searching through multiple pages and documents.

A generic AI assistant introduces another problem: it may produce a plausible answer even when the required information is not actually present.

Vericore is designed around a different workflow:

Upload
   ↓
Retrieve
   ↓
Verify
   ↓
Answer
   ↓
Inspect Evidence

The answer is only generated after relevant document evidence has been retrieved.

💡 What Vericore Does

Vericore turns uploaded PDF and TXT files into a searchable knowledge workspace.

Users can:

✅ Upload business documents

✅ Extract and index document content

✅ Ask natural-language questions

✅ Search across multiple documents

✅ Retrieve relevant evidence

✅ Generate concise grounded answers

✅ Inspect page-level source information

✅ Identify unsupported questions

✅ View evidence confidence signals

✅ Use suggested questions

✅ Ask contextual follow-up questions

🔥 Core Features

📄 Document Ingestion

PDF support

TXT support

Page-by-page PDF extraction

Text normalization

Section and heading detection

SHA-256 duplicate detection

Document-level deletion

🔎 Hybrid Retrieval

Vericore combines multiple retrieval signals:

Semantic Similarity
        +
Keyword Coverage
        +
Candidate Re-ranking

This helps retrieval handle both natural-language questions and precise business terminology such as:

Policy names

Dates

Numbers

Benefit terms

Department terminology

Procedural phrases

🧠 Grounded AI Answers

The LLM receives only selected retrieved evidence rather than the complete uploaded document.

This keeps the generation step focused on the information retrieved from the knowledge workspace.

Answers are intentionally concise and direct.

🛡️ Hallucination-Aware Unknown Handling

Vericore does not assume that every question has an answer.

When sufficient supporting evidence cannot be retrieved, the system returns:

Information not available in the uploaded documents.

This prevents the application from presenting unsupported information as a document-backed fact.

🔍 Evidence Trail

The Evidence Trail is the core product differentiator.

Users can inspect:

Source document

Page number

Section

Match information

Exact stored excerpt

Chunk identifier

The interface keeps the supporting evidence attached to the answer so users can verify where the information came from.

📊 Evidence Confidence

Vericore calculates evidence confidence from retrieval and grounding signals in the backend.

The confidence indicator is based on system retrieval signals rather than asking the LLM to invent a confidence probability.

📚 Multi-Document Workspace

Upload multiple documents and retrieve information across the indexed knowledge workspace.

Example:

Employee Handbook
        +
Leave Policy
        +
Remote Work FAQ
        ↓
     Question
        ↓
Relevant Evidence
        ↓
 Grounded Answer

💡 Suggested Questions

Vericore generates useful document questions from document structure and section headings.

This helps users discover relevant information without requiring an additional LLM call during ingestion.

💬 Lightweight Conversation Memory

The workspace supports contextual follow-up questions while limiting how much previous conversation is passed to the LLM.

This keeps follow-up questions useful while controlling unnecessary context.

♻️ SHA-256 Document Deduplication

Uploaded files are hashed before processing.

If an identical document has already been indexed, Vericore can avoid unnecessary re-processing and embedding work.

⚡ Answer Caching

Repeated questions with the same document scope and evidence can return cached results instead of triggering another generation request.

🏗 System Architecture

                         ┌─────────────────────┐
                         │        User         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ React + TypeScript  │
                         │      Frontend       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   FastAPI Backend   │
                         └──────────┬──────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  │                                   │
                  ▼                                   ▼
        ┌───────────────────┐              ┌───────────────────┐
        │ Document Pipeline │              │  Query Pipeline   │
        └─────────┬─────────┘              └─────────┬─────────┘
                  │                                  │
                  ▼                                  ▼
           PDF / TXT Parser                  Query Normalization
                  │                                  │
                  ▼                                  ▼
        Section-Aware Chunking                MiniLM Embedding
                  │                                  │
                  ▼                                  ▼
          Local Embeddings                     ChromaDB Search
                  │                                  │
                  └──────────────┐        ┌──────────┘
                                 ▼        ▼
                              ChromaDB
                                 │
                                 ▼
                         Hybrid Re-ranking
                         ┌───────┴────────┐
                         ▼                ▼
                  Semantic Match    Keyword Coverage
                         │                │
                         └───────┬────────┘
                                 ▼
                      Relevance / Grounding Gate
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
           Insufficient Evidence       Sufficient Evidence
                    │                         │
                    ▼                         ▼
          Deterministic Unknown       Evidence Selection
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
                                     Source ID Validation
                                              │
                                              ▼
                                  Verified Answer + Evidence
                                              │
                                              ▼
                                       Evidence Trail

🔄 Retrieval Pipeline

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
      ├── Semantic Similarity
      └── Keyword Coverage
      │
      ▼
Relevance / Grounding Gate
      │
      ├── Insufficient Evidence
      │        │
      │        ▼
      │   Information Not Found
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

🧩 Document Processing Pipeline

When a document is uploaded:

PDF / TXT
   │
   ▼
File Validation
   │
   ▼
SHA-256 Hash
   │
   ▼
Duplicate Check
   │
   ▼
Text Extraction
   │
   ▼
Text Normalization
   │
   ▼
Section Detection
   │
   ▼
Page / Paragraph / Sentence Chunking
   │
   ▼
Local MiniLM Embeddings
   │
   ▼
Persistent ChromaDB

Each indexed chunk retains source metadata such as:

document_id
filename
page
section
chunk_id
source_id
text

🧠 AI & Retrieval Design

Local Embeddings

Vericore uses:

sentence-transformers/all-MiniLM-L6-v2

The embedding model runs locally and produces a 384-dimensional representation.

This avoids requiring a separate external embedding API.

Vector Database

Vericore uses ChromaDB for persistent local vector storage.

Stored information includes:

Document embeddings

Chunk text

Document metadata

Page metadata

Section metadata

Source identifiers

LLM Generation

The current generation layer uses:

Provider: Groq
Model: openai/gpt-oss-20b

The LLM receives only the selected evidence needed for the question.

🛡️ Hallucination Prevention

Vericore uses multiple safeguards.

1. Retrieval Before Generation

The system retrieves evidence before asking the LLM to generate an answer.

2. Limited Context

The complete uploaded document is not sent to the LLM.

Only selected evidence chunks are included.

3. Hybrid Retrieval

Semantic similarity is combined with keyword coverage.

4. Relevance Gate

If evidence is not sufficiently relevant, the generation step can be skipped.

5. Grounded Prompt

The model is instructed to answer using only the supplied evidence.

6. Backend Source Validation

The backend resolves internal source identifiers against stored metadata before displaying source information.

This prevents generated text from independently fabricating:

File names

Page numbers

Section names

Evidence references

⚡ Token & API Optimization

Vericore is designed to reduce unnecessary generation work.

Local embeddings

Embedding generation runs locally.

Retrieval before generation

Only relevant chunks are passed to the LLM.

Relevance gating

Unsupported questions can be rejected before LLM generation.

Adaptive evidence selection

The system can select a smaller or larger evidence set based on retrieval relevance.

Duplicate evidence removal

Near-duplicate chunks are filtered before context assembly.

Trimmed prompts

The generation payload contains only the question and required evidence.

Limited conversation history

Only limited recent context is retained for follow-up questions.

Short structured output

MAX_OUTPUT_TOKENS = 250
TEMPERATURE = 0

Deterministic suggestions

Suggested questions are generated from document structure without an LLM call during ingestion.

Answer caching

Identical evidence-backed questions can use cached responses.

🎨 Workspace Design

The application uses a desktop-first B2B workspace with three functional areas:

┌─────────────────────────────────────────────────────────────┐
│                         Vericore                            │
├───────────────┬───────────────────────────┬─────────────────┤
│               │                           │                 │
│   Documents   │       Q&A Workspace       │ Evidence Trail │
│               │                           │                 │
│  Upload       │  Question                │  Source         │
│  Indexed docs │  Answer                  │  Page           │
│  Document     │  Confidence              │  Section        │
│  management   │  Sources                 │  Excerpt        │
│               │                           │  Chunk ID       │
│               │                           │                 │
└───────────────┴───────────────────────────┴─────────────────┘

The interface is designed around a simple interaction:

Ask → Answer → Inspect

🛠 Tech Stack

Frontend

React 18

TypeScript

Vite

Tailwind CSS

Lucide React

Backend

Python 3.10+

FastAPI

Uvicorn

Pydantic v2

PyMuPDF

AI / Retrieval

sentence-transformers

all-MiniLM-L6-v2

ChromaDB

Groq API

openai/gpt-oss-20b

Testing

Pytest

HTTPX

📂 Project Structure

vericore/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │   │   └── health.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── logging.py
│   │   │
│   │   ├── models/
│   │   │   └── schemas.py
│   │   │
│   │   ├── prompts/
│   │   │   └── qa_prompt.py
│   │   │
│   │   ├── services/
│   │   │   ├── chunker.py
│   │   │   ├── confidence.py
│   │   │   ├── document_parser.py
│   │   │   ├── embeddings.py
│   │   │   ├── llm.py
│   │   │   ├── retriever.py
│   │   │   ├── suggestions.py
│   │   │   └── vector_store.py
│   │   │
│   │   ├── utils/
│   │   │   ├── hashing.py
│   │   │   └── text.py
│   │   │
│   │   └── main.py
│   │
│   ├── sample_documents/
│   │   ├── generate_samples.py
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
│   │   │   ├── chat/
│   │   │   ├── common/
│   │   │   ├── documents/
│   │   │   ├── evidence/
│   │   │   └── layout/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── services/
│   │   ├── types/
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── main.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── docs/
│   ├── architecture.png
│   └── screenshots/
│       ├── home.png
│       ├── workspace.png
│       └── evidence-trail.png
│
├── .env.example
└── README.md

⚙️ Environment Variables

Backend

# Groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
USE_MOCK_LLM=false

# Generation
MAX_OUTPUT_TOKENS=250
TEMPERATURE=0
MAX_HISTORY_MESSAGES=2

# Vector database
CHROMA_PATH=./chroma_db

# Local embeddings
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

# Upload
MAX_FILE_SIZE_MB=10

# Server
ENV=development
PORT=8000
HOST=0.0.0.0

Never commit .env files or real API keys to Git.

🚀 Quick Start

Clone Repository

git clone https://github.com/Lingu17/Vericore---Evidence-First-Document-Intelligence.git

cd Vericore---Evidence-First-Document-Intelligence

Backend Setup

cd backend

Windows PowerShell

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Linux / macOS

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Create the environment file:

cp .env.example .env

Add your Groq API key to .env.

Frontend Setup

Open a second terminal:

cd frontend

npm install

npm run dev

Frontend:

http://localhost:5173

Start Backend

cd backend

uvicorn app.main:app --reload --port 8000

Backend:

http://localhost:8000

API documentation:

http://localhost:8000/docs

🔌 API Endpoints

Method

Endpoint

Description

GET

/health

Application health and system information

GET

/api/documents

List indexed documents

POST

/api/documents/upload

Upload and index PDF/TXT documents

GET

/api/documents/{document_id}

Fetch document metadata

GET

/api/documents/{document_id}/suggestions

Get suggested questions

DELETE

/api/documents/{document_id}

Delete a document and its vectors

DELETE

/api/documents

Clear indexed documents

POST

/api/chat

Submit a grounded document question

🧪 Testing

Run the backend test suite:

python -m pytest backend/tests -v

Current result:

18 passed

Coverage includes:

Health check

Document upload

Duplicate document detection

Grounded question answering

Unknown-question handling

Empty question validation

Chunk metadata preservation

Section detection

PDF page preservation

TXT parsing

Empty file rejection

Unsupported file extension rejection

Corrupt PDF handling

High-confidence retrieval

Medium-confidence retrieval

Low-confidence retrieval

Grounding-aware confidence

Hybrid retrieval / relevance behavior

🎬 Demo Questions

The following questions can be used with the sample employee handbook:

What are the normal working hours?

How many days per week can employees work remotely?

When does an employee receive their first performance review?

How many hours per week must an employee work to be considered full-time?

What should an employee do if they expect to arrive late?

🚫 Hallucination Test

Ask:

What is the company's annual performance bonus?

Expected:

Information not available in the uploaded documents.

The system should not invent a bonus amount or generate unsupported information.

📊 Evidence Confidence

Evidence confidence is calculated by the backend from retrieval and grounding signals.

It is not an LLM-generated probability.

The UI can distinguish between:

High
Medium
Low

based on the available retrieval evidence.

🔐 Security

The project follows several basic security practices:

API keys are stored in environment variables.

.env files are excluded from Git.

Real secrets are not included in the repository.

Uploaded documents are processed locally for extraction and embeddings.

Only retrieved evidence is passed to the LLM rather than complete documents.

Backend validation is applied to document and API inputs.

Source metadata is resolved by the backend rather than trusting generated citation text.

⚠️ Limitations

The current implementation is intentionally scoped for a focused RAG application.

Known limitations:

Scanned/image-only PDFs require OCR support.

PDF extraction quality depends on document structure.

Complex tables may require specialized extraction.

Upload size is configured for lightweight document workflows.

ChromaDB runs locally rather than as a distributed production vector service.

LLM generation depends on the configured Groq API.

Authentication and multi-user access control are not implemented.

The application is not currently designed for distributed production deployment.

Retrieval thresholds may require tuning for different document collections.

Large-scale retrieval benchmarking is not included.

🗺️ Roadmap

Current

PDF & TXT ingestion

Document extraction

Local embeddings

Persistent ChromaDB

Hybrid retrieval

Grounded Q&A

Evidence Trail

Unknown handling

Multi-document retrieval

Suggested questions

Conversation memory

Answer caching

Evidence confidence

Future

OCR for scanned PDFs

DOCX / CSV / XLSX ingestion

Cross-document comparison

Table-aware retrieval

BM25 + vector retrieval

Cross-encoder reranking

Streaming responses

Authentication

Role-based access control

Cloud vector infrastructure

Document versioning

Retrieval evaluation datasets

Production observability

🤖 AI-Assisted Development

AI-assisted development tools were used during implementation for:

Exploring RAG implementation approaches

Debugging retrieval behavior

Investigating edge cases

Reviewing code structure

Generating test ideas

Refining prompts

Improving answer behavior

Refining project documentation

AI-generated suggestions were reviewed, tested, debugged, and adapted before being included in the final implementation.

⏱️ Development Time

Vericore was developed within the assignment's specified 8-hour development constraint.

The development window covered:

Problem understanding

Architecture design

Frontend implementation

Backend implementation

Document ingestion

RAG pipeline

Retrieval refinement

Hallucination handling

Evidence Trail

Testing and debugging

UI refinement

Documentation

Final verification

Total development window: 8 hours

📋 Assignment Alignment

Assignment Requirement

Vericore Implementation

PDF upload

PyMuPDF parser

TXT upload

Native TXT parser

Text extraction

Document parser

Chunking

Section / paragraph / sentence-aware chunking

Embeddings

Local MiniLM embeddings

Searchable store

Persistent ChromaDB

Question answering

FastAPI + RAG + Groq

Grounded answers

Retrieved evidence only

Source attribution

Backend-verified source IDs

Unknown questions

Deterministic NOT_FOUND handling

Creative feature

Evidence Trail + suggestions + confidence

Multi-document reasoning

Document-scope retrieval

Conversation memory

Limited contextual follow-up

Architecture

docs/architecture.png

Testing

18 automated tests

Documentation

README + setup + design decisions

🤝 Contributing

Contributions are welcome.

1. Fork the repository

git fork https://github.com/Lingu17/Vericore---Evidence-First-Document-Intelligence.git

2. Create a feature branch

git checkout -b feature/new-feature

3. Commit changes

git commit -m "Add new feature"

4. Push your branch

git push origin feature/new-feature

5. Open a Pull Request

👨‍💻 Author

Lingraj Malipatil

GitHub:

https://github.com/Lingu17

LinkedIn:

https://linkedin.com/in/lingraj-malipatil

⭐ Support

If Vericore is useful:

⭐ Star the repository

🐛 Report an issue

💡 Suggest an improvement

🤝 Contribute to the project

<p align="center">
  Built with React, FastAPI, ChromaDB, local embeddings, and grounded LLM retrieval.
</p>

<p align="center">
  <strong>Vericore — Retrieve. Answer. Verify.</strong>
