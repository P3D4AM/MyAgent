"use client";

// -----------------------------------------------------------------------------
// Logs — full log viewer with tag/level filters and export.
// -----------------------------------------------------------------------------

import * as React from "react";
import { Download, Eraser, ScrollText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { usePanel } from "./panel-provider";
import { Chip, LogStream, faDigits } from "./widgets";
import type { PanelLogLevel } from "@/lib/panel/types";

const LEVELS: Array<{ id: PanelLogLevel | "all"; label: string }> = [
  { id: "all", label: "همه" },
  { id: "ok", label: "✓ موفق" },
  { id: "info", label: "اطلاع" },
  { id: "warn", label: "! هشدار" },
  { id: "error", label: "✗ خطا" },
];

export function LogsView() {
  const { state, dispatch } = usePanel();
  const [tag, setTag] = React.useState<string>("all");
  const [level, setLevel] = React.useState<PanelLogLevel | "all">("all");

  if (!state) return null;

  const tags = ["all", ...Array.from(new Set(state.logs.map((l) => l.tag)))];
  const filtered = state.logs.filter(
    (l) => (tag === "all" || l.tag === tag) && (level === "all" || l.level === level),
  );

  const exportLogs = () => {
    const text = filtered
      .map((l) => `[${l.ts}] [${l.tag.padEnd(10)}] ${l.level === "ok" ? "✓" : l.level === "warn" ? "!" : l.level === "error" ? "✗" : " "} ${l.text}`)
      .join("\n");
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "parsagent-panel.log";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-zinc-800 bg-zinc-900/50 px-4 py-3">
        <div className="flex items-center gap-2 text-sm text-zinc-400">
          <ScrollText className="size-4 text-emerald-400" aria-hidden="true" />
          {faDigits(filtered.length)} خط از {faDigits(state.logs.length)}
        </div>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={exportLogs}
            className="h-8 border-zinc-800 bg-zinc-900/60 text-xs hover:bg-zinc-800"
          >
            <Download className="size-3.5" aria-hidden="true" />
            خروجی .log
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => void dispatch("clearLogs")}
            className="h-8 border-zinc-800 bg-zinc-900/60 text-xs text-rose-300 hover:bg-rose-500/10"
          >
            <Eraser className="size-3.5" aria-hidden="true" />
            پاک‌کردن
          </Button>
        </div>
      </div>

      {/* filters */}
      <div className="flex flex-col gap-3 rounded-xl border border-zinc-800 bg-zinc-900/50 px-4 py-3">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="ml-1 text-[11px] font-bold text-zinc-500">سطح:</span>
          {LEVELS.map((l) => (
            <Chip key={l.id} active={level === l.id} onClick={() => setLevel(l.id)}>
              {l.label}
            </Chip>
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-1.5" dir="ltr">
          <span className="mr-1 text-[11px] font-bold text-zinc-500" dir="rtl">
            برچسب:
          </span>
          {tags.map((t) => (
            <Chip key={t} active={tag === t} onClick={() => setTag(t)}>
              <span className="font-mono">{t === "all" ? "همه" : t}</span>
            </Chip>
          ))}
        </div>
      </div>

      <LogStream logs={filtered} className="max-h-[60vh] flex-1" />
    </div>
  );
}
