"use client";

// -----------------------------------------------------------------------------
// AI — ایجنت خودمختار هوش مصنوعی (mirrors the desktop panel's tab-ai):
// mission composer, quick chat and live mission cards with plan/posts/log/report.
// -----------------------------------------------------------------------------

import * as React from "react";
import { motion } from "framer-motion";
import {
  Brain,
  ChevronDown,
  Clapperboard,
  ImageIcon,
  MessageCircleReply,
  MessageSquare,
  Package,
  Rocket,
  ScrollText,
  Send,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { usePanel } from "./panel-provider";
import { faDigits } from "@/components/agent/data";
import { PLATFORMS } from "@/components/agent/data";
import { cn } from "@/lib/utils";
import type { AiMission } from "@/lib/panel/types";

/** همان چهار نمونهٔ تب هوش مصنوعیِ پنل دسکتاپ. */
const AI_EXAMPLES = [
  "یک ویدیوی معرفی ۳۰ ثانیه‌ای برای فروشگاهم بساز و برای اینستاگرام زمان‌بندی کن؛ دایرکت‌ها را هم خودت جواب بده — معرفی: پیج فروش گیاهان آپارتمانی با ارسال سراسری",
  "این ۷ ایده را این هفته بگیر و برای هر کدام ۳ پست بساز؛ عکس‌ها را هم خودت با AI بساز، در تلگرام (کانال من) و توییتر منتشر کن و آخر هفته گزارش بده — ایده‌ها: آموزش عکاسی با موبایل، پشت صحنهٔ کار، معرفی محصول جدید، نظرسنجی هفتگی، داستان موفقیت مشتری، نکات سریع، تخفیف آخر هفته",
  "برای رشد پیج اینستاگرامم استراتژی فالو بچین: هر روز چند نفر و در چه ساعاتی فالو کنم؟ از هشتگ عکاسی شروع کن و برنامه‌اش را بساز",
  "برای لینکدین ۵ پست حرفه‌ای دربارهٔ تجربهٔ تیم‌سازی بساز و برای هفتهٔ آینده زمان‌بندی کن؛ فعلاً منتشر نکن",
];

const AI_TOOLS: Record<string, string> = {
  generate_content: "تولید محتوا",
  generate_image: "ساخت عکس با AI",
  generate_video: "چاپخانهٔ ویدیو",
  dm_autoreply: "پاسخ‌گوی دایرکت",
  schedule_publish: "زمان‌بندی انتشار",
  publish_now: "انتشار فوری",
  follow_strategy: "استراتژی فالو",
  wait_report: "گزارش زمان‌دار",
  report: "گزارش نهایی",
  status_check: "بررسی وضعیت",
};

const PLATFORM_FA: Record<string, string> = Object.fromEntries(
  PLATFORMS.map((p) => [p.id, p.name]),
);

const AUTONOMY_FA: Record<string, string> = {
  manual: "پیشنهادی",
  semi: "نیمه‌خودکار",
  auto: "کاملاً خودمختار",
};

const AUTONOMY_OPTIONS: Array<{ value: "manual" | "semi" | "auto"; label: string }> = [
  { value: "manual", label: "پیشنهادی — با تأیید من" },
  { value: "semi", label: "نیمه‌خودکار (توصیه)" },
  { value: "auto", label: "کاملاً خودمختار" },
];

const POST_STATUS_FA: Record<string, string> = {
  draft: "پیش‌نویس",
  scheduled: "در صف انتشار",
  published: "منتشر شد",
  failed: "ناموفق",
  needs_media: "منتظر عکس (تب رسانه‌ها)",
  no_channel: "کانال مشخص نیست",
};

const STATUS_META: Record<AiMission["status"], { label: string; cls: string }> = {
  planning: {
    label: "در حال فکر و برنامه‌ریزی…",
    cls: "border-amber-500/40 bg-amber-500/10 text-amber-300 animate-pulse",
  },
  wait_approval: {
    label: "منتظر تأیید شما",
    cls: "border-amber-500/40 bg-amber-500/10 text-amber-300 animate-pulse",
  },
  running: {
    label: "در حال اجرا",
    cls: "border-emerald-500/40 bg-emerald-500/10 text-emerald-300 animate-pulse",
  },
  paused: {
    label: "متوقف",
    cls: "border-zinc-700 bg-zinc-900/60 text-zinc-400",
  },
  waiting: {
    label: "در انتظار زمان گزارش",
    cls: "border-sky-500/40 bg-sky-500/10 text-sky-300",
  },
  completed: {
    label: "تمام شد",
    cls: "border-emerald-500/40 bg-emerald-500/10 text-emerald-300",
  },
  failed: {
    label: "ناموفق",
    cls: "border-rose-500/40 bg-rose-500/10 text-rose-300",
  },
  cancelled: {
    label: "لغو شد",
    cls: "border-zinc-700 bg-zinc-900/60 text-zinc-400",
  },
};

const LOG_LEVEL_CLS: Record<string, string> = {
  ok: "text-emerald-400/90",
  warn: "text-amber-400/90",
  error: "text-rose-400/90",
};

export function AiView() {
  const { state, dispatch } = usePanel();
  const [instruction, setInstruction] = React.useState("");
  const [chatInput, setChatInput] = React.useState("");
  const chatRef = React.useRef<HTMLDivElement>(null);

  const ai = state?.ai;

  React.useEffect(() => {
    const el = chatRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [ai?.chat.length]);

  if (!state || !ai) return null;

  const provider = ai.catalog.find((p) => p.id === ai.provider) ?? ai.catalog[0];
  const models = provider?.models ?? [];
  const providerHasKey = provider?.hasKey ?? false;

  const createMission = async () => {
    const text = instruction.trim();
    if (!text) return;
    const res = await dispatch("aiCreateMission", {
      instruction: text,
      provider: ai.provider,
      model: ai.model,
      autonomy: ai.autonomy,
    });
    if (res.ok) setInstruction("");
  };

  const sendChat = async () => {
    const text = chatInput.trim();
    if (!text) return;
    setChatInput("");
    await dispatch("aiSendChat", { content: text }, true);
  };

  return (
    <div className="grid gap-4">
      {/* header note */}
      <p className="text-xs leading-6 text-zinc-500">
        فقط <b className="text-zinc-300">ایده را بگویید</b>؛ ایجنت خودش برنامه می‌سازد، برای
        هر پلتفرم محتوا تولید می‌کند، <b className="text-zinc-300">عکس و ویدیو می‌سازد</b>،
        دایرکت‌ها را <b className="text-zinc-300">طبیعی جواب می‌دهد</b>، زمان انتشار را
        می‌چیند، استراتژی فالو را تصمیم می‌گیرد و آخر کار{" "}
        <b className="text-zinc-300">گزارش فارسی</b> می‌دهد. سرویس و مدل را همین‌جا انتخاب
        کنید — مدل‌های <b className="text-emerald-400">Z.ai (GLM)</b> اول لیست‌اند.
      </p>

      {/* --------------------- ۲.۴.۰ — media factory + dm reply demos --------------------- */}
      <VideoFactoryDemo />
      <ImageFactoryDemo />
      <DmReplyDemo />

      <div className="grid items-start gap-4 xl:grid-cols-2">
        {/* ------------------------------- composer ------------------------------ */}
        <section className="grid gap-4 rounded-xl border border-zinc-800 bg-zinc-900/50 p-5">
          <h3 className="flex items-center gap-2 text-sm font-bold text-zinc-200">
            <Rocket className="size-4 text-emerald-400" aria-hidden="true" />
            ماموریت جدید
          </h3>

          <div className="grid gap-3 sm:grid-cols-3">
            <div className="grid gap-1.5">
              <Label className="text-xs text-zinc-400">سرویس AI</Label>
              <Select
                value={ai.provider}
                onValueChange={(v) => void dispatch("aiSetProvider", { provider: v }, true)}
              >
                <SelectTrigger className="w-full border-zinc-800 bg-zinc-900/60 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="border-zinc-800 bg-zinc-950 text-xs">
                  {ai.catalog.map((p) => (
                    <SelectItem key={p.id} value={p.id} className="text-xs focus:bg-zinc-900">
                      {p.name}
                      {p.hasKey ? " ✓" : ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-1.5">
              <Label className="text-xs text-zinc-400">مدل</Label>
              <Select
                value={ai.model}
                onValueChange={(v) => void dispatch("aiSetModel", { model: v }, true)}
              >
                <SelectTrigger className="w-full border-zinc-800 bg-zinc-900/60 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="border-zinc-800 bg-zinc-950 text-xs">
                  {models.map((m) => (
                    <SelectItem key={m.id} value={m.id} className="text-xs focus:bg-zinc-900">
                      {m.name}
                      {m.tag ? ` «${m.tag}»` : ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-1.5">
              <Label className="text-xs text-zinc-400">سطح خودمختاری</Label>
              <Select
                value={ai.autonomy}
                onValueChange={(v) => void dispatch("aiSetAutonomy", { autonomy: v }, true)}
              >
                <SelectTrigger className="w-full border-zinc-800 bg-zinc-900/60 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="border-zinc-800 bg-zinc-950 text-xs">
                  {AUTONOMY_OPTIONS.map((o) => (
                    <SelectItem key={o.value} value={o.value} className="text-xs focus:bg-zinc-900">
                      {o.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid gap-1.5">
            <Label className="text-xs text-zinc-400">
              ایده یا ماموریت — فارسی، مثل حرف زدن با یک همکار
            </Label>
            <Textarea
              rows={4}
              value={instruction}
              onChange={(e) => setInstruction(e.target.value)}
              placeholder="مثلاً: این ۷ ایده را این هفته بگیر و برای هر کدام ۳ پست بساز؛ در تلگرام (کانال من) و توییتر منتشر کن و آخر هفته گزارش بده — ایده‌ها: …"
              className="min-h-24 border-zinc-800 bg-zinc-900/60 text-xs leading-6 placeholder:text-zinc-600"
            />
          </div>

          <div className="flex flex-wrap items-center gap-1.5">
            {AI_EXAMPLES.map((t, i) => (
              <button
                key={i}
                type="button"
                onClick={() => setInstruction(t)}
                title={`${t.slice(0, 120)}…`}
                className="rounded-full border border-zinc-800 bg-zinc-900/60 px-2.5 py-1 text-[11px] text-zinc-400 transition-colors hover:border-emerald-500/50 hover:text-emerald-300"
              >
                💡 نمونهٔ {faDigits(i + 1)}
              </button>
            ))}
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button
              onClick={() => void createMission()}
              disabled={!instruction.trim()}
              className="bg-emerald-500 px-6 text-sm text-zinc-950 hover:bg-emerald-400"
            >
              🚀 شروع ماموریت
            </Button>
            <span
              className={cn(
                "text-[11px]",
                providerHasKey ? "text-emerald-400" : "text-amber-400",
              )}
            >
              {providerHasKey
                ? "✓ کلید این سرویس ذخیره شده است"
                : "کلید سرویس را در تنظیمات وارد کنید"}
            </span>
          </div>
        </section>

        {/* ------------------------------- quick chat ---------------------------- */}
        <section className="grid gap-4 rounded-xl border border-zinc-800 bg-zinc-900/50 p-5">
          <h3 className="flex items-center gap-2 text-sm font-bold text-zinc-200">
            <MessageSquare className="size-4 text-emerald-400" aria-hidden="true" />
            گفتگوی سریع با مدل
          </h3>

          <div
            ref={chatRef}
            className="scrollbar-thin flex max-h-72 min-h-40 flex-col gap-2 overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-950/70 p-3"
          >
            {ai.chat.length === 0 ? (
              <span className="py-6 text-center text-xs text-zinc-600">
                سؤالتان را بپرسید — با همان مدل انتخابی بالا.
              </span>
            ) : (
              ai.chat.map((msg, i) => (
                <div
                  key={i}
                  className={cn(
                    "max-w-[88%] whitespace-pre-wrap rounded-xl border px-3.5 py-2 text-xs leading-6",
                    msg.role === "user"
                      ? "self-start rounded-tl-sm border-emerald-500/30 bg-emerald-500/10 text-emerald-100"
                      : "self-end rounded-tr-sm border-zinc-800 bg-zinc-900 text-zinc-300",
                  )}
                >
                  {msg.content}
                </div>
              ))
            )}
          </div>

          <form
            className="flex gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              void sendChat();
            }}
          >
            <Input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="سؤال، ایده یا درخواست…"
              className="h-10 border-zinc-800 bg-zinc-900/60 text-xs"
            />
            <Button
              type="submit"
              disabled={!chatInput.trim()}
              className="h-10 bg-emerald-500 text-zinc-950 hover:bg-emerald-400"
            >
              <Send className="size-4" aria-hidden="true" />
              ارسال
            </Button>
          </form>
        </section>
      </div>

      {/* ------------------------------- missions ------------------------------- */}
      <section className="grid gap-4 rounded-xl border border-zinc-800 bg-zinc-900/50 p-5">
        <div className="flex items-center justify-between gap-3">
          <h3 className="flex items-center gap-2 text-sm font-bold text-zinc-200">
            <Brain className="size-4 text-emerald-400" aria-hidden="true" />
            ماموریت‌ها
          </h3>
          <span className="inline-flex items-center rounded-full border border-zinc-800 bg-zinc-900/60 px-2.5 py-1 font-mono text-[11px] text-zinc-400">
            {faDigits(ai.missions.length)}
          </span>
        </div>

        {ai.missions.length === 0 ? (
          <p className="text-xs text-zinc-500">
            هنوز ماموریتی ساخته نشده — از فرم بالا اولین ایده‌تان را بدهید.
          </p>
        ) : (
          <div className="grid gap-3">
            {ai.missions.map((mission) => (
              <MissionCard key={mission.id} mission={mission} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* MissionCard — one mission: header, plan, posts, log, report, controls        */
/* -------------------------------------------------------------------------- */

function MissionCard({ mission }: { mission: AiMission }) {
  const { dispatch } = usePanel();
  const st = STATUS_META[mission.status] ?? STATUS_META.planning;
  const active = ["planning", "running", "wait_approval"].includes(mission.status);
  const cancellable = ["running", "planning", "paused", "waiting", "wait_approval"].includes(
    mission.status,
  );

  const control = (cmd: string) =>
    void dispatch("aiMissionControl", { missionId: mission.id, cmd });

  return (
    <motion.article
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={cn(
        "grid gap-3 rounded-xl border bg-zinc-900/40 p-4 transition-colors",
        active ? "border-emerald-500/30" : "border-zinc-800",
      )}
    >
      {/* head */}
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="truncate text-sm font-bold text-zinc-100">🎯 {mission.title}</div>
          <div dir="auto" className="mt-1 text-[11px] text-zinc-500">
            {mission.provider} / {mission.model} · خودمختاری:{" "}
            {AUTONOMY_FA[mission.autonomy] ?? mission.autonomy}
          </div>
        </div>
        <span
          className={cn(
            "inline-flex shrink-0 items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-medium",
            st.cls,
          )}
        >
          {st.label}
        </span>
      </div>

      {/* analysis / instruction */}
      {mission.plan?.analysis ? (
        <p className="text-xs leading-6 text-zinc-400">🧠 {mission.plan.analysis}</p>
      ) : (
        <p className="text-xs leading-6 text-zinc-500">{mission.instruction.slice(0, 160)}</p>
      )}

      {/* plan steps */}
      {mission.plan ? (
        <div className="grid gap-0.5">
          {mission.plan.steps.map((step, i) => {
            const done = step.status === "done" || i < mission.stepIndex;
            const current =
              i === mission.stepIndex &&
              (mission.status === "running" || mission.status === "wait_approval");
            const ic = done ? "✅" : step.status === "failed" ? "❌" : current ? "⏳" : "•";
            return (
              <div key={i} className="flex items-start gap-2 text-xs leading-6">
                <span className="shrink-0" aria-hidden="true">
                  {ic}
                </span>
                <span className="min-w-0">
                  <b className="font-bold text-zinc-200">
                    {AI_TOOLS[step.action] ?? step.action}
                  </b>
                  {step.reason ? <span className="text-zinc-500"> — {step.reason}</span> : null}
                </span>
              </div>
            );
          })}
        </div>
      ) : null}

      {/* posts */}
      {mission.posts.length > 0 ? (
        <Collapsible>
          <CollapsibleTrigger className="flex w-full items-center gap-1.5 rounded-md text-right text-[11px] text-zinc-400 transition-colors hover:text-emerald-300 [&[data-state=open]>svg]:rotate-180">
            <ChevronDown className="size-3.5 shrink-0 transition-transform" aria-hidden="true" />
            <span className="flex items-center gap-1">
              <Package className="size-3.5" aria-hidden="true" />
              {faDigits(mission.posts.length)} پست تولیدشده — {faDigits(mission.counts.scheduled)}{" "}
              مورد در صف انتشار
            </span>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <div className="mt-2 grid gap-2">
              {mission.posts.map((post) => (
                <div
                  key={post.id}
                  className="rounded-lg border border-dashed border-zinc-800 bg-zinc-950/40 p-3 text-xs"
                >
                  <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[11px] text-zinc-500">
                    <b dir="ltr" className="font-mono text-zinc-300">
                      {post.id}
                    </b>
                    <span>· {PLATFORM_FA[post.platform] ?? post.platform} ·</span>
                    <span
                      className={cn(
                        post.status === "scheduled" && "text-emerald-400",
                        post.status === "draft" && "text-amber-400",
                        post.status === "published" && "text-emerald-300",
                        (post.status === "failed" ||
                          post.status === "needs_media" ||
                          post.status === "no_channel") &&
                          "text-amber-400",
                      )}
                    >
                      {POST_STATUS_FA[post.status] ?? post.status}
                    </span>
                    <span className="truncate">· ایده: {post.idea.slice(0, 50)}</span>
                  </div>
                  <p className="mt-2 whitespace-pre-wrap leading-7 text-zinc-400">{post.text}</p>
                </div>
              ))}
            </div>
          </CollapsibleContent>
        </Collapsible>
      ) : null}

      {/* agent log */}
      {mission.log.length > 0 ? (
        <Collapsible defaultOpen={active}>
          <CollapsibleTrigger className="flex w-full items-center gap-1.5 rounded-md text-right text-[11px] text-zinc-400 transition-colors hover:text-emerald-300 [&[data-state=open]>svg]:rotate-180">
            <ChevronDown className="size-3.5 shrink-0 transition-transform" aria-hidden="true" />
            <span className="flex items-center gap-1">
              <ScrollText className="size-3.5" aria-hidden="true" />
              لاگ ایجنت ({faDigits(mission.log.length)} رخداد)
            </span>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <div className="scrollbar-thin mt-2 max-h-56 overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-950/70 p-3">
              {mission.log.map((entry, i) => (
                <div key={i} className="flex gap-2 py-0.5 text-[11px] leading-5">
                  <span dir="ltr" className="shrink-0 font-mono text-zinc-600">
                    {entry.t}
                  </span>
                  <span className={cn("min-w-0", LOG_LEVEL_CLS[entry.level] ?? "text-zinc-400")}>
                    {entry.msg}
                  </span>
                </div>
              ))}
            </div>
          </CollapsibleContent>
        </Collapsible>
      ) : null}

      {/* report */}
      {mission.report ? (
        <div className="rounded-xl border border-emerald-500/25 bg-emerald-500/5 p-4">
          <b className="text-xs text-emerald-200">📊 گزارش نهایی ماموریت</b>
          <p className="mt-2 whitespace-pre-wrap text-xs leading-7 text-zinc-300">
            {mission.report.summary}
          </p>
          <div className="mt-3 text-[11px] text-zinc-500">
            📊 {faDigits(mission.report.stats.posts_generated)} پست · 📅{" "}
            {faDigits(mission.report.stats.scheduled)} در صف انتشار · 🚀{" "}
            {faDigits(mission.report.stats.published_now)} انتشار فوری
          </div>
        </div>
      ) : null}

      {/* controls */}
      {cancellable ? (
        <div className="flex flex-wrap items-center gap-2">
          {mission.status === "wait_approval" ? (
            <Button
              size="sm"
              onClick={() => control("approve")}
              className="h-8 bg-emerald-500 text-xs text-zinc-950 hover:bg-emerald-400"
            >
              ✅ تأیید و اجرا
            </Button>
          ) : null}
          {mission.status === "running" || mission.status === "planning" ? (
            <Button
              size="sm"
              variant="outline"
              onClick={() => control("pause")}
              className="h-8 border-amber-500/30 bg-amber-500/5 text-xs text-amber-300 hover:bg-amber-500/10"
            >
              ⏸ توقف
            </Button>
          ) : null}
          {mission.status === "paused" ? (
            <Button
              size="sm"
              onClick={() => control("resume")}
              className="h-8 bg-emerald-500 text-xs text-zinc-950 hover:bg-emerald-400"
            >
              ▶ ادامه
            </Button>
          ) : null}
          {cancellable ? (
            <Button
              size="sm"
              variant="outline"
              onClick={() => control("cancel")}
              className="h-8 border-rose-500/30 bg-rose-500/5 text-xs text-rose-300 hover:bg-rose-500/10"
            >
              🛑 لغو
            </Button>
          ) : null}
        </div>
      ) : null}
    </motion.article>
  );
}

/* -------------------------------------------------------------------------- */
/* ۲.۴.۰ — دموی چاپخانهٔ ویدیو (سبک MoneyPrinterTurbo)                          */
/* -------------------------------------------------------------------------- */

const VIDEO_STEPS = [
  "🧠 فیلم‌نامهٔ صحنه‌ها نوشته می‌شود…",
  "🗣 گویندگی با صدای طبیعی (edge-tts — رایگان)…",
  "🖼 تصویر هر صحنه با AI ساخته می‌شود…",
  "📝 زیرنویس فارسی روی تصاویر حک می‌شود…",
  "🎬 ترکیب MP4 با ffmpeg — حرکت آرام دوربین…",
  "✅ ویدیو آماده شد — در «رسانه‌ها»",
];

function VideoFactoryDemo() {
  const [topic, setTopic] = React.useState(
    "معرفی فروشگاه گیاهان آپارتمانی ما — تخفیف ویژهٔ پایان فصل",
  );
  const [voice, setVoice] = React.useState("fa-IR-FaridNeural");
  const [aspect, setAspect] = React.useState("9:16");
  const [seconds, setSeconds] = React.useState(45);
  const [phase, setPhase] = React.useState(0); // 0=idle · 1..6=steps · 7=done
  const timer = React.useRef<number | null>(null);

  React.useEffect(
    () => () => {
      if (timer.current) window.clearTimeout(timer.current);
    },
    [],
  );

  const start = () => {
    if (phase > 0 && phase < 7) return;
    setPhase(1);
    let i = 1;
    const tick = () => {
      i += 1;
      setPhase(i);
      timer.current = window.setTimeout(tick, i < 6 ? 800 + Math.random() * 500 : 1100);
    };
    timer.current = window.setTimeout(tick, 900);
  };

  const busy = phase > 0 && phase < 7;
  const done = phase === 7;

  return (
    <section className="grid gap-4 rounded-xl border border-emerald-500/25 bg-zinc-900/50 p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="flex items-center gap-2 text-sm font-bold text-zinc-200">
          <Clapperboard className="size-4 text-emerald-400" aria-hidden="true" />
          چاپخانهٔ ویدیو
          <span className="inline-flex items-center rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-300">
            سبک MoneyPrinterTurbo
          </span>
        </h3>
        <span className="text-[10px] text-zinc-600">دموی تعاملی — نسخهٔ کامل در پنل خود نرم‌افزار</span>
      </div>
      <p className="text-xs leading-6 text-zinc-500">
        موضوع را بدهید؛ خودش <b className="text-zinc-300">فیلم‌نامه می‌نویسد</b>، با صدای طبیعی{" "}
        <b className="text-zinc-300">گویندگی می‌کند</b> (رایگان)، برای هر صحنه{" "}
        <b className="text-zinc-300">با AI عکس می‌سازد</b>،{" "}
        <b className="text-zinc-300">زیرنویس فارسی</b> را حک می‌کند و MP4 آمادهٔ انتشار تحویل می‌دهد.
      </p>

      <div className="grid gap-3 sm:grid-cols-4">
        <div className="grid gap-1.5 sm:col-span-2">
          <Label className="text-xs text-zinc-400">موضوع ویدیو</Label>
          <Input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="h-10 border-zinc-800 bg-zinc-900/60 text-xs"
          />
        </div>
        <div className="grid gap-1.5">
          <Label className="text-xs text-zinc-400">گوینده</Label>
          <Select value={voice} onValueChange={setVoice}>
            <SelectTrigger className="w-full border-zinc-800 bg-zinc-900/60 text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="border-zinc-800 bg-zinc-950 text-xs">
              <SelectItem value="fa-IR-FaridNeural" className="text-xs focus:bg-zinc-900">فرید — مرد، فارسی</SelectItem>
              <SelectItem value="fa-IR-DilaraNeural" className="text-xs focus:bg-zinc-900">دلارا — زن، فارسی</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label className="text-xs text-zinc-400">نسبت / طول</Label>
          <div className="flex gap-2">
            <Select value={aspect} onValueChange={setAspect}>
              <SelectTrigger className="w-full border-zinc-800 bg-zinc-900/60 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="border-zinc-800 bg-zinc-950 text-xs">
                <SelectItem value="9:16" className="text-xs focus:bg-zinc-900">۹:۱۶</SelectItem>
                <SelectItem value="1:1" className="text-xs focus:bg-zinc-900">۱:۱</SelectItem>
                <SelectItem value="16:9" className="text-xs focus:bg-zinc-900">۱۶:۹</SelectItem>
              </SelectContent>
            </Select>
            <Input
              type="number"
              value={seconds}
              min={15}
              max={180}
              onChange={(e) => setSeconds(+e.target.value || 45)}
              className="h-10 w-20 border-zinc-800 bg-zinc-900/60 text-xs"
            />
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Button onClick={start} disabled={busy} className="bg-emerald-500 px-6 text-sm text-zinc-950 hover:bg-emerald-400">
          {busy ? "…" : done ? "🎬 دوباره بساز" : "🎬 بساز!"}
        </Button>
        {phase > 0 && (
          <div className="min-w-40 flex-1">
            <div className="h-1.5 overflow-hidden rounded-full bg-zinc-800">
              <div
                className="h-full rounded-full bg-emerald-500 transition-all duration-500"
                style={{ width: `${(Math.min(phase, 6) / 6) * 100}%` }}
              />
            </div>
            <div className="mt-1.5 text-[11px] text-zinc-400">
              {done ? VIDEO_STEPS[5] : VIDEO_STEPS[Math.min(phase, 5)]}
            </div>
          </div>
        )}
      </div>

      {done && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-wrap items-center gap-4"
        >
          <img
            src="/demo/video-frame.png"
            alt="فریم ویدیوی ساخته‌شده با چاپخانهٔ ParsAgent — صحنهٔ فروشگاه گیاهان با زیرنویس فارسی"
            className="h-64 w-auto rounded-xl border border-zinc-800"
          />
          <div className="grid max-w-xs gap-1.5 text-[11px] leading-6 text-zinc-400">
            <b className="text-xs text-zinc-200">خروجی: ai-video-…-ai.mp4</b>
            <span>💬 گوینده: {voice === "fa-IR-FaridNeural" ? "فرید" : "دلارا"} · {faDigits(seconds)} ثانیه · {aspect}</span>
            <span>📜 فایل SRT جدا هم ذخیره می‌شود</span>
            <span>🎵 موسیقی اختیاری از پوشهٔ media/music زیر صدا می‌رود</span>
            <span>📦 خروجی مستقیم در «رسانه‌ها» — آمادهٔ پست/استوری</span>
          </div>
        </motion.div>
      )}
    </section>
  );
}

/* -------------------------------------------------------------------------- */
/* ۲.۴.۰ — دموی ساخت عکس با AI                                                  */
/* -------------------------------------------------------------------------- */

function ImageFactoryDemo() {
  const [prompt, setPrompt] = React.useState("میز چوبی کافه با فنجان قهوه و نور صبح، سبک مینیمال");
  const [provider, setProvider] = React.useState("zai");
  const [n, setN] = React.useState(0); // تعداد عکس‌های ظاهرشده
  const timer = React.useRef<number | null>(null);

  React.useEffect(
    () => () => {
      if (timer.current) window.clearInterval(timer.current);
    },
    [],
  );

  const start = () => {
    setN(0);
    if (timer.current) window.clearInterval(timer.current);
    timer.current = window.setInterval(() => {
      setN((v) => {
        if (v >= 3) {
          window.clearInterval(timer.current!);
          return v;
        }
        return v + 1;
      });
    }, 700);
  };

  return (
    <section className="grid gap-4 rounded-xl border border-zinc-800 bg-zinc-900/50 p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="flex items-center gap-2 text-sm font-bold text-zinc-200">
          <ImageIcon className="size-4 text-emerald-400" aria-hidden="true" />
          ساخت عکس با AI
          <span className="inline-flex items-center rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-300">
            GLM-Image / CogView / رایگان
          </span>
        </h3>
        <span className="text-[10px] text-zinc-600">دموی تعاملی — خروجی‌ها نمونهٔ واقعی هستند</span>
      </div>
      <p className="text-xs leading-6 text-zinc-500">
        توضیح بدهید و عکس بگیرید — مستقیم داخل «رسانه‌ها» ذخیره می‌شود تا در پست/استوری استفاده شود.
        اگر سرویس اصلی کلید نداشته باشد، خودکار به <b className="text-zinc-300">Pollinations رایگان</b> برمی‌گردد.
      </p>
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="grid gap-1.5 sm:col-span-2">
          <Label className="text-xs text-zinc-400">توضیح عکس (پرامپت)</Label>
          <Input
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="h-10 border-zinc-800 bg-zinc-900/60 text-xs"
          />
        </div>
        <div className="grid gap-1.5">
          <Label className="text-xs text-zinc-400">تصویرساز</Label>
          <Select value={provider} onValueChange={setProvider}>
            <SelectTrigger className="w-full border-zinc-800 bg-zinc-900/60 text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="border-zinc-800 bg-zinc-950 text-xs">
              <SelectItem value="zai" className="text-xs focus:bg-zinc-900">Z.ai — GLM-Image</SelectItem>
              <SelectItem value="openai" className="text-xs focus:bg-zinc-900">OpenAI — DALL·E 3</SelectItem>
              <SelectItem value="pollinations" className="text-xs focus:bg-zinc-900">Pollinations — رایگان</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <Button onClick={start} className="bg-emerald-500 px-6 text-sm text-zinc-950 hover:bg-emerald-400">
          🎨 بساز
        </Button>
        <span className="text-[11px] text-zinc-500">
          {n > 0 ? `✅ ${faDigits(n)} عکس ساخته شد — در «رسانه‌ها»` : "خروجی‌ها در تب «رسانه‌ها» هم می‌آیند"}
        </span>
      </div>
      {n > 0 && (
        <div className="grid grid-cols-3 gap-3">
          {["/demo/img-1.png", "/demo/img-2.png", "/demo/img-3.png"].slice(0, n).map((src, i) => (
            <motion.div
              key={src}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.25 }}
              className="overflow-hidden rounded-xl border border-zinc-800"
            >
              <img src={src} alt={`عکس ساخته‌شده با AI — نمونهٔ ${faDigits(i + 1)}`} className="h-32 w-full object-cover" />
            </motion.div>
          ))}
        </div>
      )}
    </section>
  );
}

/* -------------------------------------------------------------------------- */
/* ۲.۴.۰ — دموی پاسخ‌گوی خودکار دایرکت                                           */
/* -------------------------------------------------------------------------- */

function DmReplyDemo() {
  const [persona, setPersona] = React.useState("پیج فروشگاه گیاهان آپارتمانی؛ ارسال سراسری، سفارش از دایرکت");
  const [phase, setPhase] = React.useState(0); // 0=idle · 1=reading · 2=typing · 3=sent
  const timer = React.useRef<number | null>(null);

  React.useEffect(
    () => () => {
      if (timer.current) window.clearTimeout(timer.current);
    },
    [],
  );

  const start = () => {
    setPhase(1);
    timer.current = window.setTimeout(() => {
      setPhase(2);
      timer.current = window.setTimeout(() => setPhase(3), 2300);
    }, 900);
  };

  return (
    <section className="grid gap-4 rounded-xl border border-zinc-800 bg-zinc-900/50 p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="flex items-center gap-2 text-sm font-bold text-zinc-200">
          <MessageCircleReply className="size-4 text-emerald-400" aria-hidden="true" />
          پاسخ‌گوی خودکار دایرکت
          <span className="inline-flex items-center rounded-full border border-zinc-700 bg-zinc-900 px-2 py-0.5 text-[10px] text-zinc-400">
            هر ۷ پلتفرم
          </span>
        </h3>
        <span className="text-[10px] text-zinc-600">دموی تعاملی — با شخصیت و لحن شما</span>
      </div>
      <p className="text-xs leading-6 text-zinc-500">
        گفتگوهایی که آخرین پیامشان از طرف مقابل است را پیدا می‌کند و با شخصیت شما طبیعی جواب می‌دهد —
        با سقف روزانه، ساعت‌های فعال و <b className="text-zinc-300">حالت پیش‌نمایش</b> (اول جواب‌ها را ببینید، بعد ارسال).
      </p>
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="grid gap-1.5">
          <Label className="text-xs text-zinc-400">معرفی شما / کسب‌وکارتان (شخصیت جواب‌ها)</Label>
          <Input
            value={persona}
            onChange={(e) => setPersona(e.target.value)}
            className="h-10 border-zinc-800 bg-zinc-900/60 text-xs"
          />
        </div>
        <div className="grid gap-1.5">
          <Label className="text-xs text-zinc-400">لحن</Label>
          <Input
            defaultValue="صمیمی و محترمانه — فارسی روان"
            className="h-10 border-zinc-800 bg-zinc-900/60 text-xs"
          />
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <Button onClick={start} className="bg-emerald-500 px-6 text-sm text-zinc-950 hover:bg-emerald-400">
          🔍 پیش‌نمایش (بدون ارسال)
        </Button>
        <span className="text-[11px] text-zinc-500">
          {phase === 0 && "یک گفتگوی نمونه را ببینید"}
          {phase === 1 && "👀 گفتگوهای نیازمند جواب پیدا می‌شوند…"}
          {phase === 2 && "✍️ در حال نوشتن جواب با شخصیت شما…"}
          {phase === 3 && "✅ جواب پیشنهادی آماده است — با تأیید شما ارسال می‌شود"}
        </span>
      </div>
      <div className="flex max-h-72 flex-col gap-2 overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-950/70 p-3">
        <div className="self-start rounded-xl rounded-tl-sm border border-zinc-700 bg-zinc-900 px-3.5 py-2 text-xs leading-6 text-zinc-300">
          سلام 🌿 ببخشید ارسال به شهرستان دارید؟ برای کدوم گیاه‌ها تخفیف پایان فصل دارید؟
        </div>
        {phase >= 2 && phase < 3 && (
          <div className="flex items-center gap-1 self-end rounded-xl border border-zinc-800 bg-zinc-900 px-3.5 py-2">
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="size-1.5 animate-bounce rounded-full bg-zinc-500"
                style={{ animationDelay: `${i * 0.15}s` }}
              />
            ))}
          </div>
        )}
        {phase === 3 && (
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            className="self-end rounded-xl rounded-tr-sm border border-emerald-500/30 bg-emerald-500/10 px-3.5 py-2 text-xs leading-6 text-emerald-100"
          >
            سلام خوش آمدید 🌱 بله، ارسال به سراسر کشور انجام می‌شه — همهٔ گیاهان آپارتمانی این هفته ۲۰٪ تخفیف
            پایان فصل دارند. تا ساعت ۴ امروز سفارش بدید، فردا دستتونه می‌رسه 📦
          </motion.div>
        )}
      </div>
    </section>
  );
}
