import { UploadCloud, Search, MessageSquareText, FileSearch } from 'lucide-react';

const steps = [
  {
    num: '01',
    title: 'Upload your documents',
    description: 'Add PDF or TXT documents to create a searchable knowledge workspace.',
    icon: UploadCloud,
  },
  {
    num: '02',
    title: 'Retrieve relevant information',
    description:
      'Documents are processed into searchable chunks and represented with local embeddings for semantic retrieval.',
    icon: Search,
  },
  {
    num: '03',
    title: 'Ask a question',
    description:
      'Ask a factual question using natural language. Vericore retrieves relevant evidence before generating an answer.',
    icon: MessageSquareText,
  },
  {
    num: '04',
    title: 'Inspect the evidence',
    description:
      'Review the source document, page, section, and stored excerpt supporting the response.',
    icon: FileSearch,
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="scroll-mt-24 border-b border-slate-200 bg-white">
      <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
        <div className="max-w-2xl">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-600">
            How it works
          </p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-[40px] sm:leading-tight">
            From document to verified answer.
          </h2>
          <p className="mt-4 text-base leading-relaxed text-slate-600">
            Vericore combines document processing, retrieval, and grounded generation into
            a single workflow.
          </p>
        </div>

        <ol className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {steps.map(({ num, title, description, icon: Icon }) => (
            <li
              key={num}
              className="rounded-xl border border-slate-200 bg-white p-5 shadow-card transition-all duration-200 hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-lift"
            >
              <div className="flex items-center justify-between">
                <span className="flex h-9 w-9 items-center justify-center rounded-lg border border-brand-100 bg-brand-50 text-brand-600">
                  <Icon className="h-[18px] w-[18px]" />
                </span>
                <span className="font-mono text-xs font-semibold text-slate-400">{num}</span>
              </div>
              <h3 className="mt-4 text-[15px] font-semibold text-slate-900">{title}</h3>
              <p className="mt-2 text-[13px] leading-relaxed text-slate-600">{description}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
