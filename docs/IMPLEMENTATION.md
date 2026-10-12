# Evidence-first policy workflow

## Original architecture and baseline

React 18 + TypeScript + Vite routes `/` to the landing page and `/app` to the
three-column workspace. Hooks call `/health`, `/api/documents` (list/delete-all),
`/api/documents/upload`, `/api/documents/{id}` (detail/delete),
`/api/documents/{id}/suggestions`, and `/api/chat`.

The upload router parses PDF/TXT using PyMuPDF and text decoding, splits semantic
sections, embeds with local all-MiniLM-L6-v2, then upserts the existing
`docupilot_knowledge_base` Chroma collection. A JSON registry stores document
metadata. Retrieval uses cosine candidates, lexical reranking, a relevance gate,
deduplication and adaptive context sizing. GroqProvider already existed with a
deterministic extractive fallback. The frontend renders sources in EvidencePanel
and EvidenceDrawer. There was no authentication or workspace ownership.

Baseline: 26 backend tests passed. Frontend build initially failed because
react-router-dom was missing from checked-in node_modules. Installing the declared
dependencies fixed that baseline problem. No frontend test or lint scripts existed.

Checklist: provider validation/timeouts → claim verification → original-passage
comparison → recorded evaluations → connected UI → security/build/deployment.

## Implemented workflow

1. Open `/app`, upload `Employee_Policy_2025.txt` and `Employee_Policy_2026.txt`
   from `backend/sample_documents`, or choose **Load policy demonstration**.
   This button executes the normal upload, extraction, embedding and indexing
   pipeline; it does not inject synthetic search results.
2. Choose **Compare leave**. The answer quotes the two policy statements (20 and
   25 days) and each claim links to the original indexed passage.
3. Choose **Inspect remote work**. The two versions allow 2 and 3 days per week.
   A potential-conflict notice exposes both sources without guessing precedence.
4. In **Compare & evaluate**, select the original and revised documents. Comparison
   reads Chroma's original passages and shows additions, removals, changed wording
   and both sides. A difference is not automatically a genuine contradiction.
5. Choose **Test refusal**. Neither fixture describes stock-option vesting. The
   response is exactly `Information not available in the uploaded documents.`
6. In **Evaluations**, run the same fixed questions against the selected pair.
   Actual responses, source metadata, latency, retrieval precision/recall, citation
   coverage, unsupported-claim rate and unknown-answer results are saved as JSON
   beside the existing Chroma directory. Failed criteria are visibly marked FAIL.

## Verification boundaries

Verification is deliberately conservative **textual attribution**, not a semantic
entailment model or proof that a document is true. Exact factual sentences can be
shown. Partial matches, unsupported sentences and numeric contradictions are
classified and withheld. Paraphrases can be refused. A confidence score measures
retrieval quality and never overrides verification. Numeric conflicts with matching
wording are potential conflicts; context, scope and effective dates require review.

Provider output uses a validated schema. Cited IDs must belong to retrieved evidence;
unknown IDs cannot produce a verified answer. Provider errors are sanitized and
the existing extractive fallback remains subject to verification. Cache keys include
source contents, scope and relevant conversation history. Both policy versions survive
cross-document deduplication. Original chat response fields remain compatible;
claims, verification method, retrieval IDs and potential conflicts are additive.

Evaluation criteria are independent fixed expectations for the included corpus,
not a general-purpose semantic answer grader. Retrieval precision/recall uses expected
chunk IDs matched from those known policy statements. Citation coverage and unsupported
rate describe generated claims; withheld claims still count. Unknown cases have no
relevant answer chunks, so non-applicable metrics are null. Cost and token usage are
null rather than invented. Live Groq success requires a real server-side API key.

## Security and configuration

- Production startup requires `WORKSPACE_PASSWORD`. Short-lived HttpOnly owner sessions (and Basic authentication for CLI clients) protect
  `/app`, all `/api/` routes and API documentation before source access. It is a
  single-owner workspace, not a multi-user SaaS authorization system. Use HTTPS.
- The landing page and its public screenshot contain only demonstration fixtures.
- Provider settings show masked server configuration status. API keys remain in
  the server environment; no personal key storage or browser persistence was added.
- Bounded upload reads reject oversize files before parsing, and filenames are
  stripped of path components. Existing parser validation remains intact.
- Uploaded instructions are untrusted evidence. No document code is executed.
- Mutating API requests have a per-process IP rate limit. Deploy one worker for
  this JSON-registry architecture; distributed access and durable transactions need
  a separate production design. Internal evaluation questions share the same pipeline.
- CORS is limited to configured origins; errors no longer return raw exceptions.
- Generated node_modules, Python bytecode and runtime Chroma files were removed
  from Git tracking while their local contents were retained. There are no database
  migrations or replacements of the existing collection.

New configuration: `PROVIDER_TIMEOUT_SECONDS=30`, `REQUESTS_PER_MINUTE=60`,
`WORKSPACE_USERNAME=owner`, `WORKSPACE_PASSWORD=` (set privately on production),
`EMBEDDING_BACKEND=sentence_transformers`. Groq variables retain their original names.

The Docker deployment uses optional `EMBEDDING_BACKEND=onnx`, the same model author's
ONNX export and tokenizer, masked mean pooling and normalized 384-dimensional vectors.
The original SentenceTransformer path stays the default for existing installations.
The ONNX path was numerically compared against that path and the policy suite was
executed on both. It reduces runtime memory for small hosts; it is not a substitute
embedding model. Install `requirements-onnx.txt` to use it locally.

## Local commands (PowerShell)

From the repository root, backend terminal:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Set GROQ_API_KEY in .env privately, or leave it empty for local extraction.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend terminal:

```powershell
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```

Open `http://127.0.0.1:5173`. Node 22.12+ is required by the upgraded build tooling.

Checks and evaluation (backend terminal, with server running for evaluate.py):

```powershell
$env:CHROMA_PATH='./test_chroma'
$env:USE_MOCK_LLM='true'
python -m pytest -q
python evaluate.py --output evaluation-result.json
# With optional ONNX dependencies installed:
$env:EMBEDDING_BACKEND='onnx'
$env:CHROMA_PATH='./test_onnx_chroma'
python -m pytest -q
```

Tests use disposable Chroma paths. Never run destructive test fixtures against an
actual workspace database. `evaluate.py` uploads/deduplicates its two fixtures and
retains them for inspection. It exits nonzero when any case fails.

Frontend checks: `npm run build` includes TypeScript compilation; `npm audit` checks
dependencies. No fabricated frontend unit-test or lint result is claimed.

## Deployment

`Dockerfile` builds the existing frontend and serves it with FastAPI on one origin.
The image bakes the model assets, uses a non-root user and one Uvicorn worker.
`render.yaml` describes a free Render web service with a generated owner password.
Sign in at `/login` with username `owner`. Find that password in Render's private environment settings; it is not redisplayed
in Vericore. Keep `GROQ_API_KEY` optional if evaluating local extraction only.

The free host's filesystem is ephemeral: uploaded documents and evaluation runs
are lost on restart/redeploy. This is a portfolio demo, not durable document hosting.
A persistent disk/volume with `CHROMA_PATH` pointing to it is needed for a reliable
private workspace. No Docker runtime was installed locally, so the remote build
must verify the container before deployment is considered successful.

## Priority next steps

1. Durable storage, backups and a transactional document registry.
2. Real multi-user identity, server-enforced workspace ownership and encrypted
   per-user secrets before any personal API-key management.
3. A larger independent evaluation corpus, semantic claim verification with
   validated quotation spans, and scope-aware contradiction grading.
4. Background ingestion and distributed rate limits for concurrent workloads.

The owner sign-in form sends credentials only to the server, clears its password field,
and uses Secure, HttpOnly, SameSite=Strict cookies in production. Sessions expire in
eight hours, are revoked on sign-out and are invalidated by process restart.
Cross-origin authenticated mutations are rejected. This remains a single-owner
identity boundary, not per-user ownership or credential storage.
