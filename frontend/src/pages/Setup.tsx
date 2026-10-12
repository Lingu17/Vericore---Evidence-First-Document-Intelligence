import { FormEvent, useEffect, useState } from "react";
import { KeyRound, ArrowRight, Loader2, ShieldCheck } from "lucide-react";
export function Setup() {
  const [name, setName] = useState(""),
    [key, setKey] = useState(""),
    [model, setModel] = useState("openai/gpt-oss-20b"),
    [busy, setBusy] = useState(false),
    [ready, setReady] = useState(false),
    [error, setError] = useState("");
  useEffect(() => {
    fetch("/api/auth/status")
      .then((r) => r.json())
      .then((r) => {
        if (!r.user) {
          location.assign("/login");
          return;
        }
        if (r.provider_configured) {
          location.assign("/app");
          return;
        }
        setName(r.user.name);
        setReady(true);
      })
      .catch(() => setError("Could not load your account. Reload to retry."));
  }, []);
  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const r = await fetch("/api/provider", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: key, model }),
      });
      const data = await r.json();
      if (!r.ok)
        throw Error(
          typeof data.detail === "string"
            ? data.detail
            : "Check your key and model.",
        );
      setKey("");
      location.assign("/app");
    } catch (e) {
      setKey("");
      setError(e instanceof Error ? e.message : "Connection failed.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
      <section className="w-full max-w-lg bg-white rounded-2xl p-8 shadow-float">
        <p className="text-xs text-brand-600 font-semibold uppercase tracking-widest mb-6">
          Vericore · Step 2 of 2
        </p>
        <KeyRound className="text-brand-600 mb-5" size={32} />
        <h1 className="text-2xl font-semibold">Connect your intelligence</h1>
        <p className="text-sm text-slate-500 mt-3 mb-6">
          {name ? `Welcome, ${name}. ` : ""}Add your Groq API key to activate
          your personal evidence workspace.
        </p>
        {error && (
          <p
            role="alert"
            className="text-sm bg-rose-50 text-rose-700 rounded-lg p-3 mb-4"
          >
            {error}
          </p>
        )}
        <form onSubmit={submit} className="space-y-4">
          <label className="block text-sm font-medium">
            Groq API key
            <input
              required
              type="password"
              autoComplete="off"
              maxLength={1000}
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder="gsk_…"
              className="w-full border rounded-lg p-3 mt-2"
            />
          </label>
          <label className="block text-sm font-medium">
            Model
            <input
              required
              maxLength={100}
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full border rounded-lg p-3 mt-2"
            />
          </label>
          <p className="text-xs text-slate-500">
            Get a key from{" "}
            <a
              href="https://console.groq.com/keys"
              target="_blank"
              rel="noreferrer"
              className="text-brand-700 underline"
            >
              Groq Console
            </a>
            . Usage follows your account's limits.
          </p>
          <button
            disabled={busy || !ready}
            className="w-full bg-brand-600 text-white rounded-lg p-3 flex justify-center items-center gap-2 disabled:opacity-50"
          >
            {busy ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <ArrowRight size={16} />
            )}{" "}
            {busy ? "Validating connection…" : "Connect & open workspace"}
          </button>
        </form>
        <div className="mt-6 bg-slate-50 rounded-xl p-4 flex gap-3">
          <ShieldCheck className="text-brand-600 shrink-0" size={20} />
          <p className="text-xs text-slate-500 leading-relaxed">
            Your key stays in server memory for your account. It is never saved
            in your browser or returned by the API. Reconnect after a server
            restart. Your documents and evaluations are separate from other
            users.
          </p>
        </div>
        <button
          onClick={async () => {
            await fetch("/api/auth/logout", { method: "POST" });
            location.assign("/login");
          }}
          className="text-xs text-slate-500 mt-5"
        >
          Sign out
        </button>
      </section>
    </main>
  );
}
