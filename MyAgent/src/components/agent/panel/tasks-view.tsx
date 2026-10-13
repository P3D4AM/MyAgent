"use client";

// -----------------------------------------------------------------------------
// Tasks — task list with live progress, scheduling and CLI equivalents.
// -----------------------------------------------------------------------------

import * as React from "react";
import {
  CalendarClock,
  ListChecks,
  Loader2,
  Play,
  Plus,
  Repeat2,
  Square,
  Trash2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { usePanel } from "./panel-provider";
import { CliHint, EmptyState, StatusBadge, faClock, faDigits } from "./widgets";
import { getPlatform, SPEEDS } from "@/components/agent/data";
import { PlatformIcon } from "@/components/agent/platform-icons";
import { cn } from "@/lib/utils";
import type { PanelTask } from "@/lib/panel/types";

function scheduleLabel(task: PanelTask): string {
  switch (task.schedule.type) {
    case "every":
      return `هر ${task.schedule.label}`;
    case "daily":
      return task.schedule.label;
    default:
      return "دستی";
  }
}

export function TasksView({
  onNewTask,
}: {
  onNewTask: (platformId?: string, actionId?: string) => void;
}) {
  const { state, dispatch } = usePanel();
  if (!state) return null;

  return (
    <div className="grid gap-4">
      {/* toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-zinc-800 bg-zinc-900/50 px-4 py-3">
        <div className="flex items-center gap-2 text-sm text-zinc-400">
          <ListChecks className="size-4 text-emerald-400" aria-hidden="true" />
          {state.tasks.length === 0
            ? "هنوز تسکی ساخته نشده است"
            : `${faDigits(state.tasks.length)} تسک · ${faDigits(state.stats.totalRuns)} اجرا`}
        </div>
        <div className="flex items-center gap-2">
          {state.tasks.length === 0 ? (
            <Button
              size="sm"
              variant="outline"
              onClick={() => void dispatch("loadSampleTasks")}
              className="h-8 border-zinc-800 bg-zinc-900/60 text-xs hover:bg-zinc-800"
            >
              <Repeat2 className="size-3.5" aria-hidden="true" />
              بارگذاری تسک‌های نمونه
            </Button>
          ) : null}
          <Button
            size="sm"
            onClick={() => onNewTask()}
            className="h-8 bg-emerald-500 text-xs text-zinc-950 hover:bg-emerald-400"
          >
            <Plus className="size-3.5" aria-hidden="true" />
            تسک جدید
          </Button>
        </div>
      </div>

      {/* list */}
      {state.tasks.length === 0 ? (
        <EmptyState
          icon={<ListChecks className="size-6" aria-hidden="true" />}
          title="تسکی وجود ندارد"
          description="با «تسک جدید» یک اکشن پلتفرمی بسازید، یا نمونه‌های آمادهٔ examples.json را بارگذاری کنید."
          action={
            <Button
              onClick={() => onNewTask()}
              className="bg-emerald-500 text-zinc-950 hover:bg-emerald-400"
            >
              <Plus className="size-4" aria-hidden="true" />
              تسک جدید
            </Button>
          }
        />
      ) : (
        <div className="grid gap-3 xl:grid-cols-2">
          {state.tasks.map((task) => {
            const platform = getPlatform(task.platformId);
            const running = task.status === "running";
            return (
              <article
                key={task.id}
                className={cn(
                  "flex flex-col gap-3 rounded-xl border bg-zinc-900/50 p-4 transition-colors",
                  running ? "border-emerald-500/40" : "border-zinc-800",
                )}
              >
                {/* head */}
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span className="flex size-10 items-center justify-center rounded-lg bg-emerald-500/10 ring-1 ring-emerald-500/30">
                      <PlatformIcon id={task.platformId} className="size-5 text-emerald-300" />
                    </span>
                    <div>
                      <div dir="ltr" className="font-mono text-xs font-bold text-zinc-200">
                        {task.name}
                      </div>
                      <div className="mt-0.5 text-[11px] text-zinc-500">
                        {platform.name} · {task.actionLabel}
                      </div>
                    </div>
                  </div>
                  <StatusBadge
                    state={
                      running ? "busy" : task.status === "done" ? "ok" : "off"
                    }
                    label={
                      running
                        ? `در حال اجرا ${faDigits(Math.round(task.progress * 100))}٪`
                        : task.status === "done"
                          ? `کامل شد (${task.lastDurationS?.toFixed(1) ?? "—"} ثانیه)`
                          : "آماده"
                    }
                  />
                </div>

                {/* progress */}
                {running ? (
                  <div>
                    <Progress value={task.progress * 100} className="h-1.5 bg-zinc-800" />
                    <div className="mt-1.5 flex items-center justify-between text-[10px] text-zinc-500">
                      <span>
                        گام {faDigits(task.currentStep)} از {faDigits(task.steps.length)}
                      </span>
                      <span dir="ltr" className="font-mono">
                        engine={task.engine} · ×{SPEEDS[task.speed]?.mult}
                      </span>
                    </div>
                  </div>
                ) : null}

                {/* meta */}
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-zinc-500">
                  <span className="inline-flex items-center gap-1">
                    <CalendarClock className="size-3.5" aria-hidden="true" />
                    {scheduleLabel(task)}
                    {task.nextRunAt ? ` · بعدی: ${faClock(task.nextRunAt)}` : null}
                  </span>
                  <span>اجراها: {faDigits(task.runCount)}</span>
                  {task.lastRunAt ? <span>آخرین: {faClock(task.lastRunAt)}</span> : null}
                </div>

                {/* actions */}
                <div className="flex items-center gap-2">
                  {running ? (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => void dispatch("stopTask", { taskId: task.id })}
                      className="h-8 border-amber-500/30 bg-amber-500/5 text-xs text-amber-300 hover:bg-amber-500/10"
                    >
                      <Square className="size-3.5" aria-hidden="true" />
                      توقف
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      onClick={() => void dispatch("runTask", { taskId: task.id })}
                      className="h-8 bg-emerald-500 text-xs text-zinc-950 hover:bg-emerald-400"
                    >
                      {task.status === "done" ? (
                        <Repeat2 className="size-3.5" aria-hidden="true" />
                      ) : (
                        <Play className="size-3.5" aria-hidden="true" />
                      )}
                      اجرا
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => void dispatch("deleteTask", { taskId: task.id })}
                    className="h-8 border-zinc-800 bg-zinc-900/60 text-xs text-rose-300 hover:bg-rose-500/10"
                  >
                    <Trash2 className="size-3.5" aria-hidden="true" />
                    حذف
                  </Button>
                  <span className="mr-auto" />
                  <span dir="ltr" className="hidden items-center gap-1 font-mono text-[10px] text-zinc-600 sm:inline-flex">
                    {running ? (
                      <Loader2 className="size-3 animate-spin" aria-hidden="true" />
                    ) : null}
                    tasks/panel.json
                  </span>
                </div>

                <CliHint command={`python main.py run tasks/panel.json -t ${task.name}`} />
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}
