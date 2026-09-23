import { Users, Settings, LineChart, Scale, Library } from 'lucide-react';

const useCases = [
  {
    title: 'HR & People Operations',
    description:
      'Search employee handbooks, policies, benefits documentation, and internal procedures.',
    icon: Users,
  },
  {
    title: 'Operations',
    description:
      'Find procedures, process documentation, operating guidelines, and internal instructions.',
    icon: Settings,
  },
  {
    title: 'Finance',
    description:
      'Locate information across reports, financial documentation, policies, and business records.',
    icon: LineChart,
  },
  {
    title: 'Legal & Compliance',
    description:
      'Quickly locate relevant clauses, requirements, and policy language across documents.',
    icon: Scale,
  },
  {
    title: 'Knowledge Management',
    description: 'Help teams find information spread across internal documentation.',
    icon: Library,
  },
];

export function UseCases() {
  return (
    <section id="use-cases" className="scroll-mt-24 border-b border-slate-200 bg-white">
      <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
        <div className="max-w-2xl">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-600">
            Use cases
          </p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-[40px] sm:leading-tight">
            Built for document-heavy work.
          </h2>
        </div>

        <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {useCases.map(({ title, description, icon: Icon }) => (
            <div
              key={title}
              className="rounded-xl border border-slate-200 bg-white p-5 shadow-subtle transition-colors hover:border-brand-300"
            >
              <span className="flex h-9 w-9 items-center justify-center rounded-lg border border-brand-100 bg-brand-50 text-brand-600">
                <Icon className="h-[18px] w-[18px]" />
              </span>
              <h3 className="mt-4 text-[15px] font-semibold text-slate-900">{title}</h3>
              <p className="mt-2 text-[13px] leading-relaxed text-slate-600">{description}</p>
            </div>
          ))}

          <div className="flex items-center rounded-xl border border-dashed border-slate-300 bg-slate-50/60 p-5">
            <p className="text-[13px] leading-relaxed text-slate-600">
              Any team that needs to find reliable information across a stack of internal
              documents can use the same upload → ask → verify workflow.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
