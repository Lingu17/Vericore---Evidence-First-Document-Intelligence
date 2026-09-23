Vericore

Evidence-First Document Intelligence

<p align="center">
  <strong>Upload documents. Ask questions. Verify every answer against the source.</strong>
</p>

<p align="center">
  A focused RAG workspace for grounded document Q&A, source attribution, and evidence inspection.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-2563EB?style=for-the-badge" alt="React + TypeScript">
  <img src="https://img.shields.io/badge/Backend-FastAPI-059669?style=for-the-badge" alt="FastAPI">
  <img src="https://img.shields.io/badge/RAG-Hybrid%20Retrieval-7C3AED?style=for-the-badge" alt="Hybrid RAG">
  <img src="https://img.shields.io/badge/Tests-18%20Passed-16A34A?style=for-the-badge" alt="18 tests passed">
</p>

Product Preview

Home / Landing



Document Workspace



Evidence Trail



Repository assets: save the three UI screenshots above inside docs/screenshots/ using the exact filenames shown.

The architecture image is included below and should remain at docs/architecture.png.

What is Vericore?

Vericore is an evidence-first document intelligence workspace for business documents and knowledge workflows.

Instead of behaving like an unconstrained chat wrapper, Vericore answers questions from retrieved and verified document context. Every grounded answer can be inspected through an Evidence Trail showing the source file, page, section, match information, and stored evidence passage used for the response.

When the required information is not sufficiently supported by the uploaded documents, Vericore returns:

Information not available in the uploaded documents.

The goal is simple:

Retrieve → Answer → Verify

Why Vericore?

Business information is often distributed across:

Employee handbooks

Company policies

SOPs

Benefits documents

Internal agreements

Operational documentation

Reports and knowledge bases

Searching these documents manually can be slow. A conventional AI assistant can make search easier, but an answer without inspectable evidence can be difficult to review.

Vericore puts the retrieval and evidence layer first.

The core idea

Document
   ↓
Extract
   ↓
Chunk
   ↓
Embed
   ↓
Retrieve
   ↓
Verify
   ↓
Generate
   ↓
Inspect Evidence

Key Features

Feature

Description

📄 PDF & TXT ingestion

Extracts and indexes business documents

🔎 Semantic search

Finds conceptually relevant document passages

⚡ Hybrid retrieval

Combines semantic similarity with keyword coverage

🧠 RAG

Generates answers from retrieved evidence

🛡️ Grounding gate

Rejects insufficient evidence before generation

📌 Source attribution

Preserves document, page, section, and chunk metadata

🔍 Evidence Trail

Inspect the exact stored passage behind an answer

🚫 Unknown handling

Clearly states when information is unavailable

📚 Multi-document retrieval

Searches across multiple indexed documents

💬 Conversation memory

Supports limited contextual follow-up questions

💡 Suggested questions

Generates useful questions from document structure

♻️ SHA-256 deduplication

Avoids reprocessing identical documents

🚀 Answer caching

Avoids repeated generation for identical evidence-backed queries

📊 Evidence confidence

Shows retrieval-based confidence signals

🖥️ B2B workspace

Desktop-first document + chat + evidence interface

Product Workflow

┌───────────────┐
│  01  UPLOAD   │
│ PDF / TXT     │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  02  INDEX    │
│ Extract       │
│ Chunk         │
│ Embed         │
│ Store         │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  03  ASK      │
│ Natural       │
│ language      │
│ question      │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  04  RETRIEVE │
│ Semantic +    │
│ keyword       │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  05  VERIFY   │
│ Relevance +   │
│ grounding     │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  06  ANSWER   │
│ Grounded LLM  │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  07  INSPECT  │
│ Evidence      │
│ Trail         │
└───────────────┘

Architecture



Vericore follows an Evidence-First RAG Architecture:

                           ┌──────────────────────┐
                           │        User          │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │ React + TypeScript   │
                           │       Frontend       │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │    FastAPI Backend   │
                           └──────────┬───────────┘
                                      │
                  ┌───────────────────┴───────────────────┐
                  │                                       │
                  ▼                                       ▼
       ┌─────────────────────┐                 ┌─────────────────────┐
       │ Document Ingestion  │                 │   Query Pipeline    │
       └──────────┬──────────┘                 └──────────┬──────────┘
                  │                                       │
        ┌─────────┴─────────┐                             ▼
        │                   │                   Query Normalization
        ▼                   ▼                             │
     PDF/TXT             Extraction                         ▼
        │                   │                    Local Query Embedding
        └─────────┬─────────┘                             │
                  ▼                                       ▼
        Section-Aware Chunking                    ChromaDB Search
                  │                                       │
                  ▼                                       ▼
        Local MiniLM Embeddings                    Candidate Pool
                  │                                       │
                  └───────────────┐               ┌───────┘
                                  ▼               ▼
                              ChromaDB     Hybrid Re-ranking
                                               │
                               ┌───────────────┴───────────────┐
                               │                               │
                               ▼                               ▼
                     Semantic Similarity                 Keyword Coverage
                               │                               │
                               └───────────────┬───────────────┘
                                               ▼
                                   Relevance / Grounding Gate
                                               │
                              ┌────────────────┴────────────────┐
                              │                                 │
                              ▼                                 ▼
                    Insufficient Evidence              Sufficient Evidence
                              │                                 │
                              ▼                                 ▼
                    Deterministic Unknown             Evidence Selection
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
                                                        Evidence Trail UI

Retrieval Pipeline

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

Vericore uses multiple layers to reduce unsupported answers.

1. Retrieval Before Generation

The LLM does not receive complete uploaded documents.

Only selected retrieved evidence chunks are passed to the generation step.

2. Hybrid Retrieval

Retrieval combines:

Semantic similarity

Keyword coverage

Candidate reranking

This helps with questions containing important policy terms, dates, numbers, and specific terminology.

3. Relevance / Grounding Gate

If retrieved evidence is not sufficiently relevant, Vericore returns the deterministic unknown response instead of asking the LLM to guess.

Information not available in the uploaded documents.

4. Grounded Prompting

The LLM is instructed to answer using only the supplied evidence.

5. Backend Source Validation

Retrieved chunks contain internal source identifiers.

The LLM can return those identifiers, but the backend resolves them against stored document metadata before the Evidence Trail is rendered.

This prevents generated responses from independently fabricating:

File names

Page numbers

Section names

Evidence references

6. Concise Answers

Answers are intentionally short and direct so the response stays focused on the retrieved evidence.

Evidence Trail

The Evidence Trail is the main product differentiator.

For a grounded answer, the user can inspect:

Source document

Page number

Section

Match information

Exact stored excerpt

Chunk identifier

Example:

┌──────────────────────────────────────┐
│ EVIDENCE TRAIL                       │
├──────────────────────────────────────┤
│ Source                                │
│ Employee Handbook.pdf                 │
│                                      │
│ Page                                  │
│ 14                                   │
│                                      │
│ Section                               │
│ Performance Reviews                   │
│                                      │
│ Match                                 │
│ Semantic + keyword evidence           │
│                                      │
│ Stored excerpt                        │
│ "You will have your first performance │
│ review at the end of your first..."   │
└──────────────────────────────────────┘

The evidence displayed in the UI comes from stored document metadata and retrieved content rather than being invented by the interface.

Document Processing

Vericore supports:

PDF

TXT

For PDFs, text is extracted page by page using PyMuPDF.

During ingestion:

Validate the uploaded file.

Compute a SHA-256 content hash.

Detect duplicate documents.

Extract text.

Normalize text.

Detect headings and sections.

Split text into searchable chunks.

Preserve page and document metadata.

Generate local embeddings.

Store vectors and metadata in ChromaDB.

Each chunk preserves metadata such as:

document_id
filename
page
section
chunk_id
source_id
text

Intelligent Chunking

Vericore uses section-aware chunking rather than treating a document as one large block.

The chunking strategy considers:

Sections

Paragraphs

Sentences

Chunk size

Chunk overlap

This helps preserve useful policy context while keeping retrieval units manageable.

Local Embeddings

Vericore uses:

sentence-transformers/all-MiniLM-L6-v2

Embeddings run locally.

Benefits

No separate embedding API is required.

Reduced external embedding dependencies.

Simple local retrieval pipeline.

384-dimensional vector representation.

Vector Storage

Vericore uses persistent ChromaDB for local vector storage.

The vector store contains:

Embeddings

Chunk text

Document metadata

Page metadata

Section metadata

Source identifiers

It supports similarity search and document-level deletion.

Hybrid Retrieval

Pure semantic similarity can sometimes miss exact terminology.

Business documents frequently contain:

Policy names

Dates

Numbers

Specific benefit names

Department terminology

Exact procedural phrases

Vericore therefore combines:

Semantic Similarity
        +
Keyword Coverage
        +
Candidate Re-ranking

This gives the retrieval layer both semantic and lexical signals.

Token & LLM Usage Optimization

Vericore is designed to minimize unnecessary LLM usage.

Local embeddings

all-MiniLM-L6-v2 runs locally.

Retrieval before generation

Only selected evidence chunks are sent to the LLM.

Relevance gating

Questions with insufficient evidence can be rejected before LLM generation.

Adaptive evidence selection

Highly relevant questions can use fewer chunks while less direct questions can use additional supporting evidence.

Duplicate evidence removal

Near-duplicate chunks are filtered before context assembly.

Trimmed context payloads

Only required source metadata and extracted evidence are passed to the LLM.

Minimal prompts

The prompt uses concise QUESTION: and EVIDENCE: blocks.

Limited conversation history

Standalone questions do not require previous turns. Follow-up questions retain only limited recent context.

Short structured output

Current configuration:

MAX_OUTPUT_TOKENS=250
TEMPERATURE=0

Deterministic suggestions

Suggested questions are generated from document structure without an LLM call during ingestion.

SHA-256 deduplication

Duplicate files are detected before unnecessary re-embedding.

Answer caching

Repeated identical questions with the same evidence scope can return cached results.

Multi-Document Reasoning

Vericore can retrieve relevant evidence across multiple uploaded documents.

This enables workflows such as:

Employee Handbook
       +
Leave Policy
       +
Remote Work FAQ
       ↓
   Single Question
       ↓
Relevant Evidence
       ↓
Grounded Answer

Document scope is maintained by the retrieval layer so answers can be associated with the actual indexed sources.

Suggested Questions

Vericore can generate useful suggested questions from document structure and section headings.

The suggestions are designed to help users discover what a document can answer without requiring an LLM call during ingestion.

Conversation Memory

The application supports lightweight contextual follow-up questions while limiting how much previous conversation is passed to the LLM.

This keeps follow-up interactions useful without unnecessarily increasing the generation context.

Technology Stack

Frontend

Technology

Purpose

React 18

User interface

TypeScript

Type-safe frontend

Vite

Development and production build

Tailwind CSS

Styling

Lucide React

UI icons

Backend

Technology

Purpose

Python 3.10+

Backend language

FastAPI

API layer

Uvicorn

ASGI server

Pydantic v2

Validation

PyMuPDF

PDF extraction

sentence-transformers

Local embeddings

ChromaDB

Persistent vector storage

Pytest

Automated testing

HTTPX

API testing

AI / Retrieval

Component

Technology

Embedding model

all-MiniLM-L6-v2

Vector store

ChromaDB

Retrieval

Semantic + keyword hybrid retrieval

LLM provider

Groq

LLM model

openai/gpt-oss-20b

Generation

Grounded, concise, evidence-constrained

Project Structure

VERICORE/
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

Installation

Prerequisites

Python 3.10+

Node.js 18+

npm

Git

1. Clone

git clone https://github.com/Lingu17/Vericore---Evidence-First-Document-Intelligence.git
cd Vericore---Evidence-First-Document-Intelligence

2. Backend

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

On Windows, copy .env.example to .env manually if cp is unavailable.

3. Frontend

cd ../frontend
npm install

Environment Variables

Configure backend/.env:

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

# Local embedding model
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

Never commit .env or a real API key to Git.

Run Locally

Terminal 1 — Backend

cd backend
uvicorn app.main:app --reload --port 8000

Backend:

http://localhost:8000

FastAPI docs:

http://localhost:8000/docs

Terminal 2 — Frontend

cd frontend
npm run dev

Frontend:

http://localhost:5173

API Endpoints

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

Upload and index PDF/TXT

GET

/api/documents/{document_id}

Fetch document metadata

GET

/api/documents/{document_id}/suggestions

Get suggested questions

DELETE

/api/documents/{document_id}

Delete a document and vectors

DELETE

/api/documents

Clear indexed documents

POST

/api/chat

Submit a grounded document question

Testing

Run:

python -m pytest backend/tests -v

Current test result:

18 passed

The test suite covers:

Health check

Document upload

Duplicate document detection

Grounded Q&A

Unknown-question handling

Empty question validation

Chunk metadata preservation

Section detection

PDF page preservation

TXT parsing

Empty file rejection

Unsupported extension rejection

Corrupt PDF handling

High-confidence retrieval

Medium-confidence retrieval

Low-confidence retrieval

Grounding-aware confidence

Hybrid retrieval / relevance behavior

Demo Questions

Use the sample employee handbook to demonstrate:

What are the normal working hours?

How many days per week can employees work remotely?

When does an employee receive their first performance review?

How many hours per week must an employee work to be considered full-time?

What should an employee do if they expect to arrive late?

Hallucination Test

Ask:

What is the company's annual performance bonus?

Expected:

Information not available in the uploaded documents.

The system should not invent a bonus amount or generate unsupported information.

Design Decisions

Why Local Embeddings?

all-MiniLM-L6-v2 runs locally and avoids a separate external embedding API.

This keeps the embedding pipeline simple and reduces external API dependency.

Why ChromaDB?

ChromaDB provides lightweight persistent vector storage suitable for a focused RAG application without requiring additional external infrastructure.

Why FastAPI?

FastAPI provides:

Clear API boundaries

Request validation

Automatic API documentation

Straightforward integration with retrieval and LLM services

Why React + TypeScript?

React provides a flexible interface for:

Document management

Chat

Evidence inspection

Application state

TypeScript improves type safety and maintainability.

Why Hybrid Retrieval?

Pure semantic similarity can sometimes miss exact policy terminology, dates, numbers, and keywords.

Vericore combines semantic similarity with keyword coverage and reranking to improve retrieval for both conceptual and precise policy questions.

Why Deterministic Unknown Handling?

A document assistant should not treat every question as answerable.

If sufficient evidence cannot be retrieved, Vericore returns a deterministic unknown response instead of asking the LLM to infer or invent an answer.

Why Backend Source Validation?

Source attribution should not depend entirely on generated text.

The backend stores document metadata alongside each chunk and resolves returned source identifiers against those stored records before displaying the Evidence Trail.

Security

The project follows several basic security practices:

API keys are stored in environment variables.

.env files are not committed.

Real secrets are excluded from Git.

Uploaded documents are processed locally for extraction and embeddings.

Only retrieved evidence is passed to the LLM rather than complete documents.

Backend validation is applied to document and API inputs.

Source metadata is resolved by the backend instead of trusting generated citation text.

Limitations

The current implementation is intentionally scoped for a focused RAG application.

Known limitations:

Scanned/image-only PDFs require OCR support.

PDF extraction quality depends on document structure.

Complex tables may require specialized extraction.

The upload size limit is configured for lightweight workflows.

ChromaDB runs locally rather than as a distributed vector service.

LLM generation depends on the configured Groq API.

Authentication and multi-user access control are not implemented.

The current application is not designed for distributed production deployment.

Retrieval thresholds may require tuning for different document collections.

Large-scale retrieval benchmarking is not included.

Future Improvements

Potential next steps include:

OCR support for scanned PDFs

DOCX, CSV, and XLSX ingestion

Cross-document comparison mode

Improved table-aware retrieval

BM25 + vector hybrid retrieval

Dedicated cross-encoder reranking

Streaming LLM responses

Authentication and role-based access control

Cloud-based vector storage

Automated retrieval evaluation datasets and metrics

Document versioning and change tracking

Production observability and monitoring

AI-Assisted Development

AI-assisted development tools were used during implementation for:

Exploring RAG implementation approaches

Debugging retrieval behavior and edge cases

Reviewing code structure

Generating test ideas

Refining prompts

Improving response behavior

Refining project documentation

AI-generated suggestions were reviewed, tested, debugged, and adapted before being included in the final implementation.

Development Time

Vericore was developed within the assignment's specified 8-hour development constraint.

The development window covered:

Problem understanding and architecture

Core frontend and backend implementation

Document ingestion

RAG pipeline

Retrieval refinement

Hallucination handling

Evidence Trail implementation

Testing and debugging

UI refinement

Documentation

Final verification

Total development window: 8 hours

Assignment Alignment

Requirement

Vericore Implementation

PDF upload

PyMuPDF-based parser

TXT upload

Native TXT parser

Text extraction

Document parser

Chunking

Section / paragraph / sentence-aware chunker

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

Sample Documents

Sample documents are available under:

backend/sample_documents/

Examples:

NovaTech_Benefits_Policy.pdf
NovaTech_Employee_Handbook.pdf
NovaTech_Leave_Policy.pdf
NovaTech_Remote_Work_FAQ.txt

License

MIT License.

Project Summary

Vericore — Evidence-First Document Intelligence

A GenAI document intelligence project focused on:

Retrieval-Augmented Generation

Grounded question answering

Source attribution

Evidence inspection

Hallucination-aware document search

Practical business document workflows

Built around one principle

Don't just give an answer. Show the evidence behind it.

Final Repository Checklist

Before publishing:

Add docs/screenshots/home.png

Add docs/screenshots/workspace.png

Add docs/screenshots/evidence-trail.png

Confirm docs/architecture.png exists

Confirm .env is ignored

Confirm no real API keys exist in Git history

Run backend tests

Run npm run build

Verify the GitHub repository URL

Verify the demo video link

Verify README images render correctly on GitHub
