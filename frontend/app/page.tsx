import Link from "next/link";
import { Masthead } from "@/components/masthead";
import { withCitations } from "@/components/cite";

const SPECIMEN = {
  question: "What is the remote work policy for new engineers?",
  answer:
    "New engineers may work remotely up to three days per week after completing " +
    "the 30-day onboarding period[1]. Fully remote arrangements require director " +
    "approval and a documented four-hour overlap with the team's core hours[2].",
  sources: [
    { marker: 1, filename: "employee-handbook.pdf", page: 14, score: 0.91 },
    { marker: 2, filename: "security-policy.md", page: 3, score: 0.84 },
  ],
};

const STEPS = [
  {
    n: "I",
    title: "File",
    body: "Drop in a PDF, text, or Markdown file. It is split into overlapping passages, embedded with BGE, and stored in Postgres with pgvector.",
  },
  {
    n: "II",
    title: "Retrieve",
    body: "Your question is embedded and matched against every passage. Dense and keyword results are fused with reciprocal rank fusion, then reranked.",
  },
  {
    n: "III",
    title: "Cite",
    body: "Only the winning passages are given to the model, which must footnote each claim. Every number opens onto the page it came from.",
  },
];

const COLOPHON = [
  ["Retrieval", "pgvector · hybrid search · RRF · cross-encoder rerank"],
  ["Embeddings", "BAAI/bge-small-en-v1.5 via fastembed (ONNX)"],
  ["Backend", "FastAPI · psycopg 3 · server-sent events"],
  ["Model", "Pluggable — Gemini, OpenAI, or local Ollama"],
  ["Frontend", "Next.js · TypeScript · Tailwind"],
  ["Infrastructure", "Docker Compose on EC2, scripted end to end"],
];

export default function LandingPage() {
  return (
    <div className="mx-auto max-w-[1180px] px-6 py-8 sm:px-8">
      <Masthead strapline="No. 001 · Retrieval-augmented generation" />

      {/* ── Hero ────────────────────────────────────────────────── */}
      <section className="grid gap-12 py-14 lg:grid-cols-[1.1fr_1fr] lg:py-20">
        <div>
          <h2 className="font-display text-[clamp(38px,7vw,68px)] leading-[0.94] font-black tracking-[-0.035em]">
            Ask your
            <br />
            documents.
            <br />
            <span className="text-accent">Check the answer.</span>
          </h2>
          <p className="mt-8 max-w-[46ch] text-[17px] leading-[1.7] text-muted">
            Most assistants answer from memory and leave you to trust them. This
            one answers only from the documents you file, and footnotes every
            claim back to the exact page — so you can go and look.
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-6">
            <Link
              href="/app"
              className="label px-7 py-3.5 transition-opacity hover:opacity-90"
              style={{
                backgroundColor: "var(--accent)",
                color: "var(--accent-ink)",
              }}
            >
              Open the reading room
            </Link>
            <a
              href="https://github.com/Jeet9788/rag-knowledge-assistant"
              target="_blank"
              rel="noreferrer"
              className="label inline-flex items-center gap-3 transition-colors hover:text-accent"
            >
              Read the source
              <span className="h-px w-10 bg-current" />
            </a>
          </div>
        </div>

        {/* Specimen: the product's real output, used as the hero image */}
        <div className="flex items-center">
          <div className="card-stock w-full p-6">
            <div className="flex items-baseline gap-3 border-b border-dashed border-rule pb-3">
              <span className="label">Specimen finding</span>
              <span className="leader" />
              <span className="label">2 authorities</span>
            </div>

            <h3 className="mt-5 font-display text-[19px] leading-snug font-bold">
              {SPECIMEN.question}
            </h3>

            <p className="mt-4 text-[14.5px] leading-[1.7]">
              {withCitations(SPECIMEN.answer)}
            </p>

            <div className="mt-5 border-t border-dashed border-rule pt-3.5">
              {SPECIMEN.sources.map((s) => (
                <div
                  key={s.marker}
                  className="flex items-baseline gap-2.5 py-1 font-mono text-[10.5px] text-muted"
                >
                  <span className="font-bold text-accent">[{s.marker}]</span>
                  <span className="truncate">{s.filename}</span>
                  <span className="leader" />
                  <span>
                    p.{s.page} · {s.score.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── How it works ────────────────────────────────────────── */}
      <section className="border-t-2 border-[var(--rule-strong)] pt-8">
        <div className="flex items-baseline gap-3">
          <span className="label">How it works</span>
          <span className="leader" />
        </div>

        <div className="mt-6 grid gap-5 md:grid-cols-3">
          {STEPS.map((step) => (
            <article key={step.n} className="card-stock p-5">
              <div className="flex items-baseline justify-between border-b border-dashed border-rule pb-2.5">
                <span className="font-display text-[26px] leading-none font-black text-accent">
                  {step.n}
                </span>
                <span className="label">Step</span>
              </div>
              <h3 className="mt-3.5 font-display text-[20px] font-bold">
                {step.title}
              </h3>
              <p className="mt-2 text-[14px] leading-relaxed text-muted">
                {step.body}
              </p>
            </article>
          ))}
        </div>
      </section>

      {/* ── Colophon ────────────────────────────────────────────── */}
      <section className="mt-16 border-t-2 border-[var(--rule-strong)] pt-8">
        <div className="flex items-baseline gap-3">
          <span className="label">Colophon</span>
          <span className="leader" />
        </div>

        <dl className="mt-5 grid gap-x-10 gap-y-0 md:grid-cols-2">
          {COLOPHON.map(([term, detail]) => (
            <div
              key={term}
              className="flex items-baseline gap-3 border-b border-dashed border-rule py-2.5"
            >
              <dt className="label shrink-0">{term}</dt>
              <span className="leader" />
              <dd className="text-right font-mono text-[11px] text-muted">
                {detail}
              </dd>
            </div>
          ))}
        </dl>
      </section>

      <footer className="mt-14 flex flex-wrap items-baseline justify-between gap-4 border-t-2 border-[var(--rule-strong)] pt-5 pb-10">
        <span className="label">Built by Jeet Patel</span>
        <Link href="/app" className="label transition-colors hover:text-accent">
          Open the reading room →
        </Link>
      </footer>
    </div>
  );
}
