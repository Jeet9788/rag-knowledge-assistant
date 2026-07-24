"use client";

import { withCitations } from "./cite";
import type { Source } from "@/lib/api";

export interface Exchange {
  id: string;
  question: string;
  answer: string;
  sources: Source[];
  /** retrieving → sources back, nothing written yet; streaming → tokens arriving. */
  status: "retrieving" | "streaming" | "done" | "error";
  error?: string;
}

export function Finding({ exchange }: { exchange: Exchange }) {
  const { question, answer, sources, status, error } = exchange;

  return (
    <article className="anim-rise">
      {/* Enquiry, set as a standfirst */}
      <div className="border-l-2 border-accent pl-5">
        <div className="label mb-1.5">Enquiry</div>
        <h2 className="font-display text-[clamp(20px,2.6vw,27px)] leading-[1.22] font-bold tracking-[-0.01em]">
          {question}
        </h2>
      </div>

      {/* Retrieval trace — only while there is nothing else to show */}
      {status === "retrieving" && (
        <div className="mt-6 flex items-baseline gap-3 font-mono text-[10.5px] text-muted">
          <span className="text-accent">▸</span>
          <span>searching the collection</span>
          <span className="leader" />
          <span className="caret" />
        </div>
      )}

      {error && (
        <div
          role="alert"
          className="mt-6 border-l-2 border-accent bg-card px-4 py-3"
        >
          <div className="label mb-1">Could not complete</div>
          <p className="text-[14px] leading-relaxed">{error}</p>
        </div>
      )}

      {/* Finding */}
      {answer && (
        <div className="mt-7 border-t-2 border-[var(--rule-strong)] pt-6">
          <div className="label mb-3">Finding</div>
          <p
            className={`max-w-[64ch] text-[17px] leading-[1.72] ${
              status === "streaming" ? "caret" : ""
            }`}
          >
            {withCitations(answer)}
          </p>
        </div>
      )}

      {/* Authorities */}
      {sources.length > 0 && (
        <section className="mt-8">
          <div className="mb-3 flex items-baseline gap-3">
            <span className="label">Authorities cited</span>
            <span className="leader" />
          </div>

          {sources.map((source, i) => (
            <div
              key={source.chunk_id}
              className="anim-rise flex gap-4 border-b border-dashed border-rule py-3.5"
              style={{ animationDelay: `${Math.min(i, 6) * 90}ms` }}
            >
              <div
                className="anim-stamp mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-full font-mono text-[10px] font-bold"
                style={{
                  backgroundColor: "var(--accent)",
                  color: "var(--accent-ink)",
                  animationDelay: `${Math.min(i, 6) * 90 + 120}ms`,
                }}
              >
                {source.marker}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-baseline gap-x-2.5">
                  <span
                    className="font-display text-[15px] font-bold"
                    title={source.filename}
                  >
                    {source.filename}
                  </span>
                  <span className="font-mono text-[10px] text-muted">
                    {source.page != null && `p. ${source.page} · `}
                    similarity {source.score.toFixed(2)}
                  </span>
                </div>
                <p className="mt-1 text-[13.5px] leading-relaxed text-muted italic">
                  “{source.snippet}”
                </p>
              </div>
            </div>
          ))}
        </section>
      )}
    </article>
  );
}
