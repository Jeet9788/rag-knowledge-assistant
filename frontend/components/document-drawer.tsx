"use client";

import { useRef } from "react";
import type { DocumentInfo } from "@/lib/api";

const ACCEPT = ".pdf,.txt,.md,.markdown";

export function DocumentDrawer({
  docs,
  loading,
  uploading,
  onUpload,
  onDelete,
}: {
  docs: DocumentInfo[];
  loading: boolean;
  uploading: boolean;
  onUpload: (file: File) => void;
  onDelete: (id: string) => void;
}) {
  const fileRef = useRef<HTMLInputElement>(null);
  const totalChunks = docs.reduce((sum, d) => sum + d.num_chunks, 0);

  return (
    <aside>
      <div className="mb-3 flex items-baseline gap-3">
        <span className="label">Card catalog</span>
        <span className="leader" />
        <span className="label">
          {docs.length} vol · {totalChunks} chunks
        </span>
      </div>

      <input
        ref={fileRef}
        type="file"
        accept={ACCEPT}
        className="sr-only"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onUpload(file);
          // Reset so re-picking the same filename still fires onChange.
          e.target.value = "";
        }}
      />

      <div className="space-y-2.5">
        {loading && docs.length === 0 && (
          <div className="card-stock p-3.5">
            <div className="label">Reading the shelves…</div>
          </div>
        )}

        {!loading && docs.length === 0 && (
          <div className="border border-dashed border-rule p-4">
            <p className="font-display text-[15px] leading-snug font-bold">
              The catalog is empty.
            </p>
            <p className="mt-1 text-[13px] leading-relaxed text-muted">
              File a document below and it will be split, embedded, and indexed
              for retrieval.
            </p>
          </div>
        )}

        {docs.map((doc, i) => (
          <article
            key={doc.id}
            className="card-stock anim-file group p-3.5 transition-transform hover:-translate-y-0.5"
            style={{ animationDelay: `${Math.min(i, 8) * 90}ms` }}
          >
            <div className="flex items-center justify-between border-b border-dashed border-rule pb-2">
              <span className="label text-accent">
                No. {String(i + 1).padStart(3, "0")}
              </span>
              <button
                type="button"
                onClick={() => onDelete(doc.id)}
                aria-label={`Remove ${doc.filename} from the catalog`}
                className="label opacity-0 transition-opacity group-hover:opacity-100 focus-visible:opacity-100 hover:text-accent"
              >
                Withdraw
              </button>
            </div>
            <h3
              className="mt-2 truncate font-display text-[15px] leading-snug font-bold"
              title={doc.filename}
            >
              {doc.filename}
            </h3>
            <div className="mt-1 font-mono text-[9.5px] text-muted">
              {doc.num_chunks} chunks indexed
            </div>
          </article>
        ))}
      </div>

      <button
        type="button"
        disabled={uploading}
        onClick={() => fileRef.current?.click()}
        className="mt-3.5 w-full border-2 border-dashed border-rule px-4 py-4 text-left transition-colors hover:border-accent disabled:cursor-wait"
      >
        <div className="font-display text-[14px] font-bold">
          {uploading ? "Filing…" : "+ File a document"}
        </div>
        <div className="label mt-0.5">
          {uploading ? "Chunking & embedding" : "PDF · TXT · MD"}
        </div>
      </button>
    </aside>
  );
}
