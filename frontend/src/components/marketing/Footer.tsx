import { Link } from 'react-router-dom';
import { ExternalLink } from 'lucide-react';

const GITHUB_URL = 'https://github.com/Lingu17/Vericore---Evidence-First-Document-Intelligence.git';

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto max-w-6xl px-6 py-12">
        <div className="flex flex-col gap-10 md:flex-row md:items-start md:justify-between">
          <div className="max-w-sm">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-sm font-bold text-white shadow-card">
                V
              </div>
              <div className="leading-tight">
                <div className="text-sm font-bold text-slate-900">Vericore</div>
                <div className="text-[11px] text-slate-500">
                  Evidence-First Document Intelligence
                </div>
              </div>
            </div>
            <p className="mt-4 text-[13px] leading-relaxed text-slate-600">
              Get answers from your documents — with the evidence to verify them.
            </p>
          </div>

          <nav className="flex flex-col gap-3">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Explore
            </span>
            <a href="#product" className="text-sm font-medium text-slate-700 hover:text-slate-900">
              Product
            </a>
            <a href="#how-it-works" className="text-sm font-medium text-slate-700 hover:text-slate-900">
              How it works
            </a>
            <a href="#use-cases" className="text-sm font-medium text-slate-700 hover:text-slate-900">
              Use cases
            </a>
            <Link to="/app" className="text-sm font-medium text-slate-700 hover:text-slate-900">
              Workspace
            </Link>
          </nav>

          <div className="flex flex-col gap-3">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Source
            </span>
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 text-sm font-medium text-slate-700 hover:text-slate-900"
            >
              <ExternalLink className="h-4 w-4" />
              GitHub
            </a>
          </div>
        </div>

        <div className="mt-10 border-t border-slate-200 pt-6">
          <p className="text-xs text-slate-500">
            © 2026 Vericore. Built as a document intelligence application.
          </p>
        </div>
      </div>
    </footer>
  );
}