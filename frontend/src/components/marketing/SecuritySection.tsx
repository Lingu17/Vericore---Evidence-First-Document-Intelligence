import { Cpu, Route, KeyRound } from 'lucide-react';

const items = [
  {
    title: 'Local document embeddings',
    description:
      'Document embeddings are generated locally using a sentence-transformers model.',
    icon: Cpu,
  },
  {
    title: 'Source-aware retrieval',
    description:
      'Retrieved chunks retain document and page metadata so evidence can be traced back to the source.',
    icon: Route,
  },
  {
    title: 'Environment-based API configuration',
    description:
      'External model credentials are supplied through environment variables rather than hardcoded in the application.',
    icon: KeyRound,
  },
];

export function SecuritySection() {
  return (
    <section id="security" className="scroll-mt-24 border-b border-slate-200 bg-white">
      <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
        <div className="max-w-2xl">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-600">
            Technical approach
          </p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-[40px] sm:leading-tight">
            Built with a clear data and retrieval workflow.
          </h2>
        </div>

        <div className="mt-10 grid grid-cols-1 gap-4 md:grid-cols-3">
          {items.map(({ title, description, icon: Icon }) => (
            <div
              key={title}
              className="rounded-xl border border-slate-200 bg-white p-5 shadow-subtle"
            >
              <span className="flex h-9 w-9 items-center justify-center rounded-lg border border-brand-100 bg-brand-50 text-brand-600">
                <Icon className="h-[18px] w-[18px]" />
              </span>
              <h3 className="mt-4 text-[15px] font-semibold text-slate-900">{title}</h3>
              <p className="mt-2 text-[13px] leading-relaxed text-slate-600">{description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
