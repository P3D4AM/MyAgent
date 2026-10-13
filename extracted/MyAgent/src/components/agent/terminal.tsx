"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { LogLineView, type LogLineData } from "./log-line";

/** macOS-style terminal window chrome reused by hero + live demo. */
export function TerminalWindow({
  title,
  children,
  className,
  bodyClassName,
}: {
  title: string;
  children: React.ReactNode;
  className?: string;
  bodyClassName?: string;
}) {
  return (
    <div
      className={cn(
        "overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900 shadow-2xl shadow-zinc-950/60",
        className,
      )}
    >
      <div
        dir="ltr"
        className="relative flex items-center gap-2 border-b border-zinc-800 bg-zinc-950/70 px-4 py-3"
      >
        <span className="size-3 rounded-full bg-[#ff5f57]" aria-hidden="true" />
        <span className="size-3 rounded-full bg-[#febc2e]" aria-hidden="true" />
        <span className="size-3 rounded-full bg-[#28c840]" aria-hidden="true" />
        <span className="absolute left-1/2 -translate-x-1/2 font-mono text-xs text-zinc-500">
          {title}
        </span>
      </div>
      {children}
    </div>
  );
}

// -----------------------------------------------------------------------------
// Hero terminal — self-typing fake session, loops forever
// -----------------------------------------------------------------------------

const HERO_CMD = "parsagent run tasks/examples.json -t morning_routine";

type HeroLine =
  | { kind: "log"; tag: string; level: "info" | "ok"; text: string }
  | { kind: "prompt"; text: string };

const HERO_LINES: HeroLine[] = [
  { kind: "log", tag: "gate", level: "info", text: "engine=browser  mode=stealth  profile=per-platform" },
  {
    kind: "log",
    tag: "playwright",
    level: "info",
    text: "trying channels: msedge → chrome → chromium",
  },
  {
    kind: "log",
    tag: "playwright",
    level: "ok",
    text: "channel=msedge up — stealth: on (no download needed)",
  },
  { kind: "log", tag: "twitter", level: "ok", text: "tweet posted (64 chars)" },
  { kind: "log", tag: "linkedin", level: "ok", text: "feed post published" },
  { kind: "log", tag: "bale", level: "ok", text: "message sent → «تیم محصول»" },
  { kind: "log", tag: "notify", level: "ok", text: "روتین صبح کامل شد" },
  { kind: "prompt", text: "task completed in 14.2s — 5/5 steps OK" },
];

const LINE_DELAYS = [620, 780, 720, 680, 700, 680, 700, 560, 420];

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function HeroTerminal({ className }: { className?: string }) {
  const [cmd, setCmd] = React.useState("");
  const [lines, setLines] = React.useState<(HeroLine & { ts?: string })[]>([]);
  const [showCursor, setShowCursor] = React.useState(true);

  React.useEffect(() => {
    let cancelled = false;
    const reduced =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const printLine = (line: HeroLine & { ts?: string }) => {
      setLines((prev) => [...prev, line]);
    };

    const run = async () => {
      await sleep(500);
      while (!cancelled) {
        // reset
        setLines([]);
        setCmd("");

        // 1) type the command, char by char
        for (const ch of HERO_CMD) {
          if (cancelled) return;
          setCmd((c) => c + ch);
          await sleep(reduced ? 0 : 34 + Math.random() * 26);
        }

        // 2) print output lines with realistic gaps
        await sleep(reduced ? 120 : 380);
        for (let i = 0; i < HERO_LINES.length; i++) {
          if (cancelled) return;
          printLine({
            ...HERO_LINES[i],
            ts: new Date().toLocaleTimeString("en-GB", { hour12: false }),
          });
          await sleep(reduced ? 120 : (LINE_DELAYS[i] ?? 650));
        }

        // 3) hold, then loop
        await sleep(reduced ? 6000 : 4600);
      }
    };

    run();

    // blinking cursor independent of typing state
    const blink = window.setInterval(() => {
      setShowCursor((v) => !v);
    }, 530);

    return () => {
      cancelled = true;
      window.clearInterval(blink);
    };
  }, []);

  return (
    <TerminalWindow title="parsagent — cmd" className={className}>
      <div
        dir="ltr"
        className="min-h-[300px] p-4 text-left font-mono text-[12.5px] leading-7 text-zinc-300 sm:p-5 sm:text-[13px]"
      >
        {lines.length === 0 ? (
          <div>
            <span className="text-emerald-400">{"> "}</span>
            <span className="text-zinc-100">{cmd}</span>
            {showCursor && <span className="cursor-blink text-emerald-400">▍</span>}
          </div>
        ) : null}
        {lines.map((line, i) =>
          line.kind === "prompt" ? (
            <div key={i}>
              <span className="text-emerald-400">{"> "}</span>
              <span className="text-zinc-100">{line.text}</span>
            </div>
          ) : (
            <LogLineView
              key={i}
              ts={line.ts}
              line={{ tag: line.tag, level: line.level, text: line.text }}
            />
          ),
        )}
        {lines.length > 0 && showCursor && (
          <span className="cursor-blink text-emerald-400">▍</span>
        )}
      </div>
    </TerminalWindow>
  );
}
