import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAG Knowledge Assistant",
  description: "Chat with your documents using retrieval-augmented generation.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
