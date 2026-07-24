"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Masthead } from "@/components/masthead";
import { DocumentDrawer } from "@/components/document-drawer";
import { Finding, type Exchange } from "@/components/finding";
import { Composer } from "@/components/composer";
import {
  type DocumentInfo,
  deleteDocument,
  listDocuments,
  streamChat,
  uploadDocument,
} from "@/lib/api";

const COLLECTION = "default";

const SUGGESTIONS = [
  "Summarise the key points in one paragraph.",
  "What does this say about deadlines?",
  "List every requirement mentioned, with page numbers.",
];

export default function AppPage() {
  const [docs, setDocs] = useState<DocumentInfo[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const bottomRef = useRef<HTMLDivElement>(null);
  const seq = useRef(0);

  const refreshDocs = useCallback(async () => {
    try {
      setDocs(await listDocuments());
      setNotice(null);
    } catch {
      // The backend may still be booting — say so rather than showing an
      // empty catalog, which would read as "your uploads vanished".
      setNotice(
        "Can't reach the backend yet. If you just started it, give it a moment."
      );
    } finally {
      setLoadingDocs(false);
    }
  }, []);

  useEffect(() => {
    refreshDocs();
  }, [refreshDocs]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [exchanges]);

  async function handleUpload(file: File) {
    setUploading(true);
    setNotice(null);
    try {
      await uploadDocument(file, COLLECTION);
      await refreshDocs();
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(id: string) {
    // Optimistic: the card leaves the drawer immediately, and we re-sync after.
    const previous = docs;
    setDocs((d) => d.filter((doc) => doc.id !== id));
    try {
      await deleteDocument(id);
      await refreshDocs();
    } catch {
      setDocs(previous);
      setNotice("Could not withdraw that document.");
    }
  }

  async function handleSend() {
    const question = input.trim();
    if (!question || busy) return;

    const id = `x${++seq.current}`;
    setInput("");
    setBusy(true);
    setExchanges((xs) => [
      ...xs,
      { id, question, answer: "", sources: [], status: "retrieving" },
    ]);

    const patch = (fn: (x: Exchange) => Exchange) =>
      setExchanges((xs) => xs.map((x) => (x.id === id ? fn(x) : x)));

    try {
      await streamChat(question, COLLECTION, (event) => {
        if (event.type === "sources") {
          patch((x) => ({ ...x, sources: event.sources }));
        } else if (event.type === "token") {
          patch((x) => ({
            ...x,
            answer: x.answer + event.text,
            status: "streaming",
          }));
        } else if (event.type === "error") {
          patch((x) => ({ ...x, status: "error", error: event.message }));
        }
      });
      patch((x) =>
        x.status === "error" ? x : { ...x, status: "done" }
      );
    } catch (err) {
      patch((x) => ({
        ...x,
        status: "error",
        error:
          err instanceof Error
            ? err.message
            : "The request failed before an answer came back.",
      }));
    } finally {
      setBusy(false);
    }
  }

  const hasDocs = docs.length > 0;

  return (
    <div className="mx-auto max-w-[1180px] px-6 py-8 sm:px-8">
      <Masthead
        strapline={`Reference desk · Collection “${COLLECTION}”`}
        action={
          <Link
            href="/"
            className="label px-2.5 py-1.5 transition-colors hover:text-accent"
          >
            ← Front page
          </Link>
        }
      />

      {notice && (
        <div
          role="status"
          className="mt-5 border-l-2 border-accent bg-card px-4 py-3 text-[14px]"
        >
          {notice}
        </div>
      )}

      <div className="grid gap-9 pt-8 lg:grid-cols-[262px_1fr]">
        <DocumentDrawer
          docs={docs}
          loading={loadingDocs}
          uploading={uploading}
          onUpload={handleUpload}
          onDelete={handleDelete}
        />

        <main className="min-w-0">
          {exchanges.length === 0 ? (
            <div className="border-l-2 border-rule pl-5">
              <div className="label mb-1.5">Reading room</div>
              <h2 className="font-display text-[clamp(22px,3vw,30px)] leading-[1.2] font-bold tracking-[-0.01em]">
                {hasDocs
                  ? "Put a question to the collection."
                  : "File a document to begin."}
              </h2>
              <p className="mt-3 max-w-[52ch] text-[15px] leading-relaxed text-muted">
                {hasDocs
                  ? "Answers are drawn only from what you have filed, and every claim is numbered back to the page it came from."
                  : "Upload a PDF, text, or Markdown file using the card catalog on the left. It will be chunked, embedded, and indexed for retrieval."}
              </p>

              {hasDocs && (
                <div className="mt-6 space-y-2">
                  <div className="label">Try asking</div>
                  {SUGGESTIONS.map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => setInput(s)}
                      className="block w-full border-b border-dashed border-rule py-2 text-left text-[14px] transition-colors hover:text-accent"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-12">
              {exchanges.map((exchange) => (
                <Finding key={exchange.id} exchange={exchange} />
              ))}
            </div>
          )}

          <div ref={bottomRef} />

          <div className="mt-9 pb-6">
            <Composer
              value={input}
              onChange={setInput}
              onSend={handleSend}
              busy={busy}
              disabled={!hasDocs}
              disabledHint="File a document before asking a question…"
            />
          </div>
        </main>
      </div>
    </div>
  );
}
