"use client";

// -----------------------------------------------------------------------------
// Recorder — macro recording control + visual stage + playback + macro library.
// -----------------------------------------------------------------------------

import * as React from "react";
import {
  Circle,
  CircleStop,
  Download,
  MousePointerClick,
  Play,
  Save,
  Sparkles,
  Square,
  Trash2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { usePanel } from "./panel-provider";
import { CliHint, EmptyState, StatusBadge, faDigits } from "./widgets";
import { cn } from "@/lib/utils";
import type { MacroEvent } from "@/lib/panel/types";

const STAGE_W = 1920;
const STAGE_H = 1080;

function eventLabel(ev: MacroEvent): string {
  const t = `${(ev.t / 1000).toFixed(1)}s`;
  switch (ev.type) {
    case "move":
      return `${t} — حرکت موس → (${ev.x}, ${ev.y})`;
    case "click":
      return `${t} — کلیک ${ev.button === "right" ? "راست" : "چپ"} در (${ev.x}, ${ev.y})`;
    case "key":
      return `${t} — کلید «${ev.key}»`;
    case "scroll":
      return `${t} — اسکرول در (${ev.x}, ${ev.y})`;
    case "hotkey":
      return `${t} — هاتکی ${(ev.keys ?? []).join("+")}`;
  }
}

/** interpolated cursor position for a live playback */
function cursorAt(events: MacroEvent[], elapsedMs: number, durationMs: number): { x: number; y: number } | null {
  if (events.length === 0) return null;
  const frac = Math.min(1, Math.max(0, elapsedMs / durationMs));
  const targetT = frac * (events[events.length - 1]?.t ?? 1);
  let prev = events[0];
  for (const ev of events) {
    if (ev.t >= targetT) {
      if (ev.x !== undefined && ev.y !== undefined) {
        // interpolate between prev and ev
        const span = ev.t - prev.t || 1;
        const k = (targetT - prev.t) / span;
        if (prev.x !== undefined && prev.y !== undefined) {
          return {
            x: prev.x + (ev.x - prev.x) * k,
            y: prev.y + (ev.y - prev.y) * k,
          };
        }
      }
      return ev.x !== undefined && ev.y !== undefined ? { x: ev.x, y: ev.y } : null;
    }
    prev = ev;
  }
  const last = events[events.length - 1];
  return last && last.x !== undefined && last.y !== undefined ? { x: last.x, y: last.y } : null;
}

export function RecorderView() {
  const { state, dispatch } = usePanel();
  const [macroName, setMacroName] = React.useState("");
  const [speed, setSpeed] = React.useState("1.5");
  const [, forceTick] = React.useState(0);

  // smooth rAF loop while recording or playing
  React.useEffect(() => {
    let raf = 0;
    const loop = () => {
      forceTick((n) => (n + 1) % 1000000);
      raf = window.requestAnimationFrame(loop);
    };
    raf = window.requestAnimationFrame(loop);
    return () => window.cancelAnimationFrame(raf);
  }, []);

  if (!state) return null;

  const recording = state.recorder;
  const playback = state.playback;
  const activeMacro = playback
    ? state.macros.find((m) => m.id === playback.macroId)
    : null;
  const stageEvents = playback
    ? (activeMacro?.events ?? [])
    : recording.events;
  const elapsed = playback ? Date.now() - playback.startedAt : 0;
  const playFrac = playback
    ? Math.min(1, elapsed / Math.max(1, playback.durationMs))
    : 0;
  const cursor = playback ? cursorAt(stageEvents, elapsed, playback.durationMs) : null;

  const moves = stageEvents.filter((e) => e.type === "move" || e.type === "click");
  const points = moves.map((e) => `${e.x},${e.y}`).join(" ");
  const clicks = stageEvents.filter((e) => e.type === "click");
  const recElapsedS = recording.active && recording.startedAt
    ? Math.max(0, (Date.now() - recording.startedAt) / 1000)
    : 0;

  return (
    <div className="grid gap-4 xl:grid-cols-5">
      {/* -------------------------------- stage + controls ------------------------------ */}
      <section
        aria-label="صحنهٔ ضبط"
        className="flex flex-col gap-4 rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 xl:col-span-3"
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <StatusBadge
              state={recording.active ? "busy" : playback ? "busy" : "off"}
              label={
                recording.active
                  ? "● در حال ضبط"
                  : playback
                    ? "▶ در حال بازپخش"
                    : "آماده"}
            />
            <span className="font-mono text-xs text-zinc-500" dir="ltr">
              {recording.active
                ? `REC ${recElapsedS.toFixed(1)}s · ${recording.events.length} events`
                : playback
                  ? `PLAY ×${playback.speed} · ${Math.round(playFrac * 100)}%`
                  : "1920×1080"}
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {recording.active ? (
              <>
                <Button
                  size="sm"
                  onClick={() => void dispatch("saveMacro", { name: macroName })}
                  className="h-8 bg-emerald-500 text-xs text-zinc-950 hover:bg-emerald-400"
                >
                  <Save className="size-3.5" aria-hidden="true" />
                  ذخیرهٔ ماکرو (F9)
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => void dispatch("recordClear")}
                  className="h-8 border-rose-500/30 bg-rose-500/5 text-xs text-rose-300 hover:bg-rose-500/10"
                >
                  <Trash2 className="size-3.5" aria-hidden="true" />
                  لغو (F10)
                </Button>
              </>
            ) : (
              <Button
                size="sm"
                disabled={!!playback}
                onClick={() => {
                  setMacroName("");
                  void dispatch("recordStart");
                }}
                className="h-8 bg-emerald-500 text-xs text-zinc-950 hover:bg-emerald-400"
              >
                <Circle className="size-3.5 fill-current" aria-hidden="true" />
                شروع ضبط
              </Button>
            )}
            {playback ? (
              <Button
                size="sm"
                variant="outline"
                onClick={() => void dispatch("stopPlayback")}
                className="h-8 border-amber-500/30 bg-amber-500/5 text-xs text-amber-300 hover:bg-amber-500/10"
              >
                <CircleStop className="size-3.5" aria-hidden="true" />
                توقف بازپخش
              </Button>
            ) : null}
            {recording.active ? (
              <Input
                value={macroName}
                onChange={(e) => setMacroName(e.target.value)}
                placeholder="نام ماکرو (اختیاری)"
                className="h-8 w-44 border-zinc-800 bg-zinc-900/60 text-xs"
              />
            ) : null}
          </div>
        </div>

        {/* stage */}
        <div
          dir="ltr"
          className="relative aspect-video w-full overflow-hidden rounded-lg border border-zinc-800 bg-zinc-950"
        >
          <svg
            viewBox={`0 0 ${STAGE_W} ${STAGE_H}`}
            className="absolute inset-0 size-full"
            aria-hidden="true"
          >
            {/* grid */}
            <defs>
              <pattern id="pgrid" width="96" height="96" patternUnits="userSpaceOnUse">
                <path d="M 96 0 L 0 0 0 96" fill="none" stroke="#27272a" strokeWidth="1" />
              </pattern>
            </defs>
            <rect width={STAGE_W} height={STAGE_H} fill="url(#pgrid)" />
            {points ? (
              <polyline
                points={points}
                fill="none"
                stroke={playback ? "#fbbf24" : "#34d399"}
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
                opacity="0.8"
              />
            ) : null}
            {clicks.map((c, i) => (
              <g key={i}>
                <circle cx={c.x} cy={c.y} r="16" fill={playback ? "#fbbf24" : "#34d399"} opacity="0.18">
                  <animate attributeName="r" values="10;22;10" dur="1.6s" repeatCount="indefinite" begin={`${(i * 0.4) % 1.6}s`} />
                </circle>
                <circle cx={c.x} cy={c.y} r="7" fill={playback ? "#fbbf24" : "#34d399"} />
              </g>
            ))}
            {cursor ? (
              <g>
                <circle cx={cursor.x} cy={cursor.y} r="26" fill="#fbbf24" opacity="0.15" />
                <circle cx={cursor.x} cy={cursor.y} r="11" fill="#fbbf24" stroke="#78350f" strokeWidth="3" />
              </g>
            ) : null}
          </svg>
          {stageEvents.length === 0 ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-zinc-600">
              <MousePointerClick className="size-8" aria-hidden="true" />
              <span className="font-sans text-xs" dir="rtl">
                صحنه خالی است — «شروع ضبط» را بزنید یا ماکروی نمونه بارگذاری کنید
              </span>
            </div>
          ) : null}
          {playback ? (
            <div className="absolute bottom-2 left-2 right-2">
              <Progress value={playFrac * 100} className="h-1 bg-zinc-800/80" />
            </div>
          ) : null}
        </div>

        <CliHint command="python main.py record -o macros/my.json   # سپس F9 برای ذخیره" />

        {/* event list */}
        <div>
          <div className="mb-2 flex items-center justify-between text-[11px] text-zinc-500">
            <span>رخدادهای ضبط‌شده ({faDigits(stageEvents.length)})</span>
            {stageEvents.length > 0 ? (
              <button
                onClick={() => void dispatch("recordClear")}
                className="text-rose-400/80 hover:text-rose-300"
              >
                پاک‌کردن
              </button>
            ) : null}
          </div>
          <div
            dir="ltr"
            className="scrollbar-thin max-h-56 overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-950/70 p-3 font-mono text-[11px] leading-6 text-zinc-400"
          >
            {stageEvents.length === 0 ? (
              <div className="py-4 text-center text-zinc-600">— no events —</div>
            ) : (
              [...stageEvents]
                .reverse()
                .slice(0, 80)
                .map((ev, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <span
                      className={cn(
                        "size-1.5 shrink-0 rounded-full",
                        ev.type === "click"
                          ? "bg-emerald-400"
                          : ev.type === "key" || ev.type === "hotkey"
                            ? "bg-amber-400"
                            : "bg-zinc-600",
                      )}
                    />
                    <span dir="rtl" className="font-sans text-zinc-400">
                      {eventLabel(ev)}
                    </span>
                  </div>
                ))
            )}
          </div>
        </div>
      </section>

      {/* -------------------------------- library --------------------------------- */}
      <section
        aria-label="کتابخانهٔ ماکرو"
        className="flex flex-col gap-4 rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 xl:col-span-2"
      >
        <div className="flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-sm font-bold text-zinc-200">
            <Sparkles className="size-4 text-emerald-400" aria-hidden="true" />
            کتابخانهٔ ماکرو
          </h3>
          <span className="text-[11px] text-zinc-500">{faDigits(state.macros.length)} فایل</span>
        </div>

        {state.macros.length === 0 ? (
          <EmptyState
            icon={<Download className="size-5" aria-hidden="true" />}
            title="ماکرویی ذخیره نشده"
            description="ضبط کنید و ذخیره بزنید، یا ماکروی آماده را برای تست بارگذاری کنید."
            action={
              <Button
                size="sm"
                variant="outline"
                onClick={() => void dispatch("loadSampleMacro")}
                className="h-8 border-zinc-800 bg-zinc-900/60 text-xs hover:bg-zinc-800"
              >
                <Download className="size-3.5" aria-hidden="true" />
                بارگذاری ماکروی نمونه
              </Button>
            }
          />
        ) : (
          <div className="grid max-h-[36rem] gap-3 overflow-y-auto pr-1 scrollbar-thin">
            {state.macros.map((macro) => (
              <article
                key={macro.id}
                className="flex flex-col gap-2.5 rounded-lg border border-zinc-800/80 bg-zinc-950/50 p-3"
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="min-w-0">
                    <div dir="ltr" className="truncate font-mono text-xs font-bold text-zinc-200">
                      macros/{macro.name}.json
                    </div>
                    <div className="mt-0.5 text-[10px] text-zinc-500">
                      {faDigits(macro.events.length)} رخداد ·{" "}
                      {faDigits((macro.durationMs / 1000).toFixed(1))} ثانیه
                    </div>
                  </div>
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={() => void dispatch("deleteMacro", { macroId: macro.id })}
                    aria-label={`حذف ${macro.name}`}
                    className="size-8 text-zinc-500 hover:text-rose-300"
                  >
                    <Trash2 className="size-3.5" aria-hidden="true" />
                  </Button>
                </div>
                <div className="flex items-center gap-2">
                  <Select value={speed} onValueChange={setSpeed}>
                    <SelectTrigger className="h-8 w-24 border-zinc-800 bg-zinc-900/60 text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="border-zinc-800 bg-zinc-950">
                      {["0.5", "1", "1.5", "2"].map((s) => (
                        <SelectItem key={s} value={s}>
                          ×{s}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button
                    size="sm"
                    disabled={!!playback}
                    onClick={() =>
                      void dispatch("playMacro", {
                        macroId: macro.id,
                        speed: Number(speed),
                      })
                    }
                    className="h-8 flex-1 bg-emerald-500 text-xs text-zinc-950 hover:bg-emerald-400"
                  >
                    <Play className="size-3.5" aria-hidden="true" />
                    بازپخش
                  </Button>
                </div>
                <CliHint command={`python main.py play macros/${macro.name}.json -s ${speed}`} />
              </article>
            ))}
          </div>
        )}

        <p className="rounded-lg border border-zinc-800/70 bg-zinc-950/40 p-3 text-[11px] leading-5 text-zinc-500">
          در نسخهٔ واقعی ویندوز، ضبط با
          <span dir="ltr" className="mx-1 font-mono text-emerald-400/90">pynput</span>
          انجام می‌شود؛ کلید
          <kbd className="mx-1 rounded border border-zinc-700 bg-zinc-800 px-1.5 py-0.5 font-mono text-[10px]">F9</kbd>
          ذخیره و
          <kbd className="mx-1 rounded border border-zinc-700 bg-zinc-800 px-1.5 py-0.5 font-mono text-[10px]">F10</kbd>
          لغو می‌کند. بازپخش با تأخیر انسانی و سرعت دلخواه اجرا می‌شود.
        </p>
      </section>
    </div>
  );
}
