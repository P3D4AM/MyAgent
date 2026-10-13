"use client";

// -----------------------------------------------------------------------------
// ControlPanel — the ParsAgent web mission-control shell.
// Wraps itself in PanelProvider (polling + dispatch) and routes between views.
// -----------------------------------------------------------------------------

import * as React from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Activity,
  ArrowRight,
  Bot,
  Brain,
  Globe2,
  LayoutDashboard,
  ListChecks,
  MonitorCog,
  MousePointerClick,
  ScrollText,
  Settings2,
  Signal,
  SignalHigh,
  Wand2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { PanelProvider, usePanel } from "./panel-provider";
import { OverviewView } from "./overview-view";
import { PlatformsView } from "./platforms-view";
import { TasksView } from "./tasks-view";
import { AiView } from "./ai-view";
import { RecorderView } from "./recorder-view";
import { SystemView } from "./system-view";
import { LogsView } from "./logs-view";
import { SettingsView } from "./settings-view";
import { ActionRunner, type ActionRunnerOpenOptions } from "./action-runner";
import { StatusDot, faUptime } from "./widgets";
import { faDigits } from "@/components/agent/data";
import { cn } from "@/lib/utils";

type ViewId =
  | "overview"
  | "platforms"
  | "tasks"
  | "ai"
  | "recorder"
  | "system"
  | "logs"
  | "settings";

const NAV: Array<{ id: ViewId; label: string; icon: React.ReactNode }> = [
  { id: "overview", label: "نمای کلی", icon: <LayoutDashboard className="size-4" aria-hidden="true" /> },
  { id: "platforms", label: "پلتفرم‌ها", icon: <Globe2 className="size-4" aria-hidden="true" /> },
  { id: "tasks", label: "وظایف", icon: <ListChecks className="size-4" aria-hidden="true" /> },
  { id: "ai", label: "هوش مصنوعی", icon: <Brain className="size-4" aria-hidden="true" /> },
  { id: "recorder", label: "ضبط ماکرو", icon: <MousePointerClick className="size-4" aria-hidden="true" /> },
  { id: "system", label: "اتوماسیون سیستم", icon: <MonitorCog className="size-4" aria-hidden="true" /> },
  { id: "logs", label: "لاگ‌ها", icon: <ScrollText className="size-4" aria-hidden="true" /> },
  { id: "settings", label: "تنظیمات", icon: <Settings2 className="size-4" aria-hidden="true" /> },
];

const VIEW_META: Record<ViewId, { title: string; desc: string }> = {
  overview: { title: "نمای کلی", desc: "وضعیت لحظه‌ای ایجنت، اجرای سریع و جریان لاگ" },
  platforms: { title: "پلتفرم‌ها", desc: "مرورگر، سشن و پروفایل ماندگار هر پلتفرم" },
  tasks: { title: "وظایف", desc: "ساخت، اجرا و زمان‌بندی تسک‌ها با معادل CLI" },
  ai: { title: "هوش مصنوعی", desc: "ایجنت خودمختار — ایده بده، برنامه و محتوا و گزارش بگیر" },
  recorder: { title: "ضبط ماکرو", desc: "ضبط و بازپخش موس و کیبورد در صحنهٔ بصری" },
  system: { title: "اتوماسیون سیستم", desc: "اسکرین‌شات، کلیپ‌بورد، برنامه‌ها و هاتکی‌ها" },
  logs: { title: "لاگ‌ها", desc: "جریان کامل رخدادهای ایجنت با فیلتر" },
  settings: { title: "تنظیمات", desc: "لانچر مرورگر، رفتار انسانی و درگاه ایجنت" },
};

export function ControlPanel({ onExit }: { onExit: () => void }) {
  return (
    <PanelProvider>
      <PanelShell onExit={onExit} />
    </PanelProvider>
  );
}

function PanelShell({ onExit }: { onExit: () => void }) {
  const { state, connected } = usePanel();
  const [view, setView] = React.useState<ViewId>("overview");
  const [runnerOpen, setRunnerOpen] = React.useState(false);
  const [runnerOptions, setRunnerOptions] = React.useState<ActionRunnerOpenOptions>({});
  const mainRef = React.useRef<HTMLElement>(null);

  const openRunner = (platformId?: string, actionId?: string) => {
    setRunnerOptions({ platformId, actionId });
    setRunnerOpen(true);
  };

  const switchView = (next: ViewId) => {
    setView(next);
    mainRef.current?.scrollTo({ top: 0 });
    window.scrollTo({ top: 0 });
  };

  const meta = VIEW_META[view];

  return (
    <div className="flex min-h-screen flex-col bg-zinc-950 font-sans text-zinc-100">
      {/* ---------------------------------- top bar ------------------------------ */}
      <header className="sticky top-0 z-40 w-full border-b border-zinc-800 bg-zinc-950/85 backdrop-blur-md">
        <div className="mx-auto flex h-16 w-full max-w-[100rem] items-center justify-between gap-3 px-4 sm:px-6">
          {/* brand */}
          <div className="flex min-w-0 items-center gap-3">
            <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-emerald-500/15 ring-1 ring-emerald-500/40">
              <Bot className="size-5.5 text-emerald-400" aria-hidden="true" />
            </span>
            <div className="flex min-w-0 flex-col leading-none">
              <span className="text-base font-extrabold text-zinc-100">پنل کنترل پارس‌ایجنت</span>
              <span dir="ltr" className="mt-1 truncate font-mono text-[10px] tracking-wider text-emerald-400/80">
                PARSAGENT MISSION CONTROL
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* mode badge */}
            <TooltipProvider delayDuration={150}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span
                    className={cn(
                      "hidden items-center gap-1.5 rounded-full border px-3 py-1.5 text-[11px] font-bold sm:inline-flex",
                      connected
                        ? "border-amber-500/30 bg-amber-500/10 text-amber-300"
                        : "border-rose-500/30 bg-rose-500/10 text-rose-300",
                    )}
                  >
                    {connected ? (
                      <SignalHigh className="size-3.5" aria-hidden="true" />
                    ) : (
                      <Signal className="size-3.5" aria-hidden="true" />
                    )}
                    {connected ? "شبیه‌ساز داخلی" : "قطع"}
                  </span>
                </TooltipTrigger>
                <TooltipContent side="bottom" className="max-w-64 border-zinc-800 bg-zinc-950 text-xs leading-5">
                  این پنل به موتور شبیه‌سازی داخلی متصل است تا همهٔ قابلیت‌ها را بی‌درنگ امتحان
                  کنید. برای کنترل ایجنت واقعی ویندوز، آن را دانلود کنید و
                  <span dir="ltr" className="mx-1 font-mono text-emerald-300">python main.py gateway</span>
                  را اجرا کنید.
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>

            <Button
              onClick={() => openRunner()}
              className="h-10 bg-emerald-500 text-zinc-950 hover:bg-emerald-400"
            >
              <Wand2 className="size-4" aria-hidden="true" />
              <span className="hidden sm:inline">اجرای اکشن</span>
              <span className="sm:hidden">اکشن</span>
            </Button>

            <Button
              variant="outline"
              onClick={onExit}
              className="h-10 border-zinc-800 bg-zinc-900/60 text-xs hover:bg-zinc-800"
            >
              <ArrowRight className="size-4" aria-hidden="true" />
              <span className="hidden sm:inline">صفحهٔ معرفی</span>
            </Button>
          </div>
        </div>
      </header>

      {/* ---------------------------------- body --------------------------------- */}
      <div className="mx-auto flex w-full max-w-[100rem] flex-1">
        {/* sidebar (right in RTL) */}
        <aside className="sticky top-16 hidden h-[calc(100vh-4rem)] w-60 shrink-0 flex-col justify-between border-l border-zinc-800 bg-zinc-900/30 p-4 md:flex">
          <nav aria-label="ناوبری پنل" className="grid gap-1">
            {NAV.map((item) => {
              const active = view === item.id;
              const badge =
                item.id === "tasks" && state
                  ? state.stats.activeTasks
                  : item.id === "ai" && state
                    ? state.ai.missions.filter((m) =>
                        ["planning", "running", "wait_approval"].includes(m.status),
                      ).length
                    : item.id === "recorder" && state?.recorder.active
                      ? 1
                      : 0;
              return (
                <button
                  key={item.id}
                  onClick={() => switchView(item.id)}
                  aria-current={active ? "page" : undefined}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    active
                      ? "bg-emerald-500/10 text-emerald-300 ring-1 ring-emerald-500/30"
                      : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200",
                  )}
                >
                  {item.icon}
                  <span className="flex-1 text-right">{item.label}</span>
                  {badge > 0 ? (
                    <span className="flex size-5 items-center justify-center rounded-full bg-emerald-500 text-[10px] font-extrabold text-zinc-950">
                      {faDigits(badge)}
                    </span>
                  ) : null}
                </button>
              );
            })}
          </nav>

          {/* sidebar footer */}
          <div className="grid gap-2 rounded-xl border border-zinc-800/70 bg-zinc-950/50 p-3 text-[11px]">
            <div className="flex items-center justify-between text-zinc-500">
              <span>حالت</span>
              <span className="flex items-center gap-1 font-bold text-amber-300">
                <StatusDot state="ok" />
                شبیه‌ساز
              </span>
            </div>
            <div className="flex items-center justify-between text-zinc-500">
              <span>آپ‌تایم</span>
              <span dir="ltr" className="font-mono text-zinc-300">
                {state ? faUptime(state.system.uptimeS) : "—"}
              </span>
            </div>
            <div className="flex items-center justify-between text-zinc-500">
              <span>مرورگرهای باز</span>
              <span className="font-mono text-zinc-300">
                {state ? faDigits(state.stats.openBrowsers) : "—"}
              </span>
            </div>
          </div>
        </aside>

        {/* main */}
        <main ref={mainRef} className="min-w-0 flex-1 p-4 sm:p-6">
          {/* mobile nav */}
          <nav
            aria-label="ناوبری موبایل"
            className="scrollbar-thin -mx-1 mb-4 flex gap-1.5 overflow-x-auto px-1 pb-1 md:hidden"
          >
            {NAV.map((item) => (
              <button
                key={item.id}
                onClick={() => switchView(item.id)}
                className={cn(
                  "flex shrink-0 items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-bold transition-colors",
                  view === item.id
                    ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-300"
                    : "border-zinc-800 bg-zinc-900/60 text-zinc-400",
                )}
              >
                {item.icon}
                {item.label}
              </button>
            ))}
          </nav>

          {/* view header */}
          <div className="mb-5">
            <h1 className="text-xl font-extrabold text-zinc-100">{meta.title}</h1>
            <p className="mt-1 text-xs text-zinc-500">{meta.desc}</p>
          </div>

          {/* view content */}
          <AnimatePresence mode="wait">
            <motion.div
              key={view}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.18 }}
            >
              {view === "overview" ? <OverviewView onQuickRun={() => openRunner()} /> : null}
              {view === "platforms" ? (
                <PlatformsView onRunAction={(p, a) => openRunner(p, a)} />
              ) : null}
              {view === "tasks" ? (
                <TasksView onNewTask={(p, a) => openRunner(p, a)} />
              ) : null}
              {view === "ai" ? <AiView /> : null}
              {view === "recorder" ? <RecorderView /> : null}
              {view === "system" ? <SystemView /> : null}
              {view === "logs" ? <LogsView /> : null}
              {view === "settings" ? <SettingsView /> : null}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      {/* ---------------------------------- status bar ---------------------------- */}
      <footer className="mt-auto border-t border-zinc-800 bg-zinc-950/95">
        <div className="mx-auto flex w-full max-w-[100rem] flex-wrap items-center justify-between gap-x-6 gap-y-1 px-4 py-2.5 text-[11px] text-zinc-500 sm:px-6">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <StatusDot state={connected ? "ok" : "warn"} />
              پارس‌ایجنت v1.0.0 — شبیه‌ساز پنل
            </span>
            <span dir="ltr" className="font-mono">
              uptime {state ? faUptime(state.system.uptimeS) : "—"}
            </span>
          </div>
          <div className="flex items-center gap-4 font-mono" dir="ltr">
            <span className="flex items-center gap-1">
              <Activity className="size-3" aria-hidden="true" />
              cpu {state ? `${Math.round(state.system.cpu)}%` : "—"}
            </span>
            <span>ram {state ? `${Math.round(state.system.ram)}%` : "—"}</span>
            <span>tasks {state ? state.stats.activeTasks : 0}</span>
            <span>logs {state ? state.stats.logCount : 0}</span>
          </div>
        </div>
      </footer>

      {/* runner dialog */}
      <ActionRunner
        open={runnerOpen}
        onOpenChange={setRunnerOpen}
        options={runnerOptions}
        onCreated={() => switchView("tasks")}
      />
    </div>
  );
}
