import { Fragment, type ReactNode } from "react";

/**
 * Renders "…after onboarding[1]." with the bracketed markers promoted to
 * superscript footnote numbers in the accent colour.
 *
 * The model is prompted to cite as [n], so markers can appear mid-stream and
 * even mid-token; splitting on the completed pattern means a half-arrived "[1"
 * simply renders as text until its closing bracket lands.
 */
export function withCitations(text: string): ReactNode {
  return text.split(/(\[\d+\])/g).map((part, i) => {
    const match = part.match(/^\[(\d+)\]$/);
    if (!match) return <Fragment key={i}>{part}</Fragment>;
    return (
      <sup
        key={i}
        className="px-[3px] align-super font-mono text-[10px] font-bold text-accent"
      >
        {match[1]}
      </sup>
    );
  });
}
