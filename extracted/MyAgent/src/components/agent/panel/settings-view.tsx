"use client";

// -----------------------------------------------------------------------------
// Settings — browser fallback chain, human-like pacing, proxy, gateway.
// Mirrors agent/config.json and previews it live.
// -----------------------------------------------------------------------------

import * as React from "react";
import { ArrowDown, ArrowUp, Globe2, RotateCcw, Save, Webhook, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { usePanel } from "./panel-provider";
import { CopyButton } from "@/components/agent/copy-button";
import { faDigits } from "@/components/agent/data";
import { cn } from "@/lib/utils";
import type { PanelSettings } from "@/lib/panel/types";

const ALL_CHANNELS = ["msedge", "chrome", "chromium"];

function Section({
  icon,
  title,
  hint,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="flex flex-col gap-4 rounded-xl border border-zinc-800 bg-zinc-900/50 p-5">
      <div>
        <h3 className="flex items-center gap-2 text-sm font-bold text-zinc-200">{icon}{title}</h3>
        {hint ? <p className="mt-1 text-[11px] leading-5 text-zinc-500">{hint}</p> : null}
      </div>
      {children}
    </section>
  );
}

export function SettingsView() {
  const { state, dispatch } = usePanel();
  const [draft, setDraft] = React.useState<PanelSettings | null>(null);

  React.useEffect(() => {
    if (state && !draft) setDraft(structuredClone(state.settings));
  }, [state, draft]);

  if (!state || !draft) return null;

  const set = (patch: Partial<PanelSettings>) =>
    setDraft((d) => (d ? { ...d, ...patch } : d));
  const setHuman = (patch: Partial<PanelSettings["human"]>) =>
    setDraft((d) => (d ? { ...d, human: { ...d.human, ...patch } } : d));

  const move = (i: number, dir: -1 | 1) => {
    const fb = [...draft.channelFallbacks];
    const j = i + dir;
    if (j < 0 || j >= fb.length) return;
    [fb[i], fb[j]] = [fb[j], fb[i]];
    set({ channelFallbacks: fb });
  };
  const remove = (i: number) => {
    const fb = draft.channelFallbacks.filter((_, idx) => idx !== i);
    set({ channelFallbacks: fb.length ? fb : ["msedge"] });
  };
  const add = (channel: string) => {
    if (!draft.channelFallbacks.includes(channel)) {
      set({ channelFallbacks: [...draft.channelFallbacks, channel] });
    }
  };
  const available = ALL_CHANNELS.filter((c) => !draft.channelFallbacks.includes(c));

  const configJson = JSON.stringify(
    {
      browser: {
        headless: draft.headless,
        proxy: draft.proxy || null,
        channel: draft.channelFallbacks[0] ?? null,
        channel_fallbacks: draft.channelFallbacks,
        user_data_dir: "data/profiles/main",
      },
      human: {
        enabled: draft.human.enabled,
        min_delay_s: draft.human.minDelayS,
        max_delay_s: draft.human.maxDelayS,
        typing_delay_ms: [draft.human.typingMinMs, draft.human.typingMaxMs],
      },
      gateway: {
        enabled: true,
        url: draft.gateway.url,
        token: draft.gateway.token,
      },
    },
    null,
    2,
  );

  return (
    <div className="grid items-start gap-4 xl:grid-cols-2">
      {/* -------------------------------- browser ------------------------------- */}
      <Section
        icon={<Globe2 className="size-4 text-emerald-400" aria-hidden="true" />}
        title="مرورگر — لانچر مقاوم"
        hint="ترتیب امتحان شدن کانال‌ها. روی ویندوز ۱۰/۱۱ معمولاً Edge خود سیستم کافی است و هیچ دانلودی لازم نیست."
      >
        <div className="grid gap-2">
          {draft.channelFallbacks.map((c, i) => (
            <div
              key={c}
              className="flex items-center gap-2 rounded-lg border border-zinc-800 bg-zinc-950/60 px-3 py-2"
            >
              <span
                className={cn(
                  "flex size-6 items-center justify-center rounded-full text-[10px] font-extrabold",
                  i === 0
                    ? "bg-emerald-500 text-zinc-950"
                    : "bg-zinc-800 text-zinc-400",
                )}
              >
                {faDigits(i + 1)}
              </span>
              <span dir="ltr" className="flex-1 font-mono text-xs text-zinc-200">
                {c}
                <span className="ml-2 text-[10px] text-zinc-500">
                  {i === 0 ? "— اولین تلاش" : `— اگر ${draft.channelFallbacks[i - 1]} نبود`}
                </span>
              </span>
              <div className="flex items-center gap-0.5">
                <Button
                  size="icon"
                  variant="ghost"
                  disabled={i === 0}
                  onClick={() => move(i, -1)}
                  aria-label={`جابه‌جایی ${c} به بالا`}
                  className="size-7 text-zinc-500 hover:text-emerald-300"
                >
                  <ArrowUp className="size-3.5" aria-hidden="true" />
                </Button>
                <Button
                  size="icon"
                  variant="ghost"
                  disabled={i === draft.channelFallbacks.length - 1}
                  onClick={() => move(i, 1)}
                  aria-label={`جابه‌جایی ${c} به پایین`}
                  className="size-7 text-zinc-500 hover:text-emerald-300"
                >
                  <ArrowDown className="size-3.5" aria-hidden="true" />
                </Button>
                <Button
                  size="icon"
                  variant="ghost"
                  onClick={() => remove(i)}
                  aria-label={`حذف ${c}`}
                  className="size-7 text-zinc-500 hover:text-rose-300"
                >
                  <X className="size-3.5" aria-hidden="true" />
                </Button>
              </div>
            </div>
          ))}
          {available.length > 0 ? (
            <div className="flex flex-wrap items-center gap-1.5 pt-1">
              <span className="text-[11px] text-zinc-500">افزودن:</span>
              {available.map((c) => (
                <button
                  key={c}
                  dir="ltr"
                  onClick={() => add(c)}
                  className="rounded-full border border-dashed border-zinc-700 px-2.5 py-1 font-mono text-[10px] text-zinc-400 transition-colors hover:border-emerald-500/50 hover:text-emerald-300"
                >
                  + {c}
                </button>
              ))}
            </div>
          ) : null}
        </div>

        <div className="flex items-center justify-between rounded-lg border border-zinc-800/70 bg-zinc-950/50 px-3 py-2.5">
          <Label className="text-xs text-zinc-300">اجرای بدون پنجره (headless)</Label>
          <Switch checked={draft.headless} onCheckedChange={(v) => set({ headless: v })} />
        </div>

        <div className="grid gap-1.5">
          <Label className="text-xs text-zinc-400">پروکسی (اختیاری)</Label>
          <Input
            dir="ltr"
            value={draft.proxy}
            onChange={(e) => set({ proxy: e.target.value })}
            placeholder="http://127.0.0.1:8118"
            className="border-zinc-800 bg-zinc-900/60 font-mono text-xs"
          />
        </div>
      </Section>

      {/* -------------------------------- human --------------------------------- */}
      <Section
        icon={<Webhook className="size-4 text-emerald-400" aria-hidden="true" />}
        title="رفتار انسانی"
        hint="تأخیرهای تصادفی برای کاهش ریسک شناسایی — روی دسکتاپ و مرورگر هر دو اعمال می‌شود."
      >
        <div className="flex items-center justify-between rounded-lg border border-zinc-800/70 bg-zinc-950/50 px-3 py-2.5">
          <Label className="text-xs text-zinc-300">حرکات انسانی فعال</Label>
          <Switch
            checked={draft.human.enabled}
            onCheckedChange={(v) => setHuman({ enabled: v })}
          />
        </div>

        <div className="grid gap-4 rounded-lg border border-zinc-800/70 bg-zinc-950/50 p-4">
          <div>
            <div className="mb-2 flex items-center justify-between text-[11px]">
              <span className="text-zinc-400">تأخیر کمینه بین اقدامات</span>
              <span className="font-mono text-zinc-300">
                {faDigits(draft.human.minDelayS.toFixed(2))} ثانیه
              </span>
            </div>
            <Slider
              dir="ltr"
              value={[draft.human.minDelayS]}
              min={0.05}
              max={3}
              step={0.05}
              onValueChange={([v]) => setHuman({ minDelayS: v })}
            />
          </div>
          <div>
            <div className="mb-2 flex items-center justify-between text-[11px]">
              <span className="text-zinc-400">تأخیر بیشینه بین اقدامات</span>
              <span className="font-mono text-zinc-300">
                {faDigits(draft.human.maxDelayS.toFixed(2))} ثانیه
              </span>
            </div>
            <Slider
              dir="ltr"
              value={[draft.human.maxDelayS]}
              min={0.1}
              max={6}
              step={0.05}
              onValueChange={([v]) => setHuman({ maxDelayS: v })}
            />
          </div>
          <div>
            <div className="mb-2 flex items-center justify-between text-[11px]">
              <span className="text-zinc-400">فاصلهٔ تایپ (کمینه ← بیشینه)</span>
              <span className="font-mono text-zinc-300">
                {faDigits(draft.human.typingMinMs)}–{faDigits(draft.human.typingMaxMs)}ms
              </span>
            </div>
            <Slider
              dir="ltr"
              value={[draft.human.typingMinMs, draft.human.typingMaxMs]}
              min={10}
              max={200}
              step={5}
              onValueChange={([a, b]) =>
                setHuman({ typingMinMs: a, typingMaxMs: Math.max(a, b) })
              }
            />
          </div>
        </div>
      </Section>

      {/* -------------------------------- gateway ------------------------------- */}
      <Section
        icon={<Webhook className="size-4 text-emerald-400" aria-hidden="true" />}
        title="درگاه ایجنت واقعی"
        hint="این پنل به شبیه‌ساز داخلی متصل است. برای کنترل ایجنت واقعی ویندوز، در config.json درگاه را فعال و ایجنت را با دستور زیر اجرا کنید."
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="grid gap-1.5">
            <Label className="text-xs text-zinc-400">آدرس درگاه</Label>
            <Input
              dir="ltr"
              value={draft.gateway.url}
              onChange={(e) => set({ gateway: { ...draft.gateway, url: e.target.value } })}
              className="border-zinc-800 bg-zinc-900/60 font-mono text-xs"
            />
          </div>
          <div className="grid gap-1.5">
            <Label className="text-xs text-zinc-400">توکن</Label>
            <Input
              dir="ltr"
              type="password"
              value={draft.gateway.token}
              onChange={(e) => set({ gateway: { ...draft.gateway, token: e.target.value } })}
              className="border-zinc-800 bg-zinc-900/60 font-mono text-xs"
            />
          </div>
        </div>
        <div className="flex items-center gap-2 rounded-lg border border-emerald-500/25 bg-emerald-500/5 px-3 py-2.5" dir="ltr">
          <span className="flex-1 truncate font-mono text-[11px] text-emerald-300">
            python main.py gateway
          </span>
          <CopyButton text="python main.py gateway" className="size-7" />
        </div>
      </Section>

      {/* -------------------------------- preview ------------------------------- */}
      <Section
        icon={<Save className="size-4 text-emerald-400" aria-hidden="true" />}
        title="پیش‌نمایش config.json"
        hint="دقیقاً همین فایل روی ویندوز در ریشهٔ ایجنت ذخیره می‌شود."
      >
        <pre
          dir="ltr"
          className="scrollbar-thin max-h-72 overflow-auto rounded-lg border border-zinc-800 bg-zinc-950/70 p-3 font-mono text-[11px] leading-5 text-zinc-300"
        >
          {configJson}
        </pre>
        <div className="flex flex-wrap gap-2">
          <Button
            onClick={async () => {
              const res = await dispatch("saveSettings", { settings: draft });
              if (res.ok) {
                // keep draft in sync with saved state
                if (state.settings) setDraft(structuredClone(state.settings));
              }
            }}
            className="bg-emerald-500 text-zinc-950 hover:bg-emerald-400"
          >
            <Save className="size-4" aria-hidden="true" />
            ذخیرهٔ تنظیمات
          </Button>
          <Button
            variant="outline"
            onClick={() => setDraft(structuredClone(state.settings))}
            className="border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800"
          >
            <RotateCcw className="size-4" aria-hidden="true" />
            بازگردانی تغییرات
          </Button>
        </div>
      </Section>
    </div>
  );
}
