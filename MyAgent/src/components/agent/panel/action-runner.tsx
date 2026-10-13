"use client";

// -----------------------------------------------------------------------------
// ActionRunner — dialog for building & launching a platform task.
// Handles the login gate (per-platform persistent session) before allowing
// the action form, and previews the equivalent CLI command.
// -----------------------------------------------------------------------------

import * as React from "react";
import { Loader2, Play, Plus, ShieldCheck, Wand2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { usePanel } from "./panel-provider";
import { PLATFORMS, SPEEDS, faDigits, type EngineId, type SpeedId } from "@/components/agent/data";
import { PlatformIcon } from "@/components/agent/platform-icons";
import { cn } from "@/lib/utils";
import { CliHint } from "./widgets";
import type { ScheduleSpec } from "@/lib/panel/types";

const SCHEDULE_OPTIONS: Array<{ value: string; label: string; spec: ScheduleSpec }> = [
  { value: "manual", label: "بدون زمان‌بندی (دستی)", spec: { type: "manual" } },
  {
    value: "every-5m",
    label: "هر ۵ دقیقه",
    spec: { type: "every", seconds: 300, label: "۵ دقیقه" },
  },
  {
    value: "every-30m",
    label: "هر ۳۰ دقیقه",
    spec: { type: "every", seconds: 1800, label: "۳۰ دقیقه" },
  },
  {
    value: "every-2h",
    label: "هر ۲ ساعت",
    spec: { type: "every", seconds: 7200, label: "۲ ساعت" },
  },
  { value: "daily-0930", label: "هر روز ساعت ۰۹:۳۰", spec: { type: "daily", at: "09:30", label: "هر روز ۰۹:۳۰" } },
];

export interface ActionRunnerOpenOptions {
  platformId?: string;
  actionId?: string;
}

export function ActionRunner({
  open,
  onOpenChange,
  options,
  onCreated,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  options: ActionRunnerOpenOptions;
  onCreated?: () => void;
}) {
  const { state, dispatch } = usePanel();

  const [platformId, setPlatformId] = React.useState(options.platformId ?? "instagram");
  const [actionId, setActionId] = React.useState(options.actionId ?? "");
  const [text, setText] = React.useState("سلام! این پیام خودکار از پارس‌ایجنت است 🤖");
  const [target, setTarget] = React.useState("");
  const [image, setImage] = React.useState("assets/photo.jpg");
  const [engine, setEngine] = React.useState<EngineId>("browser");
  const [speed, setSpeed] = React.useState<SpeedId>("normal");
  const [scheduleValue, setScheduleValue] = React.useState("manual");
  const [busy, setBusy] = React.useState(false);

  const platform = PLATFORMS.find((p) => p.id === platformId) ?? PLATFORMS[0];
  const runtime = state?.platforms.find((p) => p.id === platformId);
  const action =
    platform.actions.find((a) => a.id === actionId) ?? platform.actions[0];

  // reset action when platform changes
  React.useEffect(() => {
    if (!platform.actions.some((a) => a.id === actionId)) {
      setActionId(platform.actions[0].id);
    }
  }, [platformId, platform, actionId]);

  React.useEffect(() => {
    if (open && options.platformId) setPlatformId(options.platformId);
    if (open && options.actionId) setActionId(options.actionId);
    if (open) setBusy(false);
  }, [open, options.platformId, options.actionId]);

  const schedule =
    SCHEDULE_OPTIONS.find((s) => s.value === scheduleValue)?.spec ?? { type: "manual" };
  const needsLoginGate = engine === "browser" && runtime && !runtime.loggedIn && !runtime.loggingIn;

  const loginProgress = React.useMemo(() => {
    if (!runtime?.loggingIn || !runtime.loginStartedAt) return 0;
    const elapsed = Date.now() - runtime.loginStartedAt;
    return Math.min(97, Math.round((elapsed / runtime.loginDurationMs) * 100));
  }, [runtime]);

  const cliCommand = React.useMemo(() => {
    const name = `${platformId}_${action.id}`;
    const parts = ["python main.py run tasks/panel.json", "-t", name];
    if (engine === "desktop") parts.push("# engine=desktop");
    return parts.join(" ");
  }, [platformId, action.id, engine]);

  const submit = async (runNow: boolean) => {
    setBusy(true);
    const res = await dispatch("createTask", {
      platformId,
      actionId: action.id,
      engine,
      speed,
      schedule,
      text,
      target,
      image,
      runNow,
    });
    setBusy(false);
    if (res.ok) {
      onOpenChange(false);
      onCreated?.();
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] w-[min(94vw,44rem)] overflow-y-auto border-zinc-800 bg-zinc-950 p-0 text-zinc-100">
        <DialogHeader className="border-b border-zinc-800 px-5 py-4">
          <DialogTitle className="flex items-center gap-2 text-base">
            <Wand2 className="size-4 text-emerald-400" aria-hidden="true" />
            اجرای اکشن پلتفرمی
          </DialogTitle>
          <DialogDescription className="text-xs leading-6 text-zinc-400">
            یک تسک واقعی پارس‌ایجنت می‌سازد؛ معادل کامل آن در ترمینال هم نمایش داده می‌شود.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 px-5 py-4">
          {/* platform + action */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="grid gap-1.5">
              <Label className="text-xs text-zinc-400">پلتفرم</Label>
              <Select value={platformId} onValueChange={setPlatformId}>
                <SelectTrigger className="w-full border-zinc-800 bg-zinc-900/60">
                  <span className="flex items-center gap-2">
                    <PlatformIcon id={platformId} className="size-4 text-emerald-400" />
                    <SelectValue />
                  </span>
                </SelectTrigger>
                <SelectContent className="border-zinc-800 bg-zinc-950">
                  {PLATFORMS.map((p) => (
                    <SelectItem key={p.id} value={p.id}>
                      <span className="flex items-center gap-2">
                        <PlatformIcon id={p.id} className="size-4" />
                        {p.name}
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label className="text-xs text-zinc-400">اکشن</Label>
              <Select value={action.id} onValueChange={setActionId}>
                <SelectTrigger className="w-full border-zinc-800 bg-zinc-900/60">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="border-zinc-800 bg-zinc-950">
                  {platform.actions.map((a) => (
                    <SelectItem key={a.id} value={a.id}>
                      {a.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* login gate */}
          {runtime?.loggingIn ? (
            <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4">
              <div className="flex items-center gap-2 text-xs font-bold text-amber-300">
                <Loader2 className="size-4 animate-spin" aria-hidden="true" />
                در انتظار ورود شما در پنجرهٔ مرورگر…
              </div>
              <Progress value={loginProgress} className="mt-3 h-1.5 bg-zinc-800" />
              <p className="mt-2 text-[11px] leading-5 text-amber-200/70">
                سشن به‌محض ورود، در پروفایل ماندگار
                <span dir="ltr" className="mx-1 font-mono">
                  {runtime.profile}
                </span>
                ذخیره می‌شود — دفعهٔ بعد بدون لاگین.
              </p>
            </div>
          ) : needsLoginGate ? (
            <Alert className="border-amber-500/30 bg-amber-500/5 text-amber-200">
              <ShieldCheck className="size-4 text-amber-400" aria-hidden="true" />
              <AlertTitle className="text-xs font-bold">ورود لازم است</AlertTitle>
              <AlertDescription className="mt-1 text-[11px] leading-5 text-amber-200/80">
                برای {platform.name} هنوز سشنی ذخیره نشده. اول وارد شوید تا کوکی‌ها در پروفایل
                ماندگار ذخیره شوند.
              </AlertDescription>
              <Button
                size="sm"
                onClick={() => void dispatch("login", { platformId })}
                className="mt-2 h-8 bg-amber-400 text-zinc-950 hover:bg-amber-300"
              >
                شروع فرایند ورود
              </Button>
            </Alert>
          ) : null}

          {/* params */}
          {!(runtime?.loggingIn || needsLoginGate) ? (
            <>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="grid gap-1.5">
                  <Label className="text-xs text-zinc-400">موتور اجرا</Label>
                  <div className="grid grid-cols-2 gap-1 rounded-lg border border-zinc-800 bg-zinc-900/60 p-1">
                    {(
                      [
                        { id: "browser", label: "مرورگر (Playwright)" },
                        { id: "desktop", label: "دسکتاپ (موس/کیبورد)" },
                      ] as Array<{ id: EngineId; label: string }>
                    ).map((opt) => (
                      <button
                        key={opt.id}
                        type="button"
                        onClick={() => setEngine(opt.id)}
                        className={cn(
                          "rounded-md px-2 py-1.5 text-[11px] font-bold transition-colors",
                          engine === opt.id
                            ? "bg-emerald-500 text-zinc-950"
                            : "text-zinc-400 hover:text-zinc-200",
                        )}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="grid gap-1.5">
                  <Label className="text-xs text-zinc-400">سرعت انسانی</Label>
                  <Select value={speed} onValueChange={(v) => setSpeed(v as SpeedId)}>
                    <SelectTrigger className="w-full border-zinc-800 bg-zinc-900/60">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="border-zinc-800 bg-zinc-950">
                      {Object.entries(SPEEDS).map(([id, s]) => (
                        <SelectItem key={id} value={id}>
                          {s.label} (×{faDigits(s.mult)})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {action.textLabel ? (
                <div className="grid gap-1.5">
                  <Label className="text-xs text-zinc-400">{action.textLabel}</Label>
                  <Textarea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    rows={2}
                    className="resize-none border-zinc-800 bg-zinc-900/60 text-sm"
                    placeholder="متن را وارد کنید…"
                  />
                </div>
              ) : null}
              <div className="grid gap-4 sm:grid-cols-2">
                {action.targetLabel ? (
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-zinc-400">{action.targetLabel}</Label>
                    <Input
                      dir="ltr"
                      value={target}
                      onChange={(e) => setTarget(e.target.value)}
                      className="border-zinc-800 bg-zinc-900/60 text-sm"
                      placeholder="@username"
                    />
                  </div>
                ) : null}
                {action.needsImage ? (
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-zinc-400">مسیر تصویر</Label>
                    <Input
                      dir="ltr"
                      value={image}
                      onChange={(e) => setImage(e.target.value)}
                      className="border-zinc-800 bg-zinc-900/60 font-mono text-xs"
                      placeholder="assets/photo.jpg"
                    />
                  </div>
                ) : null}
              </div>

              <div className="grid gap-1.5">
                <Label className="text-xs text-zinc-400">زمان‌بندی</Label>
                <Select value={scheduleValue} onValueChange={setScheduleValue}>
                  <SelectTrigger className="w-full border-zinc-800 bg-zinc-900/60">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="border-zinc-800 bg-zinc-950">
                    {SCHEDULE_OPTIONS.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <CliHint command={cliCommand} />
            </>
          ) : null}
        </div>

        <DialogFooter className="flex-row-reverse gap-2 border-t border-zinc-800 px-5 py-4">
          <Button
            disabled={busy || !!(runtime?.loggingIn || needsLoginGate)}
            onClick={() => void submit(true)}
            className="h-10 bg-emerald-500 text-zinc-950 hover:bg-emerald-400"
          >
            {busy ? (
              <Loader2 className="size-4 animate-spin" aria-hidden="true" />
            ) : (
              <Play className="size-4" aria-hidden="true" />
            )}
            {schedule.type === "manual" ? "اجرا" : "اجرا + زمان‌بندی"}
          </Button>
          {schedule.type !== "manual" ? (
            <Button
              variant="outline"
              disabled={busy || !!(runtime?.loggingIn || needsLoginGate)}
              onClick={() => void submit(false)}
              className="h-10 border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800"
            >
              <Plus className="size-4" aria-hidden="true" />
              فقط بساز
            </Button>
          ) : null}
          <Button
            variant="ghost"
            onClick={() => onOpenChange(false)}
            className="h-10 text-zinc-400 hover:text-zinc-200"
          >
            انصراف
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
