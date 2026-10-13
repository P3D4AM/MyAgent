"use client";

// -----------------------------------------------------------------------------
// Shared widgets for the ParsAgent control panel.
// -----------------------------------------------------------------------------

import * as React from "react";
import { Terminal } from "lucide-react";
import { cn } from "@/lib/utils";
import { CopyButton } from "@/components/agent/copy-button";
import { LogLineView } from "@/components/agent/log-line";
import { faDigits } from "@/components/agent/data";
import type { PanelLog } from "@/lib/panel/types";

// re-export for panel views
export { faDigits };

/* -------------------------------------------------------------------------- */
/* formatting helpers                                                          */
/* -------------------------------------------------------------------------- */

/** `۱:۰۴:۳۲` — persian uptime clock */
export function faUptime(totalSeconds: number): string {
  const s = Math.max(0, Math.floor(totalSeconds));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  return faDigits(`${h}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`);
}

/** `۰۹:۳۰` style — persian clock from epoch ms */
export function faClock(epochMs: number): string {
  const d = new Date(epochMs);
  return faDigits(
    `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}:${String(
      d.getSeconds(),
    ).padStart(2, "0")}`,
  );
}

export function faBytes(n: number): string {
  return n.toLocaleString("fa-IR");
}

/* -------------------------------------------------------------------------- */
/* StatCard                                                                    */
/* -------------------------------------------------------------------------- */

export function StatCard({
  icon,
  label,
  value,
  sub,
  accent = "emerald",
}: {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
  sub?: React.ReactNode;
  accent?: "emerald" | "amber" | "orange" | "rose";
}) {
  const accents: Record<string, string> = {
    emerald: "text-emerald-400 bg-emerald-500/10 ring-emerald-500/30",
    amber: "text-amber-400 bg-amber-500/10 ring-amber-500/30",
    orange: "text-orange-400 bg-orange-500/10 ring-orange-500/30",
    rose: "text-rose-400 bg-rose-500/10 ring-rose-500/30",
  };
  return (
    <div className="flex items-center gap-4 rounded-xl border border-zinc-800 bg-zinc-900/50 p-4">
      <span
        className={cn(
          "flex size-11 shrink-0 items-center justify-center rounded-lg ring-1",
          accents[accent],
        )}
      >
        {icon}
      </span>
      <div className="min-w-0">
        <div className="truncate text-xs text-zinc-400">{label}</div>
        <div className="mt-0.5 truncate text-xl font-extrabold text-zinc-100">{value}</div>
        {sub ? <div className="mt-0.5 truncate text-[11px] text-zinc-500">{sub}</div> : null}
      </div>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* StatusDot + badges                                                          */
/* -------------------------------------------------------------------------- */

export type DotState = "ok" | "busy" | "off" | "warn";

const DOT_CLS: Record<DotState, string> = {
  ok: "bg-emerald-400",
  busy: "bg-amber-400 animate-pulse",
  off: "bg-zinc-600",
  warn: "bg-rose-400",
};

export function StatusDot({ state, className }: { state: DotState; className?: string }) {
  return (
    <span className={cn("relative inline-flex size-2 rounded-full", DOT_CLS[state], className)} />
  );
}

export function StatusBadge({ state, label }: { state: DotState; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-zinc-800 bg-zinc-900/60 px-2.5 py-1 text-[11px] font-medium text-zinc-300">
      <StatusDot state={state} />
      {label}
    </span>
  );
}

/* -------------------------------------------------------------------------- */
/* Chip                                                                        */
/* -------------------------------------------------------------------------- */

export function Chip({
  children,
  className,
  onClick,
  active,
}: {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  active?: boolean;
}) {
  const Comp = onClick ? "button" : "span";
  return (
    <Comp
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-[11px] font-medium transition-colors",
        onClick && "cursor-pointer hover:border-emerald-500/50 hover:text-emerald-300",
        active
          ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-300"
          : "border-zinc-800 bg-zinc-900/60 text-zinc-400",
        className,
      )}
    >
      {children}
    </Comp>
  );
}

/* -------------------------------------------------------------------------- */
/* LogStream                                                                   */
/* -------------------------------------------------------------------------- */

export function LogStream({
  logs,
  className,
  autoScroll = true,
}: {
  logs: PanelLog[];
  className?: string;
  autoScroll?: boolean;
}) {
  const ref = React.useRef<HTMLDivElement>(null);
  const pinned = React.useRef(true);

  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const onScroll = () => {
      const gap = el.scrollHeight - el.scrollTop - el.clientHeight;
      pinned.current = gap < 48;
    };
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => el.removeEventListener("scroll", onScroll);
  }, []);

  React.useEffect(() => {
    const el = ref.current;
    if (el && autoScroll && pinned.current) {
      el.scrollTop = el.scrollHeight;
    }
  }, [logs, autoScroll]);

  return (
    <div
      ref={ref}
      dir="ltr"
      className={cn(
        "scrollbar-thin overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-950/70 p-3 font-mono text-[11.5px] leading-relaxed",
        className,
      )}
    >
      {logs.length === 0 ? (
        <div className="py-6 text-center font-sans text-xs text-zinc-600" dir="rtl">
          — هنوز لاگی ثبت نشده —
        </div>
      ) : (
        logs.map((line) => <LogLineView key={line.id} line={line} ts={line.ts} />)
      )}
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* CliHint — «معادل در ترمینال»                                                */
/* -------------------------------------------------------------------------- */

export function CliHint({
  command,
  label = "معادل در ترمینال",
  className,
}: {
  command: string;
  label?: string;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-lg border border-zinc-800 bg-zinc-950/70 px-3 py-2",
        className,
      )}
    >
      <Terminal className="size-3.5 shrink-0 text-emerald-500/80" aria-hidden="true" />
      <div className="min-w-0 flex-1">
        <div className="text-[10px] text-zinc-500" dir="rtl">
          {label}
        </div>
        <div dir="ltr" className="truncate font-mono text-[11px] text-zinc-300">
          {command}
        </div>
      </div>
      <CopyButton text={command} className="size-7 shrink-0" />
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* MiniBar — cpu / ram style meter                                             */
/* -------------------------------------------------------------------------- */

export function MiniBar({
  value,
  label,
  danger = 80,
}: {
  value: number;
  label: string;
  danger?: number;
}) {
  const v = Math.round(Math.min(100, Math.max(0, value)));
  const barCls =
    v > danger ? "bg-rose-500" : v > 55 ? "bg-amber-400" : "bg-emerald-500";
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-[11px]">
        <span className="text-zinc-400">{label}</span>
        <span className="font-mono text-zinc-300">{faDigits(v)}٪</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-zinc-800" dir="ltr">
        <div
          className={cn("h-full rounded-full transition-all duration-700", barCls)}
          style={{ width: `${v}%` }}
        />
      </div>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* EmptyState                                                                  */
/* -------------------------------------------------------------------------- */

export function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-800 bg-zinc-900/30 px-6 py-12 text-center">
      <span className="mb-3 flex size-12 items-center justify-center rounded-full bg-zinc-900 text-zinc-500 ring-1 ring-zinc-800">
        {icon}
      </span>
      <div className="text-sm font-bold text-zinc-300">{title}</div>
      {description ? <div className="mt-1 max-w-sm text-xs text-zinc-500">{description}</div> : null}
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
