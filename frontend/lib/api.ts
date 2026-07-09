function resolveApiUrl(): string {
  // Explicit override wins (baked at build time).
  if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;
  // In the browser, talk to the backend on the same host, port 8000.
  // This lets the same build run locally and on a deployed server.
  if (typeof window !== "undefined") {
    return `${window.location.protocol}//${window.location.hostname}:8000`;
  }
  return "http://localhost:8000";
}

export const API_URL = resolveApiUrl();

export interface DocumentInfo {
  id: string;
  filename: string;
  collection: string;
  num_chunks: number;
  created_at: string;
}

export interface Source {
  marker: number;
  chunk_id: string;
  document_id: string;
  filename: string;
  page: number | null;
  chunk_index: number;
  score: number;
  snippet: string;
}

export type ChatEvent =
  | { type: "sources"; sources: Source[] }
  | { type: "token"; text: string }
  | { type: "done" }
  | { type: "error"; message: string };

export async function listDocuments(): Promise<DocumentInfo[]> {
  const res = await fetch(`${API_URL}/documents`);
  if (!res.ok) throw new Error("Failed to load documents");
  return res.json();
}

export async function uploadDocument(
  file: File,
  collection: string
): Promise<void> {
  const form = new FormData();
  form.append("file", file);
  form.append("collection", collection);
  const res = await fetch(`${API_URL}/documents`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || "Upload failed");
  }
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/documents/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Delete failed");
}

/**
 * Stream a chat answer, parsing the backend's Server-Sent Events.
 * Calls onEvent for each parsed event.
 */
export async function streamChat(
  question: string,
  collection: string,
  onEvent: (event: ChatEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, collection }),
    signal,
  });
  if (!res.ok || !res.body) throw new Error("Chat request failed");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";
    for (const part of parts) {
      const dataLine = part
        .split("\n")
        .find((l) => l.startsWith("data:"));
      if (!dataLine) continue;
      try {
        const payload = JSON.parse(dataLine.slice("data:".length).trim());
        onEvent(payload as ChatEvent);
      } catch {
        // ignore malformed partial frames
      }
    }
  }
}
