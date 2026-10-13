"use client";

// -----------------------------------------------------------------------------
// System — desktop automation: screenshot, clipboard, apps, hotkeys,
// typing, clicking, waits, notifications.
// -----------------------------------------------------------------------------

import * as React from "react";
import {
  Bell,
  ClipboardCopy,
  ClipboardPaste,
  Copy,
  Keyboard,
  Lock,
  MousePointerClick,
  Monitor,
  Rocket,
  Timer,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { usePanel } from "./panel-provider";
import { CliHint, StatusBadge, faDigits } from "./widgets";
import { cn } from "@/lib/utils";

function Card({
  icon,
  title,
  hint,
  children,
  className,
}: {
  icon: React.ReactNode;
  title: string;
  hint?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={cn("flex flex-col gap-3 rounded-xl border border-zinc-800 bg-zinc-900/50 p-4", className)}>
      <div>
        <h3 className="flex items-center gap-2 text-sm font-bold text-zinc-200">{icon}{title}</h3>
        {hint ? <p className="mt-1 text-[11px] leading-5 text-zinc-500">{hint}</p> : null}
      </div>
      {children}
    </section>
  );
}

const HOTKEY_PRESETS: Array<{ keys: string[]; label: string }> = [
  { keys: ["win", "r"], label: "پنجرهٔ Run" },
  { keys: ["ctrl", "c"], label: "کپی" },
  { keys: ["ctrl", "v"], label: "چسباندن" },
  { keys: ["ctrl", "shift", "esc"], label: "مدیریت وظایف" },
  { keys: ["alt", "tab"], label: "سوییچ پنجره" },
  { keys: ["win", "d"], label: "دسکتاپ" },
];

export function SystemView() {
  const { state, dispatch } = usePanel();
  const [app, setApp] = React.useState("notepad");
  const [typeText, setTypeText] = React.useState("متن نمونه برای تایپ خودکار…");
  const [clickX, setClickX] = React.useState("960");
  const [clickY, setClickY] = React.useState("540");
  const [clipboard, setClipboard] = React.useState("");
  const [notifyMsg, setNotifyMsg] = React.useState("اجرا به پایان رسید ✅");
  const [lastShot, setLastShot] = React.useState<string | null>(null);
  const [readResult, setReadResult] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (state) setClipboard(state.system.clipboard);
  }, [state?.system.clipboard]);

  if (!state) return null;

  return (
    <div className="grid gap-4 xl:grid-cols-2">
      {/* screenshot */}
      <Card
        icon={<Monitor className="size-4 text-emerald-400" aria-hidden="true" />}
        title="اسکرین‌شات"
        hint="تصویر کامل صفحه در data/screenshots ذخیره می‌شود (mss)."
      >
        <Button
          onClick={async () => {
            const res = await dispatch("systemAction", { kind: "screenshot" });
            const path = (res.data as { path?: string } | undefined)?.path;
            if (path) setLastShot(path);
          }}
          className="bg-emerald-500 text-zinc-950 hover:bg-emerald-400"
        >
          گرفتن اسکرین‌شات
        </Button>
        {lastShot ? (
          <div dir="ltr" className="truncate rounded-lg border border-zinc-800 bg-zinc-950/70 px-3 py-2 font-mono text-[11px] text-emerald-300">
            ✓ {lastShot}
          </div>
        ) : null}
      </Card>

      {/* clipboard */}
      <Card
        icon={<ClipboardCopy className="size-4 text-emerald-400" aria-hidden="true" />}
        title="کلیپ‌بورد"
        hint="خواندن و نوشتن کلیپ‌بورد ویندوز با pyperclip."
      >
        <div className="grid gap-2">
          <Textarea
            value={clipboard}
            onChange={(e) => setClipboard(e.target.value)}
            rows={2}
            dir="ltr"
            className="resize-none border-zinc-800 bg-zinc-900/60 font-mono text-xs"
          />
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              onClick={() => void dispatch("systemAction", { kind: "clipboardWrite", text: clipboard })}
              className="h-8 bg-emerald-500 text-xs text-zinc-950 hover:bg-emerald-400"
            >
              <Copy className="size-3.5" aria-hidden="true" />
              نوشتن در کلیپ‌بورد
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={async () => {
                const res = await dispatch("systemAction", { kind: "clipboardRead" });
                const text = (res.data as { text?: string } | undefined)?.text;
                if (text !== undefined) setReadResult(text);
              }}
              className="h-8 border-zinc-800 bg-zinc-900/60 text-xs hover:bg-zinc-800"
            >
              <ClipboardPaste className="size-3.5" aria-hidden="true" />
              خواندن
            </Button>
          </div>
          {readResult !== null ? (
            <div dir="ltr" className="truncate rounded-lg border border-zinc-800 bg-zinc-950/70 px-3 py-2 font-mono text-[11px] text-zinc-300">
              {readResult || "— empty —"}
            </div>
          ) : null}
        </div>
      </Card>

      {/* open app */}
      <Card
        icon={<Rocket className="size-4 text-emerald-400" aria-hidden="true" />}
        title="باز کردن برنامه"
        hint="فعال‌سازی پنجرهٔ برنامه با os.startfile و انتقال فوکوس."
      >
        <div className="flex gap-2">
          <Input
            dir="ltr"
            value={app}
            onChange={(e) => setApp(e.target.value)}
            placeholder="notepad / chrome / calc"
            className="border-zinc-800 bg-zinc-900/60 font-mono text-xs"
          />
          <Button
            onClick={() => void dispatch("systemAction", { kind: "openApp", app })}
            className="shrink-0 bg-emerald-500 text-zinc-950 hover:bg-emerald-400"
          >
            اجرا
          </Button>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {["notepad", "calc", "chrome", "explorer"].map((a) => (
            <button
              key={a}
              onClick={() => setApp(a)}
              dir="ltr"
              className="rounded-full border border-zinc-800 bg-zinc-900/60 px-2.5 py-1 font-mono text-[10px] text-zinc-400 transition-colors hover:border-emerald-500/50 hover:text-emerald-300"
            >
              {a}
            </button>
          ))}
        </div>
      </Card>

      {/* hotkeys */}
      <Card
        icon={<Keyboard className="size-4 text-emerald-400" aria-hidden="true" />}
        title="هاتکی‌ها"
        hint="ارسال ترکیب کلید با PyAutoGUI و تأخیر انسانی."
      >
        <div className="flex flex-wrap gap-1.5">
          {HOTKEY_PRESETS.map((hk) => (
            <button
              key={hk.keys.join("+")}
              onClick={() => void dispatch("systemAction", { kind: "hotkey", keys: hk.keys })}
              className="group flex flex-col items-center gap-1 rounded-lg border border-zinc-800 bg-zinc-900/60 px-3 py-2 transition-colors hover:border-emerald-500/50 hover:bg-emerald-500/5"
            >
              <kbd dir="ltr" className="font-mono text-[11px] font-bold text-zinc-300 group-hover:text-emerald-300">
                {hk.keys.join("+")}
              </kbd>
              <span className="text-[10px] text-zinc-500">{hk.label}</span>
            </button>
          ))}
        </div>
      </Card>

      {/* type text */}
      <Card
        icon={<Keyboard className="size-4 text-emerald-400" aria-hidden="true" />}
        title="تایپ متن"
        hint={`تایپ نویسه‌به‌نویسه با ${faDigits(state.settings.human.typingMinMs)}–${faDigits(state.settings.human.typingMaxMs)} میلی‌ثانیه فاصله.`}
      >
        <div className="grid gap-2">
          <Textarea
            value={typeText}
            onChange={(e) => setTypeText(e.target.value)}
            rows={2}
            className="resize-none border-zinc-800 bg-zinc-900/60 text-sm"
          />
          <Button
            size="sm"
            onClick={() => void dispatch("systemAction", { kind: "typeText", text: typeText })}
            className="h-8 w-fit bg-emerald-500 text-xs text-zinc-950 hover:bg-emerald-400"
          >
            تایپ کن
          </Button>
        </div>
      </Card>

      {/* click at */}
      <Card
        icon={<MousePointerClick className="size-4 text-emerald-400" aria-hidden="true" />}
        title="کلیک در مختصات"
        hint="حرکت موس با jitter انسانی و کلیک — failsafe در گوشهٔ صفحه فعال است."
      >
        <div className="flex items-end gap-2">
          <div className="grid flex-1 gap-1.5">
            <Label className="text-[10px] text-zinc-500">X</Label>
            <Input
              dir="ltr"
              type="number"
              value={clickX}
              onChange={(e) => setClickX(e.target.value)}
              className="border-zinc-800 bg-zinc-900/60 font-mono text-xs"
            />
          </div>
          <div className="grid flex-1 gap-1.5">
            <Label className="text-[10px] text-zinc-500">Y</Label>
            <Input
              dir="ltr"
              type="number"
              value={clickY}
              onChange={(e) => setClickY(e.target.value)}
              className="border-zinc-800 bg-zinc-900/60 font-mono text-xs"
            />
          </div>
          <Button
            size="sm"
            onClick={() =>
              void dispatch("systemAction", {
                kind: "clickAt",
                x: Number(clickX),
                y: Number(clickY),
              })
            }
            className="mb-0.5 h-9 bg-emerald-500 text-xs text-zinc-950 hover:bg-emerald-400"
          >
            کلیک
          </Button>
        </div>
        <div className="flex items-center justify-between rounded-lg border border-zinc-800/70 bg-zinc-950/50 px-3 py-2 text-[11px]">
          <span className="text-zinc-500">موقعیت فعلی موس (زنده)</span>
          <span dir="ltr" className="font-mono text-zinc-300">
            ({faDigits(state.system.mouse.x)}, {faDigits(state.system.mouse.y)})
          </span>
        </div>
      </Card>

      {/* notify + wait + lock */}
      <Card
        icon={<Bell className="size-4 text-emerald-400" aria-hidden="true" />}
        title="اعلان و ابزارهای دیگر"
        hint="اعلان toast ویندوز با plyer، انتظار و قفل صفحه."
      >
        <div className="grid gap-2">
          <div className="flex gap-2">
            <Input
              value={notifyMsg}
              onChange={(e) => setNotifyMsg(e.target.value)}
              className="border-zinc-800 bg-zinc-900/60 text-sm"
              placeholder="متن اعلان…"
            />
            <Button
              size="sm"
              onClick={() =>
                void dispatch("systemAction", { kind: "notify", message: notifyMsg })
              }
              className="shrink-0 bg-emerald-500 text-xs text-zinc-950 hover:bg-emerald-400"
            >
              ارسال
            </Button>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => void dispatch("systemAction", { kind: "wait", seconds: 3 })}
              className="h-8 border-zinc-800 bg-zinc-900/60 text-xs hover:bg-zinc-800"
            >
              <Timer className="size-3.5" aria-hidden="true" />
              ۳ ثانیه انتظار
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => void dispatch("systemAction", { kind: "lock" })}
              className="h-8 border-zinc-800 bg-zinc-900/60 text-xs text-rose-300 hover:bg-rose-500/10"
            >
              <Lock className="size-3.5" aria-hidden="true" />
              قفل صفحه (win+l)
            </Button>
          </div>
        </div>
      </Card>

      {/* live status */}
      <Card
        icon={<Monitor className="size-4 text-emerald-400" aria-hidden="true" />}
        title="محیط دسکتاپ"
        className="xl:col-span-2"
        hint="وضعیت زندهٔ موتور دسکتاپ."
      >
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          <StatusBadge state="ok" label="failsafe فعال (گوشه)" />
          <StatusBadge state={state.settings.human.enabled ? "ok" : "warn"} label={state.settings.human.enabled ? "حرکات انسانی روشن" : "حرکات انسانی خاموش"} />
          <StatusBadge state="ok" label={`رزولوشن ${faDigits(state.system.resolution.w)}×${faDigits(state.system.resolution.h)}`} />
          <StatusBadge state={state.recorder.active ? "busy" : "off"} label={state.recorder.active ? "ضبط ورودی فعال" : "ضبط ورودی خاموش"} />
        </div>
        <CliHint command="python main.py demo   # تست سریع موتور مرورگر و دسکتاپ" />
      </Card>
    </div>
  );
}
