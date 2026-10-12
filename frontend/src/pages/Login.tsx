import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Loader2, ShieldCheck } from "lucide-react";
export function Login() {
  const [status, setStatus] = useState<{
    public_accounts: boolean;
    google_enabled?: boolean;
    required: boolean;
  } | null>(null);
  const [register, setRegister] = useState(false),
    [name, setName] = useState(""),
    [email, setEmail] = useState(""),
    [password, setPassword] = useState(""),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(
      location.search.includes("error=")
        ? "Google sign-in failed. Retry or use your existing email account."
        : "",
    );
  useEffect(() => {
    fetch("/api/auth/status")
      .then((r) => r.json())
      .then(setStatus)
      .catch(() => setError("Service unavailable. Reload to retry."));
  }, []);
  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const r = await fetch(`/api/auth/${register ? "register" : "login"}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(
          register ? { email, name, password } : { username: email, password },
        ),
      });
      const result = await r.json();
      if (!r.ok)
        throw Error(
          typeof result.detail === "string"
            ? result.detail
            : "Check your account details.",
        );
      setPassword("");
      location.assign(status?.public_accounts ? "/setup" : "/app");
    } catch (e) {
      setPassword("");
      setError(e instanceof Error ? e.message : "Sign-in failed.");
    } finally {
      setBusy(false);
    }
  }
  const input = "w-full border border-slate-200 rounded-lg p-3 mt-2";
  return (
    <main className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <Link to="/" className="inline-flex gap-3 items-center text-white mb-8">
          <span className="w-10 h-10 bg-brand-600 rounded-xl grid place-items-center font-bold text-xl">
            V
          </span>
          <span className="text-xl font-semibold">Vericore</span>
        </Link>
        <section className="bg-white rounded-2xl p-8 shadow-float">
          <ShieldCheck className="text-brand-600 mb-5" size={32} />
          <p className="text-xs text-brand-600 uppercase tracking-widest mb-2 font-semibold">
            Evidence starts here
          </p>
          <h1 className="text-2xl font-semibold">
            {register ? "Create your workspace" : "Welcome to Vericore"}
          </h1>
          <p className="text-sm text-slate-500 mt-2 mb-6">
            Your documents. Your API key. Answers you can trace.
          </p>
          {error && (
            <p
              role="alert"
              className="text-sm bg-rose-50 text-rose-700 rounded-lg p-3 mb-4"
            >
              {error}
            </p>
          )}
          {status?.public_accounts && (
            <>
              <a
                href={status.google_enabled ? "/api/auth/google" : undefined}
                aria-disabled={!status.google_enabled}
                className={`flex justify-center gap-3 border rounded-lg p-3 font-medium ${status.google_enabled ? "hover:bg-slate-50" : "opacity-50 cursor-not-allowed"}`}
              >
                <span className="text-blue-600 font-bold">G</span>Continue with
                Google
              </a>
              {!status.google_enabled && (
                <p className="text-xs text-slate-500 mt-2">
                  Google sign-in is awaiting site configuration. Email accounts
                  are available now.
                </p>
              )}
              <p className="text-center text-xs text-slate-400 my-5">
                or use email
              </p>
            </>
          )}
          {status?.required === false ? (
            <Link to="/app">Open local workspace →</Link>
          ) : (
            <form onSubmit={submit} className="space-y-4">
              {register && (
                <label className="block text-sm font-medium">
                  Your name
                  <input
                    required
                    maxLength={80}
                    autoComplete="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className={input}
                  />
                </label>
              )}
              <label className="block text-sm font-medium">
                {status?.public_accounts ? "Email address" : "Username"}
                <input
                  required
                  type={status?.public_accounts ? "email" : "text"}
                  autoComplete="username"
                  maxLength={254}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={input}
                />
              </label>
              <label className="block text-sm font-medium">
                Password
                <input
                  required
                  type="password"
                  autoComplete={register ? "new-password" : "current-password"}
                  minLength={register ? 12 : 1}
                  maxLength={128}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={input}
                />
              </label>
              {register && (
                <p className="text-xs text-slate-500">
                  Use at least 12 characters. Password recovery is not available
                  yet.
                </p>
              )}
              <button
                disabled={busy || !status}
                className="w-full bg-slate-900 text-white rounded-lg p-3 flex justify-center gap-2 items-center disabled:opacity-50"
              >
                {busy ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <ArrowRight size={16} />
                )}{" "}
                {register ? "Create account" : "Sign in"}
              </button>
            </form>
          )}
          {status?.public_accounts && (
            <button
              onClick={() => {
                setRegister(!register);
                setPassword("");
                setError("");
              }}
              className="w-full text-sm text-brand-700 mt-5"
            >
              {register
                ? "Already have an account? Sign in"
                : "New here? Create an account"}
            </button>
          )}
          <p className="text-xs text-slate-400 mt-6">
            {status?.public_accounts
              ? "Connect your personal Groq key next. Free demo hosting may reset account data on restart."
              : "Owner credentials are managed in deployment settings."}
          </p>
        </section>
      </div>
    </main>
  );
}
