"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  DocumentInfo,
  Source,
  deleteDocument,
  listDocuments,
  streamChat,
  uploadDocument,
} from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

const COLLECTION = "default";

export default function Home() {
  const [docs, setDocs] = useState<DocumentInfo[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const refreshDocs = useCallback(async () => {
    try {
      setDocs(await listDocuments());
    } catch {
      /* backend may still be starting */
    }
  }, []);

  useEffect(() => {
    refreshDocs();
  }, [refreshDocs]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      await uploadDocument(file, COLLECTION);
      await refreshDocs();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  async function handleDelete(id: string) {
    await deleteDocument(id);
    await refreshDocs();
  }

  async function handleSend() {
    const question = input.trim();
    if (!question || busy) return;
    setInput("");
    setError(null);
    setBusy(true);

    setMessages((m) => [
      ...m,
      { role: "user", content: question },
      { role: "assistant", content: "", sources: [] },
    ]);

    const update = (fn: (msg: Message) => Message) =>
      setMessages((m) => {
        const copy = [...m];
        copy[copy.length - 1] = fn(copy[copy.length - 1]);
        return copy;
      });

    try {
      await streamChat(question, COLLECTION, (event) => {
        if (event.type === "sources") {
          update((msg) => ({ ...msg, sources: event.sources }));
        } else if (event.type === "token") {
          update((msg) => ({ ...msg, content: msg.content + event.text }));
        } else if (event.type === "error") {
          setError(event.message);
        }
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span>RAG</span> Knowledge Assistant
        </div>
        <div className="subtle">Chat with your documents, with citations.</div>

        <div className="upload-box">
          <p className="subtle" style={{ marginTop: 0 }}>
            Upload PDF, TXT, or Markdown
          </p>
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.txt,.md,.markdown"
            style={{ display: "none" }}
            onChange={handleUpload}
          />
          <button
            className="btn"
            disabled={uploading}
            onClick={() => fileRef.current?.click()}
          >
            {uploading ? "Indexing..." : "Upload document"}
          </button>
        </div>

        <div className="doc-list">
          {docs.length === 0 && (
            <div className="subtle">No documents indexed yet.</div>
          )}
          {docs.map((d) => (
            <div className="doc" key={d.id}>
              <div className="doc-name" title={d.filename}>
                {d.filename}
                <div className="subtle">{d.num_chunks} chunks</div>
              </div>
              <button className="icon-btn" onClick={() => handleDelete(d.id)}>
                ✕
              </button>
            </div>
          ))}
        </div>
      </aside>

      <main className="main">
        <div className="messages">
          {messages.length === 0 && (
            <div className="empty-state">
              <h2>Ask a question about your documents</h2>
              <p>
                Upload a file on the left, then ask anything. Answers are grounded
                in your documents and include numbered citations.
              </p>
            </div>
          )}

          {messages.map((m, i) => (
            <div className={`msg ${m.role}`} key={i}>
              <div className="role">{m.role}</div>
              <div
                className={`bubble ${
                  m.role === "assistant" && busy && i === messages.length - 1
                    ? "blink"
                    : ""
                }`}
              >
                {m.content}
              </div>
              {m.sources && m.sources.length > 0 && (
                <div className="citations">
                  {m.sources.map((s) => (
                    <div className="citation" key={s.chunk_id}>
                      <b>
                        [{s.marker}] {s.filename}
                        {s.page != null ? `, p.${s.page}` : ""}
                      </b>{" "}
                      &middot; score {s.score}
                      <div>{s.snippet}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          {error && <div className="error">{error}</div>}
          <div ref={bottomRef} />
        </div>

        <div className="composer">
          <textarea
            value={input}
            placeholder="Ask a question..."
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <button className="btn" disabled={busy || !input.trim()} onClick={handleSend}>
            {busy ? "..." : "Send"}
          </button>
        </div>
      </main>
    </div>
  );
}
