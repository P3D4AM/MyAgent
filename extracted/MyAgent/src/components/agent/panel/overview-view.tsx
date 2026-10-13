"use client";

// -----------------------------------------------------------------------------
// Overview — dashboard: vitals, quick-launch, active tasks, live log tail.
// -----------------------------------------------------------------------------

import * as React from "react";
import {
  Activity,
  Camera,
  ClipboardCopy,
  Globe2,
  ListChecks,
  MousePointer2,
  Timer,
  Zap,
} from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { usePanel } from "./panel-provider";
import {
  CliHint,
  LogStream,
  MiniBar,
  StatCard,
  StatusDot,
  faClock,
  faDigits,
  faUptime,
} from "./widgets";
import { PLATFORMS, getPlatform } from "@/components/agent/data";
import { PlatformIcon } from "@/components/agent/platform-icons";
import { cn } from "@/lib/utils";

export function OverviewView({ onQuickRun }: { onQuickRun: () => void }) {
  const { state, dispatch } = usePanel();

  if (!state) return null;
  const activeTasks = state.tasks.filter((t) => t.status === "running");
  const scheduled = state.tasks.filter(
    (t) => t.schedule.type !== "manual" && t.status !== "running",
  );

  return (
    <TooltipProvider delayDuration={150}>
      <div className="grid gap-5">
        {/* stat cards */}
        <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
          <StatCard
            icon={<Timer className="size-5" aria-hidden="true" />}
            label="آپ‌تایم ایجنت"
            value={faUptime(state.system.uptimeS)}
            sub="شبیه‌ساز داخلی مرورگر"
          />
          <StatCard
            icon={<ListChecks className="size-5" aria-hidden="true" />}
            label="تسک‌ها"
            value={`${faDigits(activeTasks.length)} فعال / ${faDigits(state.tasks.length)} کل`}
            sub={`${faDigits(state.stats.totalRuns)} اجرای موفق`}
            accent="amber"
          />
          <StatCard
            icon={<Globe2 className="size-5" aria-hidden="true" />}
            label="مرورگرهای باز"
            value={faDigits(state.stats.openBrowsers)}
            sub={`${faDigits(state.stats.loggedIn)} پلتفرم لاگین‌شده`}
            accent="orange"
          />
          <StatCard
            icon={<Zap className="size-5" aria-hidden="true" />}
            label="ماکروهای ذخیره‌شده"
            value={faDigits(state.stats.macroCount)}
            sub={state.recorder.active ? "● در حال ضبط…" : "ضبط خاموش است"}
            accent="rose"
          />
        </div>

        {/* quick launch + vitals */}
        <div className="grid gap-4 lg:grid-cols-5">
          <section
            aria-label="اجرای سریع پلتفرم"
            className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 lg:col-span-3"
          >
            <div className="mb-3 flex items-center justify-between">
              <h3 className="flex items-center gap-2 text-sm font-bold text-zinc-200">
                <Zap className="size-4 text-emerald-400" aria-hidden="true" />
                اجرای سریع
              </h3>
              <span className="text-[11px] text-zinc-500">
                کلیک = باز/بستن مرورگرِ پروفایل ماندگار
              </span>
            </div>
            <div className="grid grid-cols-4 gap-2 sm:grid-cols-8 lg:grid-cols-4 xl:grid-cols-8">
              {PLATFORMS.map((p) => {
                const rt = state.platforms.find((x) => x.id === p.id);
                const running = rt?.running ?? false;
                return (
                  <Tooltip key={p.id}>
                    <TooltipTrigger asChild>
                      <button
                        onClick={() =>
                          void dispatch(running ? "closeBrowser" : "launch", { platformId: p.id })
                        }
                        aria-label={`${running ? "بستن" : "باز کردن"} مرورگر ${p.name}`}
                        className={cn(
                          "flex flex-col items-center gap-1.5 rounded-xl border p-3 transition-all",
                          running
                            ? "border-emerald-500/50 bg-emerald-500/10 hover:bg-emerald-500/15"
                            : "border-zinc-800 bg-zinc-900/60 hover:border-zinc-700 hover:bg-zinc-800/60",
                        )}
                      >
                        <span className="relative">
                          <PlatformIcon id={p.id} className="size-6 text-zinc-200" />
                          <StatusDot
                            state={running ? "ok" : rt?.loggedIn ? "warn" : "off"}
                            className="absolute -right-1 -top-1"
                          />
                        </span>
                        <span className="text-[10px] font-medium text-zinc-400">{p.short ?? p.name}</span>
                      </button>
                    </TooltipTrigger>
                    <TooltipContent side="top" className="border-zinc-800 bg-zinc-950 text-xs">
                      <div className="font-bold text-zinc-200">{p.name}</div>
                      <div dir="ltr" className="font-mono text-[10px] text-zinc-400">
                        {p.url}
                      </div>
                      <div className="mt-1 text-[10px] text-zinc-400">
                        {running
                          ? `باز است · کانال ${rt?.channel ?? "msedge"}`
                          : rt?.loggedIn
                            ? "سشن آماده — کلیک برای باز کردن"
                            : "کلیک برای باز کردن مرورگر"}
                      </div>
                    </TooltipContent>
                  </Tooltip>
                );
              })}
            </div>
            <CliHint
              className="mt-3"
              command="python main.py login instagram   # ورود و ذخیرهٔ سشن هر پلتفرم"
            />
          </section>

          {/* vitals */}
          <section
            aria-label="وضعیت سیستم"
            className="grid gap-4 rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 lg:col-span-2"
          >
            <div>
              <h3 className="mb-3 flex items-center gap-2 text-sm font-bold text-zinc-200">
                <Activity className="size-4 text-emerald-400" aria-hidden="true" />
                وضعیت سیستم (ویندوز)
              </h3>
              <div className="grid gap-3">
                <MiniBar value={state.system.cpu} label="پردازنده" />
                <MiniBar value={state.system.ram} label="حافظه" danger={85} />
                <div className="flex items-center justify-between rounded-lg border border-zinc-800/70 bg-zinc-950/50 px-3 py-2 text-[11px]">
                  <span className="flex items-center gap-1.5 text-zinc-400">
                    <MousePointer2 className="size-3.5" aria-hidden="true" />
                    موس
                  </span>
                  <span dir="ltr" className="font-mono text-zinc-300">
                    ({faDigits(state.system.mouse.x)}, {faDigits(state.system.mouse.y)})
                  </span>
                </div>
                <div className="flex items-center justify-between rounded-lg border border-zinc-800/70 bg-zinc-950/50 px-3 py-2 text-[11px]">
                  <span className="flex items-center gap-1.5 text-zinc-400">
                    <Camera className="size-3.5" aria-hidden="true" />
                    اسکرین‌شات‌ها
                  </span>
                  <span className="font-mono text-zinc-300">data/screenshots/</span>
                </div>
                <div className="flex items-center justify-between rounded-lg border border-zinc-800/70 bg-zinc-950/50 px-3 py-2 text-[11px]">
                  <span className="flex items-center gap-1.5 text-zinc-400">
                    <ClipboardCopy className="size-3.5" aria-hidden="true" />
                    کلیپ‌بورد
                  </span>
                  <span dir="ltr" className="max-w-40 truncate font-mono text-zinc-300">
                    {state.system.clipboard || "—"}
                  </span>
                </div>
              </div>
            </div>
          </section>
        </div>

        {/* active tasks + logs */}
        <div className="grid gap-4 lg:grid-cols-5">
          <section
            aria-label="تسک‌های فعال"
            className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 lg:col-span-2"
          >
            <div className="mb-3 flex items-center justify-between">
              <h3 className="flex items-center gap-2 text-sm font-bold text-zinc-200">
                <ListChecks className="size-4 text-emerald-400" aria-hidden="true" />
                در حال اجرا و زمان‌بندی
              </h3>
              <button
                onClick={onQuickRun}
                className="rounded-md bg-emerald-500/10 px-2.5 py-1 text-[11px] font-bold text-emerald-300 ring-1 ring-emerald-500/30 transition-colors hover:bg-emerald-500/20"
              >
                + اکشن جدید
              </button>
            </div>
            <div className="grid max-h-96 gap-2 overflow-y-auto pr-1 scrollbar-thin">
              {activeTasks.length === 0 && scheduled.length === 0 ? (
                <div className="rounded-lg border border-dashed border-zinc-800 px-4 py-8 text-center text-xs text-zinc-600">
                  تسکی در جریان نیست — از «اجرای سریع» یا «اکشن جدید» شروع کنید
                </div>
              ) : (
                [...activeTasks, ...scheduled].map((task) => (
                  <div
                    key={task.id}
                    className="rounded-lg border border-zinc-800/80 bg-zinc-950/50 p-3"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span dir="ltr" className="truncate font-mono text-[11px] text-zinc-300">
                        {task.name}
                      </span>
                      {task.status === "running" ? (
                        <span className="shrink-0 text-[10px] font-bold text-emerald-400">
                          {faDigits(Math.round(task.progress * 100))}٪
                        </span>
                      ) : (
                        <span className="shrink-0 text-[10px] text-zinc-500">
                          {task.schedule.type === "every"
                            ? `هر ${task.schedule.label}`
                            : task.schedule.type === "daily"
                              ? task.schedule.label
                              : ""}
                        </span>
                      )}
                    </div>
                    {task.status === "running" ? (
                      <Progress value={task.progress * 100} className="mt-2 h-1.5 bg-zinc-800" />
                    ) : (
                      <div className="mt-1 text-[10px] text-zinc-500">
                        {task.nextRunAt
                          ? `اجرای بعدی: ${faClock(task.nextRunAt)}`
                          : getPlatform(task.platformId).name}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </section>

          <section
            aria-label="جریان لاگ"
            className="flex flex-col rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 lg:col-span-3"
          >
            <div className="mb-3 flex items-center justify-between">
              <h3 className="flex items-center gap-2 text-sm font-bold text-zinc-200">
                <Activity className="size-4 text-emerald-400" aria-hidden="true" />
                جریان زندهٔ لاگ
              </h3>
              <span className="text-[11px] text-zinc-500">
                {faDigits(state.stats.logCount)} خط · به‌روزرسانی خودکار
              </span>
            </div>
            <LogStream logs={state.logs.slice(-60)} className="max-h-96 flex-1" />
          </section>
        </div>
      </div>
    </TooltipProvider>
  );
}
