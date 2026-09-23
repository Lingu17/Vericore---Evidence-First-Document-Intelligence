import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Bookmark,
  CheckCircle2,
  FileText,
  Layers,
  MapPin,
  MessageSquareText,
  Quote,
  ShieldCheck,
  UploadCloud,
} from 'lucide-react';

const capabilities = [
  { label: 'PDF & TXT', icon: FileText },
  { label: 'Natural-language Q&A', icon: MessageSquareText },
  { label: 'Source attribution', icon: ShieldCheck },
  { label: 'Evidence Trail', icon: Quote },
];

export function HeroSection() {
  return (
    <section id="product" className="scroll-mt-16 border-b border-slate-200 bg-white">
      <div className="mx-auto max-w-6xl px-6 pt-14 pb-14 sm:pt-16 sm:pb-16 lg:pb-20">
        <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-[1fr_1.05fr] lg:gap-12 xl:gap-16">
          {/* Left column — copy */}
          <div className="max-w-xl">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">
              Evidence-First Document Intelligence
            </p>

            <h1 className="mt-4 text-[34px] font-bold leading-[1.12] tracking-tight text-slate-900 sm:text-[44px] sm:leading-[1.08] xl:text-[52px] xl:leading-[1.06]">
              Get answers from your documents — with the evidence to verify them.
            </h1>

            <p className="mt-5 max-w-lg text-base leading-relaxed text-slate-600 sm:text-lg">
              Vericore helps teams find information across business documents, answer
              questions in natural language, and inspect the source behind each answer.
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
              <Link
                to="/app"
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-brand-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2"
              >
                Open workspace
                <ArrowRight className="h-4 w-4" />
              </Link>
              <a
                href="#how-it-works"
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50 hover:border-slate-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2"
              >
                See how it works
              </a>
            </div>

            <ul className="mt-9 flex flex-wrap items-center gap-x-6 gap-y-3 border-t border-slate-200 pt-6">
              {capabilities.map(({ label, icon: Icon }) => (
                <li key={label} className="flex items-center gap-2 text-[13px] font-medium text-slate-600">
                  <Icon className="h-4 w-4 text-brand-600" />
                  {label}
                </li>
              ))}
            </ul>
          </div>

          {/* Right column — product preview */}
          <HeroProductPreview />
        </div>
      </div>
    </section>
  );
}

function HeroProductPreview() {
  return (
    <div className="w-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-float transition-all duration-200 hover:-translate-y-1 hover:shadow-glow-blue">
      {/* Window header */}
      <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50/70 px-4 py-2.5">
        <div className="flex items-center gap-2 text-xs font-bold text-slate-800">
          <span className="flex h-5 w-5 items-center justify-center rounded bg-brand-600 text-[10px] font-bold text-white">
            V
          </span>
          Vericore
        </div>
        <span className="flex items-center gap-1.5 rounded-full border border-brand-200 bg-brand-50 px-2.5 py-1 text-[10px] font-semibold text-brand-700">
          <ShieldCheck className="h-3 w-3" />
          Evidence Trail
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-[172px_1fr]">
        {/* Left — Knowledge Workspace */}
        <div className="border-b border-slate-200 bg-slate-50/40 p-4 md:border-b-0 md:border-r">
          <div className="flex items-center gap-1.5">
            <Layers className="h-3.5 w-3.5 text-brand-600" />
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-800">
              Knowledge Workspace
            </span>
          </div>

          <div className="mt-3 rounded-lg border border-slate-200 bg-white p-3 shadow-subtle ring-1 ring-brand-200">
            <div className="flex items-center gap-2">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-rose-100 bg-rose-50 text-rose-600">
                <FileText className="h-3.5 w-3.5" />
              </span>
              <p className="min-w-0 truncate text-[11px] font-semibold text-slate-900">
                Employee Handbook.pdf
              </p>
            </div>
            <p className="mt-2 flex items-center gap-1 text-[10px] text-slate-500">
              <span>35 pages</span>
              <span>•</span>
              <span>219 chunks</span>
            </p>
            <p className="mt-1.5 flex items-center gap-1 text-[10px] font-medium text-emerald-700">
              <CheckCircle2 className="h-3 w-3 text-emerald-600" />
              Indexed
            </p>
          </div>

          <div className="mt-3 flex items-center justify-center gap-1.5 rounded-lg border border-dashed border-slate-300 px-2 py-2 text-[10px] text-slate-500">
            <UploadCloud className="h-3.5 w-3.5 text-brand-600" />
            PDF & TXT
          </div>
        </div>

        {/* Right — Question → Answer → Evidence */}
        <div className="space-y-4 p-4 sm:p-5">
          {/* Question */}
          <HeroMiniBlock label="Question">
            <div className="flex items-start gap-2">
              <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-200 text-[9px] font-semibold text-slate-700">
                You
              </span>
              <div className="rounded-xl rounded-tr-sm bg-slate-900 px-3.5 py-2.5 text-[12px] leading-relaxed text-white">
                When does an employee receive their first performance review?
              </div>
            </div>
          </HeroMiniBlock>

          {/* Answer */}
          <HeroMiniBlock label="Answer">
            <div className="rounded-xl border border-slate-200 bg-white p-3.5 shadow-subtle">
              <div className="mb-2 flex items-center justify-between border-b border-slate-100 pb-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                  Grounded answer
                </span>
                <span className="rounded border border-emerald-200 bg-emerald-50 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-700">
                  Verified
                </span>
              </div>
              <p className="text-[12px] leading-relaxed text-slate-800">
                You will have your first performance review at the end of your first three
                months of employment with the Company.
              </p>
            </div>
          </HeroMiniBlock>

          {/* Evidence */}
          <HeroMiniBlock label="Evidence Trail">
            <div className="rounded-xl border border-brand-200 bg-brand-50/40 p-3.5">
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="flex items-center gap-1 rounded bg-white px-1.5 py-0.5 text-[10px] font-semibold text-slate-700 ring-1 ring-slate-200">
                  <MapPin className="h-3 w-3 text-brand-500" />
                  Page 14
                </span>
                <span className="flex items-center gap-1 rounded bg-white px-1.5 py-0.5 text-[10px] font-semibold text-slate-700 ring-1 ring-slate-200">
                  <Bookmark className="h-3 w-3 text-brand-500" />
                  Performance Reviews
                </span>
                <span className="rounded bg-white px-1.5 py-0.5 text-[10px] font-medium text-slate-600 ring-1 ring-slate-200">
                  Retrieved evidence
                </span>
              </div>
              <blockquote className="mt-2.5 font-mono text-[11px] leading-relaxed text-slate-700 selection:bg-amber-100">
                “You will have your first performance review at the end of your first three
                (3) months...”
              </blockquote>
            </div>
          </HeroMiniBlock>
        </div>
      </div>
    </div>
  );
}

function HeroMiniBlock({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <p className="mb-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-500">
        {label}
      </p>
      {children}
    </div>
  );
}