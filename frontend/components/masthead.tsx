import Link from "next/link";
import { ThemeToggle } from "./theme-toggle";

/**
 * The newspaper masthead that opens both surfaces. `strapline` carries the
 * page-specific detail (collection name on the app, positioning line on the
 * landing page) in the slot a newspaper reserves for edition and date.
 */
export function Masthead({
  strapline,
  action,
}: {
  strapline: string;
  action?: React.ReactNode;
}) {
  return (
    <header className="border-b-2 border-[var(--rule-strong)] pb-4">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="label">{strapline}</div>
          <Link href="/" className="mt-1.5 block">
            <h1 className="font-display text-[clamp(28px,5vw,42px)] leading-none font-black tracking-[-0.02em]">
              <span className="text-accent">RAG</span> Knowledge Assistant
            </h1>
          </Link>
        </div>
        <div className="flex items-center gap-3">
          {action}
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
