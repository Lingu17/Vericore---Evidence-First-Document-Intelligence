import { FileText, MapPin, Bookmark, Quote, Percent, HelpCircle } from 'lucide-react';

const metaFields = [
  { label: 'Source document', value: 'Employee Handbook.pdf', icon: FileText },
  { label: 'Page', value: 'Page 14', icon: MapPin },
  { label: 'Section', value: 'Performance Reviews', icon: Bookmark },
  { label: 'Match information', value: 'Retrieved with the answer', icon: Percent },
];

export function EvidenceSection() {
  return (
    <section id="evidence" className="scroll-mt-24 border-b border-slate-200 bg-slate-50/70">
      <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
        <div className="grid grid-cols-1 gap-10 lg:grid-cols-2 lg:gap-14">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-600">
              Evidence Trail
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-[40px] sm:leading-tight">
              Answers are only useful when you can verify them.
            </h2>
            <p className="mt-4 text-base leading-relaxed text-slate-600">
              Vericore keeps retrieved evidence attached to the answer so users can inspect
              where the information came from.
            </p>

            {/* Unknown-state example */}
            <div className="mt-8 rounded-xl border border-slate-200 bg-white p-5 shadow-subtle">
              <div className="flex items-start gap-3">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-amber-200 bg-amber-50 text-amber-700">
                  <HelpCircle className="h-4 w-4" />
                </span>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                      Unknown handling
                    </h3>
                    <span className="rounded bg-slate-200/80 px-2 py-0.5 text-[10px] font-semibold text-slate-700">
                      No evidence
                    </span>
                  </div>
                  <p className="mt-2 text-sm font-medium text-slate-800">
                    Information not available in the uploaded documents.
                  </p>
                  <p className="mt-2 text-[13px] leading-relaxed text-slate-600">
                    When sufficient evidence is not available, Vericore can return an
                    explicit information-not-found response instead of presenting an
                    unsupported answer as fact.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Evidence card mock */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card sm:p-6">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <Quote className="h-4 w-4 text-brand-600" />
                <span className="text-xs font-bold uppercase tracking-wider text-slate-800">
                  Retrieved evidence
                </span>
              </div>
              <span className="font-mono text-[10px] text-slate-400">chunk-0014-03</span>
            </div>

            <dl className="mt-4 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
              {metaFields.map(({ label, value, icon: Icon }) => (
                <div
                  key={label}
                  className="rounded-lg border border-slate-200 bg-slate-50/70 px-3 py-2.5"
                >
                  <dt className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                    <Icon className="h-3 w-3 text-brand-600" />
                    {label}
                  </dt>
                  <dd className="mt-1 truncate text-[13px] font-semibold text-slate-800">
                    {value}
                  </dd>
                </div>
              ))}
            </dl>

            <div className="mt-4">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                Retrieved excerpt
              </p>
              <blockquote className="mt-2 rounded-lg border border-slate-200 bg-slate-50/70 p-3.5 font-mono text-xs leading-relaxed text-slate-700 selection:bg-amber-100">
                “You will have your first performance review at the end of your first three
                (3) months of employment with the Company. Reviews are conducted by the
                employee's direct manager...”
              </blockquote>
            </div>

            <p className="mt-4 border-t border-slate-100 pt-3 text-[11px] leading-relaxed text-slate-500">
              Every cited fact is traced back to the source document, page, and section
              shown above.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
