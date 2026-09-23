import {
  MessageSquareText,
  FileCheck2,
  Quote,
  Combine,
  HelpCircle,
  LayoutGrid,
  Sparkles,
  Cpu,
} from 'lucide-react';

const features = [
  {
    title: 'Natural-language document search',
    description: 'Ask questions using normal language instead of manually scanning documents.',
    icon: MessageSquareText,
  },
  {
    title: 'Grounded answers',
    description: 'Responses are generated using retrieved document context.',
    icon: FileCheck2,
  },
  {
    title: 'Evidence Trail',
    description:
      'Inspect the source document, page, section, and retrieved excerpt behind an answer.',
    icon: Quote,
  },
  {
    title: 'Hybrid retrieval',
    description:
      'Combines semantic similarity with keyword coverage to improve retrieval of relevant passages.',
    icon: Combine,
  },
  {
    title: 'Unknown handling',
    description:
      'When relevant evidence is not available, the system can return an explicit information-not-found response.',
    icon: HelpCircle,
  },
  {
    title: 'Multi-document workspace',
    description: 'Search across documents available in the current knowledge workspace.',
    icon: LayoutGrid,
  },
  {
    title: 'Suggested questions',
    description: 'Generate useful follow-up questions based on uploaded document content.',
    icon: Sparkles,
  },
  {
    title: 'Local embeddings',
    description:
      'Document embeddings are generated locally using a sentence-transformers model.',
    icon: Cpu,
  },
];

export function Features() {
  return (
    <section id="features" className="scroll-mt-24 border-b border-slate-200 bg-slate-50/70">
      <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
        <div className="max-w-2xl">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-600">
            Features
          </p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-[40px] sm:leading-tight">
            Designed around the way teams work with documents.
          </h2>
        </div>

        <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {features.map(({ title, description, icon: Icon }) => (
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
        </div>
      </div>
    </section>
  );
}
