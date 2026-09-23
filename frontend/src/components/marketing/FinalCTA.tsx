import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

export function FinalCTA() {
  return (
    <section className="border-b border-slate-200 bg-slate-900">
      <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-white sm:text-[40px] sm:leading-tight">
            Search your documents with context you can inspect.
          </h2>
          <p className="mt-4 text-base leading-relaxed text-slate-300">
            Upload a document, ask a question, and follow the evidence back to its source.
          </p>
          <div className="mt-8 flex justify-center">
            <Link
              to="/app"
              className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-brand-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900"
            >
              Open Vericore
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
