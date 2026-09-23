import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X } from 'lucide-react';

const navLinks = [
  { label: 'Product', hash: '#product' },
  { label: 'How it works', hash: '#how-it-works' },
  { label: 'Use cases', hash: '#use-cases' },
];

export function MarketingNavbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2.5" onClick={() => setIsMenuOpen(false)}>
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-sm font-bold text-white shadow-card">
            V
          </div>
          <div className="leading-tight">
            <div className="text-sm font-bold text-slate-900">Vericore</div>
            <div className="hidden text-[11px] text-slate-500 sm:block">
              Evidence-First Document Intelligence
            </div>
          </div>
        </Link>

        <div className="flex items-center gap-3">
          <nav className="hidden items-center gap-6 text-sm font-medium text-slate-600 md:flex">
            {navLinks.map(({ label, hash }) => (
              <a key={hash} href={hash} className="hover:text-slate-900">
                {label}
              </a>
            ))}
          </nav>

          <Link
            to="/app"
            className="hidden items-center rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white shadow-card transition-all duration-200 hover:-translate-y-px hover:bg-brand-700 hover:shadow-lift sm:inline-flex"
          >
            Open workspace
          </Link>

          <button
            onClick={() => setIsMenuOpen((prev) => !prev)}
            className="md:hidden inline-flex items-center justify-center rounded-lg border border-slate-200 p-2 text-slate-700 transition-colors hover:bg-slate-50"
            aria-label="Toggle navigation menu"
            aria-expanded={isMenuOpen}
          >
            {isMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="border-t border-slate-200 bg-white md:hidden animate-fade-in">
          <nav className="mx-auto max-w-6xl space-y-1 px-6 py-3">
            {navLinks.map(({ label, hash }) => (
              <a
                key={hash}
                href={hash}
                onClick={() => setIsMenuOpen(false)}
                className="block rounded-lg px-3 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 hover:text-slate-900"
              >
                {label}
              </a>
            ))}
            <Link
              to="/app"
              onClick={() => setIsMenuOpen(false)}
              className="mt-2 flex items-center justify-center rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-brand-700"
            >
              Open workspace
            </Link>
          </nav>
        </div>
      )}
    </header>
  );
}