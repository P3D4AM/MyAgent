"use client";

import * as React from "react";
import { CircleDot, MousePointer2, Play, Square, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { faDigits } from "./data";

interface Pt {
  x: number; // normalized 0..1
  y: number; // normalized 0..1
  t: number; // ms since recording start
}

type Phase = "idle" | "recording" | "replaying" | "done";

/** Sampling interval for mouse points (ms). */
const SAMPLE_MS = 30;
/** Replay speed multiplier. */
const REPLAY_SPEED = 1.5;

export function RecorderDemo() {
  // high-frequency mutable storage (event handlers / effects only)
  const pointsRef = React.useRef<Pt[]>([]);
  const clicksRef = React.useRef<Pt[]>([]);
  const recStartRef = React.useRef(0);
  const lastMoveRef = React.useRef(0);
  const rafRef = React.useRef(0);
  const trailIdxRef = React.useRef(0);

  // published snapshots (render source of truth)
  const [points, setPoints] = React.useState<Pt[]>([]);
  const [clicks, setClicks] = React.useState<Pt[]>([]);

  const [phase, setPhase] = React.useState<Phase>("idle");
  const [duration, setDuration] = React.useState(0);
  const [head, setHead] = React.useState<Pt | null>(null);
  const [replayT, setReplayT] = React.useState(0);
  const [trailIdx, setTrailIdx] = React.useState(0);

  const recording = phase === "recording";
  const count = points.length;
  const clickCount = clicks.length;
  const hasRecording = count > 1;

  /** Publish the mutable recording buffers into renderable state. */
  const flush = React.useCallback(() => {
    setPoints([...pointsRef.current]);
    setClicks([...clicksRef.current]);
  }, []);

  // live counters + live trail while recording
  React.useEffect(() => {
    if (phase !== "recording") return;
    const iv = window.setInterval(() => {
      setDuration((performance.now() - recStartRef.current) / 1000);
      flush();
      if (pointsRef.current.length > 0) {
        trailIdxRef.current = pointsRef.current.length - 1;
        setTrailIdx(pointsRef.current.length - 1);
      }
    }, 100);
    return () => window.clearInterval(iv);
  }, [phase, flush]);

  // cancel any rAF on unmount
  React.useEffect(() => () => cancelAnimationFrame(rafRef.current), []);

  const addPoint = (e: React.PointerEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    pointsRef.current.push({
      x: (e.clientX - rect.left) / rect.width,
      y: (e.clientY - rect.top) / rect.height,
      t: performance.now() - recStartRef.current,
    });
  };

  const onPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!recording) return;
    const now = performance.now();
    if (now - lastMoveRef.current < SAMPLE_MS) return;
    lastMoveRef.current = now;
    addPoint(e);
  };

  const onPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!recording) return;
    addPoint(e);
    const rect = e.currentTarget.getBoundingClientRect();
    clicksRef.current.push({
      x: (e.clientX - rect.left) / rect.width,
      y: (e.clientY - rect.top) / rect.height,
      t: performance.now() - recStartRef.current,
    });
  };

  const startRecording = () => {
    cancelAnimationFrame(rafRef.current);
    pointsRef.current = [];
    clicksRef.current = [];
    trailIdxRef.current = 0;
    recStartRef.current = performance.now();
    lastMoveRef.current = 0;
    setPoints([]);
    setClicks([]);
    setDuration(0);
    setHead(null);
    setReplayT(0);
    setTrailIdx(0);
    setPhase("recording");
  };

  const startReplay = () => {
    // publish the final recording before replaying
    flush();
    const pts = pointsRef.current;
    if (pts.length < 2) return;
    cancelAnimationFrame(rafRef.current);
    setPhase("replaying");
    const total = pts[pts.length - 1].t;
    const t0 = performance.now();
    trailIdxRef.current = 0;
    setTrailIdx(0);

    const step = (now: number) => {
      const el = (now - t0) * REPLAY_SPEED;
      if (el >= total) {
        trailIdxRef.current = pts.length - 1;
        setTrailIdx(pts.length - 1);
        setHead(pts[pts.length - 1]);
        setReplayT(total);
        setPhase("done");
        return;
      }
      let i = trailIdxRef.current;
      while (i + 1 < pts.length && pts[i + 1].t <= el) i++;
      trailIdxRef.current = i;
      const a = pts[i];
      const b = pts[Math.min(i + 1, pts.length - 1)];
      const span = b.t - a.t;
      const f = span > 0 ? Math.min(1, Math.max(0, (el - a.t) / span)) : 1;
      setTrailIdx(i);
      setHead({ x: a.x + (b.x - a.x) * f, y: a.y + (b.y - a.y) * f, t: el });
      setReplayT(el);
      rafRef.current = requestAnimationFrame(step);
    };
    rafRef.current = requestAnimationFrame(step);
  };

  const stopReplay = () => {
    cancelAnimationFrame(rafRef.current);
    setPhase("done");
  };

  const reset = () => {
    cancelAnimationFrame(rafRef.current);
    pointsRef.current = [];
    clicksRef.current = [];
    trailIdxRef.current = 0;
    setPoints([]);
    setClicks([]);
    setDuration(0);
    setHead(null);
    setReplayT(0);
    setTrailIdx(0);
    setPhase("idle");
  };

  const trailPoints = React.useMemo(
    () =>
      points
        .slice(0, trailIdx + 1)
        .map((p) => `${(p.x * 100).toFixed(2)},${(p.y * 100).toFixed(2)}`)
        .join(" "),
    [points, trailIdx],
  );

  const visibleClicks = clicks.filter(
    (c) => phase !== "replaying" || c.t <= replayT,
  );

  return (
    <Card className="border-zinc-800 bg-zinc-900/60">
      <CardContent className="flex flex-col gap-4 p-5 sm:p-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h3 className="text-lg font-extrabold text-zinc-100">
              ضبط‌کننده را همین‌جا امتحان کنید
            </h3>
            <p className="mt-1.5 max-w-2xl text-sm leading-7 text-zinc-400">
              همین نسخهٔ نمایشی، حرکات موس شما را داخل کادر ضبط می‌کند و مثل ماکروی
              واقعی پارس‌ایجنت بازپخش می‌کند؛ با کلیک‌ها، مسیر حرکت و سرعت ۱٫۵
              برابر.
            </p>
          </div>

          {/* controls */}
          <div className="flex flex-wrap items-center gap-2">
            {!recording && phase !== "replaying" ? (
              <>
                <Button
                  onClick={startRecording}
                  className="h-11 bg-emerald-500 text-zinc-950 hover:bg-emerald-400"
                >
                  <CircleDot className="size-4" aria-hidden="true" />
                  {hasRecording ? "ضبط دوباره" : "شروع ضبط"}
                </Button>
                <Button
                  onClick={startReplay}
                  disabled={!hasRecording}
                  variant="outline"
                  className="h-11 border-zinc-700 bg-zinc-900/60 text-zinc-200 hover:border-emerald-500/50 hover:bg-emerald-500/10 hover:text-emerald-300"
                >
                  <Play className="size-4" aria-hidden="true" />
                  بازپخش
                </Button>
              </>
            ) : null}

            {recording ? (
              <Button
                onClick={startReplay}
                disabled={count < 2}
                className="h-11 bg-amber-400 text-zinc-950 hover:bg-amber-300"
              >
                <Play className="size-4" aria-hidden="true" />
                توقف و بازپخش
              </Button>
            ) : null}

            {phase === "replaying" ? (
              <Button
                onClick={stopReplay}
                variant="outline"
                className="h-11 border-amber-400/40 bg-transparent text-amber-300 hover:bg-amber-400/10"
              >
                <Square className="size-4" aria-hidden="true" />
                توقف بازپخش
              </Button>
            ) : null}

            <Button
              onClick={reset}
              variant="ghost"
              disabled={count === 0 && clickCount === 0}
              className="h-11 text-zinc-400 hover:bg-red-500/10 hover:text-red-300"
            >
              <Trash2 className="size-4" aria-hidden="true" />
              پاک کردن
            </Button>
          </div>
        </div>

        {/* recording surface */}
        <div
          role="img"
          aria-label={
            recording
              ? "کادر ضبط حرکات موس — در حال ضبط"
              : "کادر ضبط حرکات موس"
          }
          onPointerMove={onPointerMove}
          onPointerDown={onPointerDown}
          className={cn(
            "relative h-72 w-full touch-none select-none overflow-hidden rounded-xl border bg-zinc-950 transition-colors",
            recording
              ? "border-red-500/60 shadow-[inset_0_0_40px_rgba(239,68,68,0.08)]"
              : phase === "replaying"
                ? "border-emerald-500/50"
                : "border-dashed border-zinc-700",
          )}
        >
          {/* empty hint */}
          {count === 0 && phase !== "recording" ? (
            <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center gap-2 text-zinc-600">
              <MousePointer2 className="size-6" aria-hidden="true" />
              <p className="text-xs">
                برای شروع، «شروع ضبط» را بزنید و موس را داخل کادر حرکت دهید
              </p>
            </div>
          ) : null}

          {/* REC indicator */}
          {recording ? (
            <div
              dir="ltr"
              className="absolute left-3 top-3 z-10 flex items-center gap-1.5 rounded-md bg-red-500/15 px-2 py-1 font-mono text-[10px] font-bold text-red-300 ring-1 ring-red-500/40"
            >
              <span
                className="size-2 animate-pulse rounded-full bg-red-400"
                aria-hidden="true"
              />
              REC
            </div>
          ) : null}

          {/* trail */}
          <svg
            className="pointer-events-none absolute inset-0 h-full w-full"
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
            aria-hidden="true"
          >
            <polyline
              points={trailPoints}
              fill="none"
              stroke="#34d399"
              strokeOpacity="0.65"
              strokeWidth="2"
              strokeLinejoin="round"
              strokeLinecap="round"
              vectorEffect="non-scaling-stroke"
            />
          </svg>

          {/* click markers */}
          {visibleClicks.map((c, i) => (
            <span
              key={i}
              className="pointer-events-none absolute -translate-x-1/2 -translate-y-1/2"
              style={{ left: `${c.x * 100}%`, top: `${c.y * 100}%` }}
              aria-hidden="true"
            >
              <span className="absolute inline-flex size-5 animate-ping rounded-full bg-amber-400/40" />
              <span className="relative inline-flex size-2.5 rounded-full bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.8)]" />
            </span>
          ))}

          {/* replay head */}
          {phase === "replaying" && head ? (
            <span
              className="pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-1/2"
              style={{ left: `${head.x * 100}%`, top: `${head.y * 100}%` }}
              aria-hidden="true"
            >
              <span className="block size-3.5 rounded-full bg-emerald-400 shadow-[0_0_16px_rgba(52,211,153,0.95)] ring-2 ring-emerald-200/40" />
            </span>
          ) : null}

          {/* live counters */}
          <div
            dir="rtl"
            className="pointer-events-none absolute bottom-3 right-3 z-10 flex items-center gap-3 rounded-md bg-zinc-900/80 px-3 py-1.5 text-[11px] text-zinc-400 ring-1 ring-zinc-800"
          >
            <span>
              رخدادها: <span className="font-mono text-zinc-200">{faDigits(count)}</span>
            </span>
            <span>
              کلیک: <span className="font-mono text-zinc-200">{faDigits(clickCount)}</span>
            </span>
            <span>
              مدت:{" "}
              <span className="font-mono text-zinc-200">
                {faDigits(duration.toFixed(1)).replace(".", "٫")} ثانیه
              </span>
            </span>
          </div>
        </div>

        <p className="text-[11px] leading-6 text-zinc-500">
          در ایجنت واقعی، همین ضبط با کلیدهای F9 (پایان) و F10 (لغو) انجام می‌شود و
          خروجی JSON آن با دستور <span dir="ltr" className="font-mono">play</span> و
          سرعت دلخواه بازپخش می‌گردد.
        </p>
      </CardContent>
    </Card>
  );
}
