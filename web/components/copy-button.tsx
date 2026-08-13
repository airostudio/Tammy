"use client";

import { useState } from "react";

export function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(text).then(() => {
          setCopied(true);
          setTimeout(() => setCopied(false), 1500);
        });
      }}
      className="rounded-md border border-line-strong bg-surface px-3.5 py-1.25 text-[12.5px] transition-colors hover:border-teal hover:text-teal-deep"
    >
      {copied ? "Copied!" : "Copy"}
    </button>
  );
}
