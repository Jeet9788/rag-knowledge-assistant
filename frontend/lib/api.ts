function resolveApiUrl(): string {
  // Explicit override wins (baked at build time).
  if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;

  if (typeof window !== "undefined") {
    const { protocol, hostname, port, origin } = window.location;
    // Legacy/dev entry point: the frontend is hit directly on :3000, so the
    // backend is a sibling on :8000 of the same host (cross-origin, HTTP).
    if (port === "3000") return `${protocol}//${hostname}:8000`;
    // Reverse-proxied entry point (ports 80/443, incl. the HTTPS tunnel): the
    // proxy serves the API same-origin under /api, so there is no cross-origin
    // call and no HTTP-from-HTTPS mixed-content block.
    return `${origin}/api`;
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
