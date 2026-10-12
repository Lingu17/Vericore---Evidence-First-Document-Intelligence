import { useEffect, useState } from "react";
import { DocumentItem, SourceEvidence, ChatResponse } from "../../types";

type Change = {
  changes?: { before: string; after: string }[];
  kind: string;
  explanation: string;
  potential_conflict?: boolean;
  before: SourceEvidence | null;
  after: SourceEvidence | null;
};
type Run = {
  id: string;
  created_at: string;
  passed: number;
  total: number;
  results: {
    question: string;
    passed: boolean;
    latency_ms: number;
    retrieval_precision: number | null;
    retrieval_recall: number | null;
    citation_coverage: number | null;
    unsupported_claim_rate: number | null;
    response: ChatResponse;
  }[];
};
async function request<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(
    "/api/" + path,
    body
      ? {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }
      : undefined,
  );
  if (!res.ok) {
    if (res.status === 401) window.location.assign("/login");
    const error = await res.json();
    throw new Error(
      typeof error.detail === "string" ? error.detail : "Request failed.",
    );
  }
  return res.json();
}

export function EvidenceLab({
  documents,
  onSource,
}: {
  documents: DocumentItem[];
  onSource: (source: SourceEvidence) => void;
}) {
  const [tab, setTab] = useState("compare");
  const [left, setLeft] = useState("");
  const [right, setRight] = useState("");
  const [changes, setChanges] = useState<Change[] | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [provider, setProvider] = useState<{
    provider: string;
    model: string;
    configured: boolean;
    mode: string;
    credential_management: string;
    owner_configuration_enabled: boolean;
  } | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState("openai/gpt-oss-20b");
  const [connection, setConnection] = useState("");
  useEffect(() => {
    request<{ runs: Run[] }>("evaluations")
      .then((r) => setRuns(r.runs))
      .catch((e) => setError(e.message));
    request<typeof provider>("provider")
      .then(setProvider)
      .catch((e) => setError(e.message));
  }, []);
  const metric = (value: number | null | undefined) =>
    value == null ? "N/A" : `${Math.round(value * 100)}%`;
  async function configure(action: "test" | "activate" | "clear") {
    setBusy(true);
    setError("");
    setConnection("");
    try {
      if (action === "clear") {
        const response = await fetch("/api/provider", { method: "DELETE" });
        if (!response.ok) throw new Error("Could not disconnect the API key.");
        setProvider(await response.json());
        setConnection("API key disconnected.");
      } else if (action === "test") {
        await request("provider/test", { api_key: apiKey, model });
        setConnection(
          "Groq credential and model validated. Key was not saved.",
        );
      } else {
        setProvider(
          await request<typeof provider>("provider", {
            api_key: apiKey,
            model,
          }),
        );
        setConnection(
          "Groq activated for your workspace until the server restarts.",
        );
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Connection failed.");
    } finally {
      setApiKey("");
      setBusy(false);
    }
  }
  async function run() {
    setBusy(true);
    setError("");
    try {
      const body = { left_id: left, right_id: right };
      if (tab === "compare")
        setChanges(
          (await request<{ changes: Change[] }>("compare", body)).changes,
        );
      else {
        const result = await request<Run>("evaluations", body);
        setRuns((prev) => [result, ...prev]);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="flex-1 overflow-auto p-6 bg-slate-50">
      <h1 className="text-xl font-semibold">Evidence Lab</h1>
      <p className="text-sm text-slate-500 mt-1">
        Compare policy versions and measure answers against original passages.
      </p>
      <nav className="flex gap-2 my-5" aria-label="Evidence Lab views">
        {["compare", "evaluations", "provider"].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg capitalize ${tab === t ? "bg-slate-900 text-white" : "bg-white border"}`}
          >
            {t}
          </button>
        ))}
      </nav>
      {error && (
        <p role="alert" className="p-3 bg-rose-50 text-rose-700 mb-4">
          {error}
        </p>
      )}
      {tab === "provider" ? (
        <section className="p-5 bg-white border rounded-xl space-y-3">
          <h2 className="font-semibold">Personal provider configuration</h2>
          {provider ? (
            <>
              <p>
                {provider.provider} · {provider.model}
              </p>
              <p>
                Credential:{" "}
                {provider.configured ? "Connected" : "Not configured"} · Mode:{" "}
                {provider.mode}
              </p>
              <p className="text-sm text-slate-500">
                {provider.credential_management}
              </p>
              <p className="text-sm">
                Set GROQ_API_KEY in backend/.env and restart the backend. Keys
                are never returned to this screen.
              </p>
            </>
          ) : (
            <p>Loading configuration…</p>
          )}
          {connection && (
            <p role="status" className="text-sm text-emerald-700">
              {connection}
            </p>
          )}
          {provider?.owner_configuration_enabled && (
            <div className="border-t border-slate-200 pt-4 space-y-3">
              <h3 className="font-semibold text-sm">Your Groq connection</h3>
              <p className="text-xs text-slate-500">
                Keys are validated with Groq, kept only in authenticated server
                memory, and cleared from this form after submission. They are
                never returned or stored in your browser. Restarting the service
                clears temporary account keys.
              </p>
              <label className="block text-sm">
                Groq model
                <input
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="block w-full max-w-md border border-slate-200 rounded-lg p-2 mt-1"
                />
              </label>
              <label className="block text-sm">
                Groq API key
                <input
                  type="password"
                  autoComplete="off"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="block w-full max-w-md border border-slate-200 rounded-lg p-2 mt-1"
                />
              </label>
              <div className="flex flex-wrap gap-2">
                <button
                  disabled={busy || !apiKey || !model}
                  onClick={() => configure("test")}
                  className="border rounded-lg px-3 py-2 text-sm disabled:opacity-40"
                >
                  Test connection
                </button>
                <button
                  disabled={busy || !apiKey || !model}
                  onClick={() => configure("activate")}
                  className="bg-slate-900 text-white rounded-lg px-3 py-2 text-sm disabled:opacity-40"
                >
                  Validate & activate
                </button>
                <button
                  disabled={busy}
                  onClick={() => configure("clear")}
                  className="border rounded-lg px-3 py-2 text-sm disabled:opacity-40"
                >
                  Disconnect API key
                </button>
              </div>
            </div>
          )}
        </section>
      ) : (
        <>
          <div className="flex flex-wrap gap-3 items-center mb-5">
            {[
              { label: "Original policy", value: left, set: setLeft },
              { label: "Revised policy", value: right, set: setRight },
            ].map((item) => (
              <label key={item.label} className="text-sm">
                {item.label}
                <select
                  aria-label={item.label}
                  value={item.value}
                  onChange={(e) => {
                    item.set(e.target.value);
                    setChanges(null);
                  }}
                  className="block border rounded-lg p-2 mt-1 bg-white max-w-64"
                >
                  <option value="">Select document</option>
                  {documents.map((d) => (
                    <option key={d.document_id} value={d.document_id}>
                      {d.filename}
                    </option>
                  ))}
                </select>
              </label>
            ))}
            <button
              onClick={run}
              disabled={busy || !left || !right || left === right}
              className="bg-slate-900 text-white rounded-lg px-4 py-2 disabled:opacity-40"
            >
              {busy
                ? "Running…"
                : tab === "compare"
                  ? "Compare sources"
                  : "Run policy evaluation"}
            </button>
          </div>
          {tab === "compare" ? (
            <div className="space-y-4">
              {changes === null ? (
                <p className="text-slate-500">
                  Select two uploaded documents to inspect added, removed and
                  modified passages.
                </p>
              ) : changes.length === 0 ? (
                <p>No passage changes found.</p>
              ) : (
                changes.map((c, i) => (
                  <section key={i} className="bg-white border rounded-xl p-4">
                    <h2 className="font-semibold capitalize">
                      {c.kind}
                      {c.potential_conflict && (
                        <span className="text-amber-700 text-xs ml-3">
                          Potential conflict · review context
                        </span>
                      )}
                    </h2>
                    <p className="text-xs text-slate-500 my-2">
                      {c.explanation}
                    </p>
                    {c.changes && (
                      <div className="flex flex-wrap gap-2 mb-3">
                        {c.changes.map((change, k) => (
                          <span
                            key={k}
                            className="text-xs bg-slate-50 border rounded px-2 py-1"
                          >
                            <del className="text-rose-700">
                              {change.before || "(empty)"}
                            </del>
                            <span className="mx-2">→</span>
                            <ins className="text-emerald-700 no-underline">
                              {change.after || "(empty)"}
                            </ins>
                          </span>
                        ))}
                      </div>
                    )}
                    <div className="grid md:grid-cols-2 gap-4">
                      {[c.before, c.after].map((s, j) => (
                        <div
                          key={j}
                          className="bg-slate-50 rounded-lg p-3 text-sm"
                        >
                          {s ? (
                            <>
                              <button
                                onClick={() => onSource(s)}
                                className="text-brand-700 underline text-xs"
                              >
                                {s.filename} · page {s.page} · {s.section}
                              </button>
                              <p className="mt-2 whitespace-pre-wrap">
                                {s.evidence}
                              </p>
                            </>
                          ) : (
                            <p className="text-slate-400">
                              No passage on this side.
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </section>
                ))
              )}
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-slate-500">
                Fixed dataset: upload Employee_Policy_2025.txt and
                Employee_Policy_2026.txt from backend/sample_documents. Other
                policies may fail these criteria. Each run uses the selected
                documents and the actual retrieval, generation and verification
                pipeline.
              </p>
              {runs.length === 0 && <p>No evaluations have run yet.</p>}
              {runs.map((r) => (
                <section key={r.id} className="border bg-white rounded-xl p-4">
                  <h2 className="font-semibold">
                    {r.passed}/{r.total} passed ·{" "}
                    {new Date(r.created_at).toLocaleString()}
                  </h2>
                  <p className="text-xs text-slate-500 mt-1">
                    Measured run · {r.id.slice(0, 8)} · Token usage and cost
                    unavailable
                  </p>
                  {r.results.map((result, i) => (
                    <div key={i} className="border-t mt-3 pt-3 text-sm">
                      <p
                        className={
                          result.passed ? "text-emerald-700" : "text-rose-700"
                        }
                      >
                        {result.passed ? "PASS" : "FAIL"} · {result.question}
                      </p>
                      <p className="my-2 whitespace-pre-line">
                        {result.response.answer}
                      </p>
                      <p className="text-xs text-slate-500">
                        {result.latency_ms} ms · Retrieval precision{" "}
                        {metric(result.retrieval_precision)} · Recall{" "}
                        {metric(result.retrieval_recall)} · Citation coverage{" "}
                        {metric(result.citation_coverage)} · Unsupported{" "}
                        {metric(result.unsupported_claim_rate)}
                      </p>
                      <div className="flex flex-wrap gap-3 mt-2">
                        {result.response.sources.map((s) => (
                          <button
                            key={s.chunk_id}
                            onClick={() => onSource(s)}
                            className="underline text-brand-700 text-xs"
                          >
                            {s.filename} · p. {s.page}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </section>
              ))}
            </div>
          )}
        </>
      )}
    </main>
  );
}
