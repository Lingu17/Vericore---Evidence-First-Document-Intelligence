import { Link } from "react-router-dom";
import {
  ArrowRight,
  FileText,
  MessageSquareText,
  Quote,
  ShieldCheck,
} from "lucide-react";

const capabilities = [
  { label: "PDF & TXT", icon: FileText },
  { label: "Natural-language Q&A", icon: MessageSquareText },
  { label: "Source attribution", icon: ShieldCheck },
  { label: "Evidence Trail", icon: Quote },
];

export function HeroSection() {
  return (
    <section
      id="product"
      className="scroll-mt-16 border-b border-slate-200 bg-white"
    >
      <div className="mx-auto max-w-6xl px-6 pt-14 pb-14 sm:pt-16 sm:pb-16 lg:pb-20">
        <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-[1fr_1.05fr] lg:gap-12 xl:gap-16">
          {/* Left column — copy */}
          <div className="max-w-xl">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">
              Evidence-First Document Intelligence
            </p>

            <h1 className="mt-4 text-[34px] font-bold leading-[1.12] tracking-tight text-slate-900 sm:text-[44px] sm:leading-[1.08] xl:text-[52px] xl:leading-[1.06]">
              Get answers from your documents — with the evidence to verify
              them.
            </h1>

            <p className="mt-5 max-w-lg text-base leading-relaxed text-slate-600 sm:text-lg">
              Vericore helps teams find information across business documents,
              answer questions in natural language, and inspect the source
              behind each answer.
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
                <li
                  key={label}
                  className="flex items-center gap-2 text-[13px] font-medium text-slate-600"
                >
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
    <figure className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-float">
      <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-3">
        <span className="text-xs font-semibold text-slate-700">
          Inside the policy workspace
        </span>
        <span className="text-[10px] text-brand-700">
          Actual application screenshot
        </span>
      </div>
      <Link to="/app" aria-label="Explore the policy demonstration in Vericore">
        <img
          src="/workspace-preview.png"
          alt="Vericore answering across two employee policy versions, linking both leave clauses and displaying their potential conflict beside the original passage."
          className="w-full h-auto"
          width="1280"
          height="720"
        />
      </Link>
      <figcaption className="px-4 py-3 text-xs text-slate-500">
        Two policies. Every displayed claim linked to its passage. Conflicting
        values surfaced for review.
      </figcaption>
    </figure>
  );
}
