"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import {
  CheckCircle2,
  Globe,
  MousePointerClick,
  Play,
  Square,
  Trash2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { RecorderDemo } from "./recorder-demo";
import { LogLineView } from "./log-line";
import { PlatformIcon, PLATFORM_VISUALS } from "./platform-icons";
import { SectionHeader, FadeIn } from "./section-header";
import { TerminalWindow } from "./terminal";
import {
  PLATFORMS,
  SPEEDS,
  buildScript,
  faDigits,
  getPlatform,
  logTimestamp,
  type EngineId,
  type LogLevel,
  type SpeedId,
} from "./data";

/** base delay per weight unit at normal speed */
const BASE_MS = 700;
/** per-character delay for animated (typing) log lines */
const CHAR_MS = 24;

interface DemoLine {
  id: number;
  tag: string;
  level: LogLevel;
  text: string;
  ts: string;
}

type RunStatus = "idle" | "running" | "success" | "stopped" | "error";

const STATUS_META: Record<RunStatus, { label: string; cls: string; pulse?: boolean }> = {
  idle: { label: "آماده", cls: "bg-zinc-800/80 text-zinc-300 ring-zinc-700" },
  running: {
    label: "در حال اجرا",
    cls: "bg-emerald-500/15 text-emerald-300 ring-emerald-500/40",
    pulse: true,
  },
  success: { label: "موفق", cls: "bg-emerald-500 text-zinc-950 ring-emerald-500" },
  stopped: { label: "متوقف", cls: "bg-amber-400/15 text-amber-300 ring-amber-400/40" },
  error: { label: "خطا", cls: "bg-red-500/15 text-red-300 ring-red-500/40" },
};

const sleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

function faSeconds(seconds: number): string {
  return faDigits(seconds.toFixed(1)).replace(".", "٫");
}

export function Demo() {
  // ---- form state ----
  const [platformId, setPlatformId] = React.useState("instagram");
  const [actionId, setActionId] = React.useState("post_photo");
  const [text, setText] = React.useState("سلام! این یک پست خودکار از پارس‌ایجنت است");
  const [target, setTarget] = React.useState("@parsagent");
  const [image, setImage] = React.useState("assets/photo.jpg");
  const [engine, setEngine] = React.useState<EngineId>("browser");
  const [networkIssue, setNetworkIssue] = React.useState(false);
  const [speed, setSpeed] = React.useState<SpeedId>("normal");

  // ---- run state ----
  const [lines, setLines] = React.useState<DemoLine[]>([]);
  const [status, setStatus] = React.useState<RunStatus>("idle");
  const [progress, setProgress] = React.useState(0);
  const [elapsed, setElapsed] = React.useState(0);
  const [stepsDone, setStepsDone] = React.useState(0);
  const [stepsTotal, setStepsTotal] = React.useState(0);

  const runIdRef = React.useRef(0);
  const lineIdRef = React.useRef(0);
  const bodyRef = React.useRef<HTMLDivElement>(null);

  const platform = getPlatform(platformId);
  const action =
    platform.actions.find((a) => a.id === actionId) ?? platform.actions[0];
  const running = status === "running";

  // keep the terminal scrolled to the latest line
  React.useEffect(() => {
    const el = bodyRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [lines]);

  const pushLine = (tag: string, level: LogLevel, textStr: string) => {
    setLines((prev) => [
      ...prev,
      { id: lineIdRef.current++, tag, level, text: textStr, ts: logTimestamp() },
    ]);
  };

  const selectPlatform = (id: string) => {
    setPlatformId(id);
    setActionId(getPlatform(id).actions[0].id);
  };

  const stop = () => {
    if (!running) return;
    runIdRef.current++;
    setStatus("stopped");
    pushLine("gate", "error", "task aborted by user (signal: stop)");
  };

  const clear = () => {
    runIdRef.current++;
    setLines([]);
    setStatus("idle");
    setProgress(0);
    setElapsed(0);
    setStepsDone(0);
    setStepsTotal(0);
  };

  const run = async () => {
    const script = buildScript(
      platform,
      action,
      { text, target, image },
      { networkIssue, engine },
    );
    const totalWeight = script.reduce((acc, st) => acc + st.weight, 0);
    const mult = SPEEDS[speed].mult;
    const runId = ++runIdRef.current;

    setStatus("running");
    setLines([]);
    setProgress(0);
    setElapsed(0);
    setStepsDone(0);
    setStepsTotal(script.length);

    const t0 = performance.now();
    const ticker = window.setInterval(() => {
      setElapsed((performance.now() - t0) / 1000);
    }, 100);

    let doneWeight = 0;

    for (let i = 0; i < script.length; i++) {
      const step = script[i];
      const delay = step.weight * BASE_MS * mult;

      // wait for the step delay in small chunks (progress feedback)
      let waited = 0;
      while (waited < delay) {
        const chunk = Math.min(70, delay - waited);
        await sleep(chunk);
        if (runIdRef.current !== runId) {
          window.clearInterval(ticker);
          return;
        }
        waited += chunk;
        setProgress(
          (doneWeight + (waited / delay) * step.weight) / totalWeight,
        );
      }

      if (step.typing) {
        // animate this line char by char
        const id = lineIdRef.current++;
        setLines((prev) => [
          ...prev,
          { id, tag: step.tag, level: step.level, text: "", ts: logTimestamp() },
        ]);
        for (let c = 1; c <= step.text.length; c++) {
          await sleep(CHAR_MS);
          if (runIdRef.current !== runId) {
            window.clearInterval(ticker);
            return;
          }
          const slice = step.text.slice(0, c);
          setLines((prev) =>
            prev.map((l) => (l.id === id ? { ...l, text: slice } : l)),
          );
          setProgress(
            (doneWeight + (c / step.text.length) * step.weight) / totalWeight,
          );
        }
      } else {
        pushLine(step.tag, step.level, step.text);
        await sleep(40);
        if (runIdRef.current !== runId) {
          window.clearInterval(ticker);
          return;
        }
      }

      doneWeight += step.weight;
      setStepsDone(i + 1);
      setProgress(doneWeight / totalWeight);
    }

    window.clearInterval(ticker);
    if (runIdRef.current !== runId) return;

    const finalElapsed = (performance.now() - t0) / 1000;
    setElapsed(finalElapsed);
    setStatus("success");
    toast.success("تسک با موفقیت اجرا شد", {
      description: `${platform.name} · ${action.label} — ${faDigits(script.length)} گام در ${faSeconds(finalElapsed)} ثانیه`,
    });
  };

  const statusMeta = STATUS_META[status];

  return (
    <section id="demo" className="scroll-mt-24 py-16 sm:py-20">
      <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeader
          index="۰۴"
          en="live demo"
          title="دموی زنده — تسک بسازید و اجرا کنید"
          subtitle="این دمو، بازسازی دقیق جریان کنسول ایجنت است: پلتفرم و اکشن را انتخاب کنید، پارامترها را وارد کنید و لاگ واقعی اجرا را ببینید."
        />

        <div className="mt-12 grid gap-6 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)]">
          {/* ------------------------------- form ------------------------------- */}
          <FadeIn className="h-full">
            <Card className="h-full border-zinc-800 bg-zinc-900/60">
              <CardContent className="flex h-full flex-col gap-5 p-5 sm:p-6">
                {/* platform picker */}
                <div className="space-y-2.5">
                  <Label className="text-zinc-300">انتخاب پلتفرم</Label>
                  <div className="grid grid-cols-4 gap-2">
                    {PLATFORMS.map((p) => {
                      const active = platformId === p.id;
                      return (
                        <button
                          key={p.id}
                          type="button"
                          onClick={() => selectPlatform(p.id)}
                          disabled={running}
                          aria-pressed={active}
                          className={cn(
                            "flex min-h-[60px] flex-col items-center justify-center gap-1.5 rounded-lg border px-1 py-2 text-[11px] transition-all disabled:opacity-60",
                            active
                              ? "border-emerald-500/60 bg-emerald-500/10 text-emerald-300 ring-2 ring-emerald-500/40"
                              : "border-zinc-800 bg-zinc-900/60 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200",
                          )}
                        >
                          <PlatformIcon id={p.id} className="size-5" />
                          <span>{PLATFORM_VISUALS[p.id].short}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* action */}
                <div className="space-y-2.5">
                  <Label htmlFor="demo-action" className="text-zinc-300">
                    انتخاب اکشن
                  </Label>
                  <Select
                    value={action.id}
                    onValueChange={setActionId}
                    disabled={running}
                  >
                    <SelectTrigger
                      id="demo-action"
                      className="w-full border-zinc-800 bg-zinc-950/60"
                    >
                      <SelectValue placeholder="اکشن را انتخاب کنید" />
                    </SelectTrigger>
                    <SelectContent className="border-zinc-800 bg-zinc-900">
                      <SelectGroup>
                        <SelectLabel>{platform.name}</SelectLabel>
                        {platform.actions.map((a) => (
                          <SelectItem key={a.id} value={a.id}>
                            {a.label}
                          </SelectItem>
                        ))}
                      </SelectGroup>
                    </SelectContent>
                  </Select>
                </div>

                {/* dynamic params */}
                {action.textLabel ? (
                  <div className="space-y-2">
                    <Label htmlFor="demo-text" className="text-zinc-300">
                      {action.textLabel}
                    </Label>
                    <Textarea
                      id="demo-text"
                      value={text}
                      onChange={(e) => setText(e.target.value)}
                      disabled={running}
                      rows={3}
                      dir="auto"
                      className="resize-none border-zinc-800 bg-zinc-950/60 text-sm leading-7 focus-visible:ring-emerald-500/40"
                    />
                  </div>
                ) : null}

                {action.targetLabel ? (
                  <div className="space-y-2">
                    <Label htmlFor="demo-target" className="text-zinc-300">
                      هدف ({action.targetLabel})
                    </Label>
                    <Input
                      id="demo-target"
                      value={target}
                      onChange={(e) => setTarget(e.target.value)}
                      disabled={running}
                      dir="ltr"
                      className="border-zinc-800 bg-zinc-950/60 text-left font-mono text-sm focus-visible:ring-emerald-500/40"
                    />
                  </div>
                ) : null}

                {action.needsImage ? (
                  <div className="space-y-2">
                    <Label htmlFor="demo-image" className="text-zinc-300">
                      مسیر تصویر
                    </Label>
                    <Input
                      id="demo-image"
                      value={image}
                      onChange={(e) => setImage(e.target.value)}
                      disabled={running}
                      dir="ltr"
                      className="border-zinc-800 bg-zinc-950/60 text-left font-mono text-sm focus-visible:ring-emerald-500/40"
                    />
                  </div>
                ) : null}

                {/* engine */}
                <div className="space-y-2.5">
                  <Label className="text-zinc-300">موتور اجرا</Label>
                  <div
                    role="radiogroup"
                    aria-label="انتخاب موتور اجرا"
                    className="grid grid-cols-2 gap-2"
                  >
                    <button
                      type="button"
                      role="radio"
                      aria-checked={engine === "browser"}
                      onClick={() => setEngine("browser")}
                      disabled={running}
                      className={cn(
                        "flex min-h-11 items-center justify-center gap-2 rounded-lg border px-3 text-xs font-medium transition-all disabled:opacity-60",
                        engine === "browser"
                          ? "border-emerald-500/60 bg-emerald-500/10 text-emerald-300 ring-2 ring-emerald-500/30"
                          : "border-zinc-800 bg-zinc-900/60 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200",
                      )}
                    >
                      <Globe className="size-4 shrink-0" aria-hidden="true" />
                      <span>موتور مرورگر</span>
                      <span className="text-[10px] text-emerald-400/80">(پیشنهادی)</span>
                    </button>
                    <button
                      type="button"
                      role="radio"
                      aria-checked={engine === "desktop"}
                      onClick={() => setEngine("desktop")}
                      disabled={running}
                      className={cn(
                        "flex min-h-11 items-center justify-center gap-2 rounded-lg border px-3 text-xs font-medium transition-all disabled:opacity-60",
                        engine === "desktop"
                          ? "border-amber-400/60 bg-amber-400/10 text-amber-300 ring-2 ring-amber-400/30"
                          : "border-zinc-800 bg-zinc-900/60 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200",
                      )}
                    >
                      <MousePointerClick className="size-4 shrink-0" aria-hidden="true" />
                      <span>موتور دسکتاپ</span>
                    </button>
                  </div>
                </div>

                {/* network issue + speed */}
                <div className="grid gap-2 sm:grid-cols-2">
                  <div className="flex items-center justify-between gap-3 rounded-lg border border-zinc-800 bg-zinc-950/40 px-3 py-2.5">
                    <div>
                      <Label htmlFor="net-issue" className="text-xs text-zinc-300">
                        خطای شبکه (retry)
                      </Label>
                      <p className="mt-0.5 text-[11px] text-zinc-500">
                        شبیه‌سازی تایم‌اوت و retry
                      </p>
                    </div>
                    <Switch
                      id="net-issue"
                      checked={networkIssue}
                      onCheckedChange={setNetworkIssue}
                      disabled={running}
                      className="data-[state=checked]:bg-emerald-500"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="demo-speed" className="text-xs text-zinc-300">
                      سرعت نمایش
                    </Label>
                    <Select
                      value={speed}
                      onValueChange={(v) => setSpeed(v as SpeedId)}
                      disabled={running}
                    >
                      <SelectTrigger
                        id="demo-speed"
                        className="h-10 w-full border-zinc-800 bg-zinc-950/60"
                      >
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="border-zinc-800 bg-zinc-900">
                        {(Object.keys(SPEEDS) as SpeedId[]).map((id) => (
                          <SelectItem key={id} value={id}>
                            {SPEEDS[id].label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* actions */}
                <div className="mt-auto flex flex-col gap-2 border-t border-zinc-800/70 pt-4 sm:flex-row">
                  <Button
                    onClick={run}
                    disabled={running}
                    className="h-12 flex-1 bg-emerald-500 text-zinc-950 hover:bg-emerald-400"
                  >
                    <Play className="size-4" aria-hidden="true" />
                    اجرای تسک
                  </Button>
                  {running ? (
                    <Button
                      onClick={stop}
                      variant="outline"
                      className="h-12 border-amber-400/40 bg-transparent text-amber-300 hover:bg-amber-400/10"
                    >
                      <Square className="size-4" aria-hidden="true" />
                      توقف
                    </Button>
                  ) : null}
                  <Button
                    onClick={clear}
                    variant="ghost"
                    className="h-12 text-zinc-400 hover:bg-red-500/10 hover:text-red-300"
                  >
                    <Trash2 className="size-4" aria-hidden="true" />
                    پاک کردن
                  </Button>
                </div>
              </CardContent>
            </Card>
          </FadeIn>

          {/* ----------------------------- terminal ----------------------------- */}
          <FadeIn delay={0.1} className="h-full">
            <div className="flex h-full flex-col">
              <TerminalWindow title="parsagent — live run" className="flex-1">
                {/* status bar */}
                <div
                  dir="rtl"
                  className="flex flex-wrap items-center gap-x-4 gap-y-2 border-b border-zinc-800 bg-zinc-950/50 px-4 py-2.5"
                >
                  <span
                    className={cn(
                      "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-medium ring-1",
                      statusMeta.cls,
                    )}
                    role="status"
                    aria-live="polite"
                  >
                    <span
                      className={cn(
                        "size-1.5 rounded-full",
                        status === "running"
                          ? "animate-pulse bg-emerald-400"
                          : status === "success"
                            ? "bg-zinc-900"
                            : status === "stopped"
                              ? "bg-amber-400"
                              : "bg-zinc-400",
                      )}
                      aria-hidden="true"
                    />
                    {statusMeta.label}
                  </span>
                  <span className="text-[11px] text-zinc-500">
                    گام‌ها:{" "}
                    <span dir="ltr" className="font-mono text-zinc-300">
                      {stepsDone}/{stepsTotal}
                    </span>
                  </span>
                  <span className="text-[11px] text-zinc-500">
                    زمان:{" "}
                    <span dir="ltr" className="font-mono text-zinc-300">
                      {elapsed.toFixed(1)}s
                    </span>
                  </span>
                  <div className="min-w-24 flex-1">
                    <Progress
                      value={Math.min(100, progress * 100)}
                      className="h-1.5 bg-zinc-800"
                    />
                  </div>
                </div>

                {/* log body */}
                <div
                  ref={bodyRef}
                  dir="ltr"
                  aria-label="لاگ اجرای تسک"
                  className="max-h-[420px] min-h-[300px] overflow-y-auto scrollbar-thin p-4 text-left font-mono text-[12px] leading-6 text-zinc-300 sm:text-[12.5px]"
                >
                  {lines.length === 0 ? (
                    <div className="text-zinc-600">
                      <div>
                        <span className="text-emerald-400/70">$ </span>
                        parsagent ready — build a task and press run
                      </div>
                      <div>
                        <span className="text-emerald-400/70">$ </span>
                        waiting for task definition ...
                      </div>
                    </div>
                  ) : (
                    lines.map((line) => (
                      <LogLineView
                        key={line.id}
                        ts={line.ts}
                        line={{ tag: line.tag, level: line.level, text: line.text }}
                      />
                    ))
                  )}
                </div>
              </TerminalWindow>

              {/* success banner */}
              {status === "success" ? (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 flex items-center gap-3 rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-4"
                  role="alert"
                >
                  <CheckCircle2 className="size-5 shrink-0 text-emerald-400" aria-hidden="true" />
                  <p className="text-sm leading-7 text-emerald-200">
                    تسک با موفقیت در {faSeconds(elapsed)} ثانیه اجرا شد —{" "}
                    {faDigits(stepsDone)} از {faDigits(stepsTotal)} گام
                  </p>
                </motion.div>
              ) : null}

              {status === "stopped" ? (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 flex items-center gap-3 rounded-xl border border-amber-400/40 bg-amber-400/10 p-4"
                  role="alert"
                >
                  <Square className="size-5 shrink-0 text-amber-300" aria-hidden="true" />
                  <p className="text-sm leading-7 text-amber-200">
                    اجرای تسک متوقف شد — {faDigits(stepsDone)} از {faDigits(stepsTotal)}{" "}
                    گام انجام شد.
                  </p>
                </motion.div>
              ) : null}
            </div>
          </FadeIn>
        </div>

        {/* ------------------------- recorder demo ------------------------- */}
        <FadeIn delay={0.1}>
          <div className="mt-10">
            <RecorderDemo />
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
