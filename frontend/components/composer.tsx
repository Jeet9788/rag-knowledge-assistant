"use client";

import { useRef, type KeyboardEvent } from "react";

export function Composer({
  value,
  onChange,
  onSend,
  busy,
  disabled,
  disabledHint,
}: {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  busy: boolean;
  disabled: boolean;
  disabledHint: string;
}) {
  const ref = useRef<HTMLTextAreaElement>(null);

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    // Enter sends; Shift+Enter is a newline — the convention every chat UI uses.
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  }

  function autoGrow() {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }

  return (
    <div>
      <div
        className="flex items-end gap-3 border-2 border-[var(--rule-strong)] bg-card p-3"
        style={{ boxShadow: "5px 5px 0 0 var(--shadow-offset)" }}
      >
        <textarea
          ref={ref}
          value={value}
          rows={1}
          disabled={disabled || busy}
          placeholder={
            disabled ? disabledHint : "Put a question to the collection…"
          }
          aria-label="Your question"
          onChange={(e) => {
            onChange(e.target.value);
            autoGrow();
          }}
          onKeyDown={handleKeyDown}
          className="max-h-[160px] min-h-[28px] flex-1 resize-none bg-transparent text-[15px] leading-relaxed text-ink outline-none placeholder:text-muted disabled:cursor-not-allowed"
        />
        <button
          type="button"
          onClick={onSend}
          disabled={disabled || busy || !value.trim()}
          className="label shrink-0 px-5 py-2.5 transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
          style={{ backgroundColor: "var(--accent)", color: "var(--accent-ink)" }}
        >
          {busy ? "Working" : "Enquire"}
        </button>
      </div>
      <p className="label mt-2 tracking-[0.16em] normal-case">
        Enter to send · Shift + Enter for a new line
      </p>
    </div>
  );
}
