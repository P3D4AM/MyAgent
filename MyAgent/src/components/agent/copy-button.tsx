"use client";

import * as React from "react";
import { Check, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

/** Small copy-to-clipboard icon button with a "copied" state. */
export function CopyButton({
  text,
  className,
  label,
}: {
  text: string;
  className?: string;
  label?: string;
}) {
  const [copied, setCopied] = React.useState(false);

  const onCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      // clipboard unavailable — silently ignore
    }
  };

  return (
    <Button
      type="button"
      variant="ghost"
      size="icon"
      aria-label={label ?? "کپی"}
      onClick={onCopy}
      className={cn(
        "size-9 text-zinc-400 hover:text-emerald-300 hover:bg-emerald-500/10",
        className,
      )}
    >
      {copied ? (
        <Check className="size-4 text-emerald-400" />
      ) : (
        <Copy className="size-4" />
      )}
      <span className="sr-only">{label ?? "کپی در کلیپ‌بورد"}</span>
    </Button>
  );
}
