import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ShieldCheck, ArrowRight, Loader2 } from "lucide-react";

export function Login() {
  const [username, setUsername] = useState("owner");
  const [password, setPassword] = useState("");
  const [required, setRequired] = useState<boolean | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    fetch("/api/auth/status")
      .then((r) => r.json())
      .then((r) => setRequired(r.required))
      .catch(() => setError("The workspace is unavailable. Please retry."));
  }, []);
  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || "Sign-in failed.");
      setPassword("");
      window.location.assign("/app");
    } catch (e) {
      setPassword("");
      setError(e instanceof Error ? e.message : "Sign-in failed.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <Link to="/" className="inline-flex gap-3 items-center text-white mb-8">
          <span className="w-10 h-10 bg-brand-600 rounded-xl flex items-center justify-center font-bold text-xl">
            V
          </span>
          <span className="text-xl font-semibold">Vericore</span>
        </Link>
        <section className="bg-white rounded-2xl p-8 shadow-float">
          <ShieldCheck className="text-brand-600 w-8 h-8 mb-5" />
          <h1 className="text-2xl font-semibold tracking-tight">
            Your evidence workspace
          </h1>
          <p className="text-sm text-slate-500 mt-2 mb-6">
            Sign in to inspect documents, compare policies and run evaluations.
          </p>
          {error && (
            <p
              role="alert"
              className="text-sm text-rose-700 bg-rose-50 rounded-lg p-3 mb-4"
            >
              {error}
            </p>
          )}
          {required === false ? (
            <Link
              to="/app"
              className="inline-flex gap-2 items-center text-brand-700 font-medium"
            >
              Open local workspace <ArrowRight className="w-4 h-4" />
            </Link>
          ) : (
            <form onSubmit={submit} className="space-y-4">
              <label className="block text-sm font-medium">
                Username
                <input
                  autoComplete="username"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full border border-slate-200 rounded-lg p-3 mt-2"
                />
              </label>
              <label className="block text-sm font-medium">
                Workspace password
                <input
                  type="password"
                  autoComplete="off"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full border border-slate-200 rounded-lg p-3 mt-2"
                />
              </label>
              <button
                disabled={busy || required === null}
                className="w-full rounded-lg bg-slate-900 text-white p-3 flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {busy ? (
                  <Loader2 className="animate-spin w-4 h-4" />
                ) : (
                  <ArrowRight className="w-4 h-4" />
                )}
                Sign in
              </button>
            </form>
          )}
          <p className="text-xs text-slate-400 mt-6 leading-relaxed">
            Single-owner access. The deployment password is managed privately in
            your Render environment settings.
          </p>
        </section>
      </div>
    </main>
  );
}
