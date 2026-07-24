"use client";

import { useEffect, useState } from "react";
import { useTheme } from "next-themes";

const OPTIONS = [
  { value: "light", label: "Day" },
  { value: "dark", label: "Night" },
] as const;

export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // resolvedTheme is undefined until the client knows the real theme; render a
  // same-sized placeholder so the masthead doesn't reflow on hydration.
  useEffect(() => setMounted(true), []);

  return (
    <div
      className="inline-flex border border-rule"
      role="group"
      aria-label="Colour theme"
    >
      {OPTIONS.map((option) => {
        const active = mounted && resolvedTheme === option.value;
        return (
          <button
            key={option.value}
            type="button"
            onClick={() => setTheme(option.value)}
            aria-pressed={active}
            className={`label px-2.5 py-1.5 transition-colors ${
              active
                ? "bg-ink text-ground"
                : "text-muted hover:text-ink"
            }`}
            style={active ? { color: "var(--ground)" } : undefined}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
