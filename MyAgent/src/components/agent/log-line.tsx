"use client";

import { cn } from "@/lib/utils";
import type { LogLevel } from "./data";

/** Tag → color mapping for terminal log tags (mission-control palette). */
export const TAG_COLORS: Record<string, string> = {
  gate: "text-zinc-400",
  playwright: "text-amber-300",
  stealth: "text-emerald-300",
  desktop: "text-orange-300",
  scheduler: "text-yellow-300",
  notify: "text-lime-300",
};

const LEVEL_MARK: Record<LogLevel, { char: string; cls: string }> = {
  info: { char: "", cls: "" },
  ok: { char: "✓", cls: "text-emerald-400" },
  warn: { char: "!", cls: "text-amber-400" },
  error: { char: "✗", cls: "text-red-400" },
};

export interface LogLineData {
  tag: string;
  level: LogLevel;
  text: string;
}

/** A single terminal log line: `[HH:MM:SS] [tag      ] ✓ text` */
export function LogLineView({
  line,
  ts,
}: {
  line: LogLineData;
  ts?: string;
}) {
  const tagCls = TAG_COLORS[line.tag] ?? "text-emerald-300";
  const mark = LEVEL_MARK[line.level];

  return (
    <div className="whitespace-pre-wrap break-words" dir="ltr">
      {ts ? <span className="text-zinc-600">{ts} </span> : null}
      <span className={cn("font-medium", tagCls)}>
        [{line.tag.padEnd(10)}]
      </span>{" "}
      {mark.char ? (
        <span className={cn("font-bold", mark.cls)}>{mark.char} </span>
      ) : null}
      <span
        className={cn(
          line.level === "error" ? "text-red-300" : "text-zinc-300",
        )}
      >
        {line.text}
      </span>
    </div>
  );
}
