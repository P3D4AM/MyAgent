// -----------------------------------------------------------------------------
// ParsAgent Web Panel — in-memory agent simulation store.
//
// This powers the web control panel while running inside the browser sandbox:
// every capability of the real Windows agent (resilient browser launcher with
// per-platform persistent profiles, task engine, macro recorder/player,
// desktop system actions, scheduler, settings) is simulated faithfully so the
// panel behaves exactly like it would against `python main.py gateway`.
// -----------------------------------------------------------------------------

import {
  PLATFORMS as CATALOG,
  SPEEDS,
  buildScript,
  faDigits,
  getPlatform,
  type ActionDef,
  type EngineId,
  type SpeedId,
} from "@/components/agent/data";
import type {
  AiMission,
  AiMissionStep,
  AiPanelState,
  AiProviderInfo,
  Macro,
  MacroEvent,
  PanelActionType,
  PanelLogLevel,
  PanelLog,
  PanelSettings,
  PanelState,
  PanelTask,
  PlaybackState,
  PlatformRuntime,
  ScheduleSpec,
  SystemSnapshot,
  TaskStepState,
} from "./types";

const VERSION = "v1.0.0";
const MAX_LOGS = 400;
const MAX_EVENTS = 240;

function now(): number {
  return Date.now();
}

function ts(): string {
  return new Date().toLocaleTimeString("en-GB", { hour12: false });
}

function rand(min: number, max: number): number {
  return min + Math.random() * (max - min);
}

function randInt(min: number, max: number): number {
  return Math.floor(rand(min, max + 1));
}

function clamp(v: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, v));
}

function pick<T>(arr: T[]): T {
  return arr[randInt(0, arr.length - 1)];
}

function logTimestamp(d: Date): string {
  return d.toLocaleTimeString("en-GB", { hour12: false });
}

function pad(n: number): string {
  return String(n).padStart(2, "0");
}

const DEFAULT_SETTINGS: PanelSettings = {
  channelFallbacks: ["msedge", "chrome", "chromium"],
  headless: false,
  proxy: "",
  human: {
    enabled: true,
    minDelayS: 0.35,
    maxDelayS: 1.4,
    typingMinMs: 35,
    typingMaxMs: 95,
  },
  gateway: {
    url: "ws://127.0.0.1:3030",
    token: "change-me",
  },
};

const SAMPLE_TEXTS = [
  "سلام! این پیام خودکار از پارس‌ایجنت است 🤖",
  "گزارش امروز آماده شد ✅",
  "یادآوری جلسه ساعت ۱۴",
  "دنبال کردن اخبار فناوری",
  "parsagent",
];

const HOTKEY_SAMPLES = [
  ["ctrl", "c"],
  ["ctrl", "v"],
  ["ctrl", "shift", "esc"],
  ["win", "d"],
  ["alt", "tab"],
];

// --------------------------------------------------------------------------- //
// هوش مصنوعی — ایجنت خودمختار (mirrors parsagent/ai_agent.py)
// --------------------------------------------------------------------------- //

const AI_TOOL_FA: Record<string, string> = {
  generate_content: "تولید محتوا",
  schedule_publish: "زمان‌بندی انتشار",
  publish_now: "انتشار فوری",
  follow_strategy: "استراتژی فالو",
  wait_report: "گزارش زمان‌دار",
  report: "گزارش نهایی",
  status_check: "بررسی وضعیت",
};

const AI_PLATFORM_FA: Record<string, string> = {
  instagram: "اینستاگرام",
  twitter: "توییتر (X)",
  telegram: "تلگرام",
  facebook: "فیسبوک",
  linkedin: "لینکدین",
  bale: "بله",
  rubika: "روبیکا",
};

/** کاتالوگ سرویس‌ها — همان PROVIDERS در ai_agent.py؛ ترتیب مهم است (Z.ai اول). */
const AI_CATALOG: AiProviderInfo[] = [
  {
    id: "zai",
    name: "Z.ai (GLM)",
    note: "پیشنهادی — مدل‌های GLM؛ دو مدل Flash کاملاً رایگان‌اند",
    hasKey: true,
    models: [
      { id: "glm-4.6", name: "GLM-4.6", tag: "پیشرفته", note: "پرچمدار جدید Z.ai — بهترین کیفیت" },
      { id: "glm-4.5", name: "GLM-4.5", tag: "پولی", note: "نسخهٔ پایدار نسل قبل" },
      { id: "glm-4.5-air", name: "GLM-4.5-Air", tag: "اقتصادی", note: "سبک و ارزان" },
      { id: "glm-4.5-flash", name: "GLM-4.5-Flash", tag: "رایگان", note: "رایگان و سریع — برای شروع" },
      { id: "glm-4-flash-250414", name: "GLM-4-Flash", tag: "رایگان", note: "رایگان — نسل قبل" },
    ],
  },
  {
    id: "zai_coding",
    name: "Z.ai — طرح Coding",
    note: "برای مشترکان GLM Coding Plan — همان کلید Z.ai",
    hasKey: false,
    models: [
      { id: "glm-4.6", name: "GLM-4.6 (Coding)", tag: "پولی", note: "با اشتراک ماهانهٔ Coding Plan" },
      { id: "glm-4.5", name: "GLM-4.5 (Coding)", tag: "پولی", note: "با اشتراک ماهانهٔ Coding Plan" },
    ],
  },
  {
    id: "openai",
    name: "OpenAI",
    note: "GPT — پولی",
    hasKey: false,
    models: [
      { id: "gpt-5", name: "GPT-5", tag: "پیشرفته", note: "پرچمدار OpenAI" },
      { id: "gpt-5-mini", name: "GPT-5 mini", tag: "اقتصادی", note: "سریع و ارزان" },
      { id: "gpt-4.1", name: "GPT-4.1", tag: "پولی", note: "نسخهٔ پایدار" },
      { id: "gpt-4.1-mini", name: "GPT-4.1 mini", tag: "اقتصادی", note: "سبک" },
      { id: "gpt-4o", name: "GPT-4o", tag: "پولی", note: "چندوجهی نسل قبل" },
      { id: "gpt-4o-mini", name: "GPT-4o mini", tag: "اقتصادی", note: "کم‌هزینه" },
    ],
  },
  {
    id: "anthropic",
    name: "Anthropic Claude",
    note: "کلود — پولی",
    hasKey: false,
    models: [
      { id: "claude-sonnet-4-5", name: "Claude Sonnet 4.5", tag: "پیشرفته", note: "تعادل کیفیت/قیمت" },
      { id: "claude-opus-4-1", name: "Claude Opus 4.1", tag: "پیشرفته", note: "بالاترین کیفیت" },
      { id: "claude-haiku-4-5", name: "Claude Haiku 4.5", tag: "اقتصادی", note: "سریع و ارزان" },
    ],
  },
  {
    id: "gemini",
    name: "Google Gemini",
    note: "جِمینی — Fluent رایگان در AI Studio",
    hasKey: false,
    models: [
      { id: "gemini-2.5-pro", name: "Gemini 2.5 Pro", tag: "پیشرفته", note: "پرچمدار گوگل" },
      { id: "gemini-2.5-flash", name: "Gemini 2.5 Flash", tag: "رایگان", note: "سریع و اقتصادی" },
      { id: "gemini-2.0-flash", name: "Gemini 2.0 Flash", tag: "رایگان", note: "نسل قبل" },
    ],
  },
  {
    id: "groq",
    name: "Groq",
    note: "سریع‌ترین اینترنت — با سطح رایگان سخاوتمندانه",
    hasKey: false,
    models: [
      { id: "llama-3.3-70b-versatile", name: "Llama 3.3 70B", tag: "رایگان", note: "باکیفیت و رایگان" },
      { id: "llama-3.1-8b-instant", name: "Llama 3.1 8B", tag: "رایگان", note: "فوری" },
      { id: "deepseek-r1-distill-llama-70b", name: "DeepSeek R1 Distill", tag: "رایگان", note: "استدلالی" },
      { id: "qwen/qwen3-32b", name: "Qwen3 32B", tag: "رایگان", note: "چندزبانه" },
      { id: "moonshotai/kimi-k2-instruct", name: "Kimi K2", tag: "رایگان", note: "مدل بزرگ جدید" },
    ],
  },
  {
    id: "deepseek",
    name: "DeepSeek",
    note: "بسیار ارزان",
    hasKey: false,
    models: [
      { id: "deepseek-chat", name: "DeepSeek V3", tag: "اقتصادی", note: "ارزان و توانمند" },
      { id: "deepseek-reasoner", name: "DeepSeek R1", tag: "اقتصادی", note: "استدلال گام‌به‌گام" },
    ],
  },
  {
    id: "openrouter",
    name: "OpenRouter",
    note: "تجمیع‌کنندهٔ صدها مدل — خیلی از مدل‌ها «:free» رایگان‌اند",
    hasKey: false,
    models: [
      { id: "deepseek/deepseek-chat-v3-0324:free", name: "DeepSeek V3 (رایگان)", tag: "رایگان", note: "نسخهٔ رایگان OpenRouter" },
      { id: "meta-llama/llama-3.3-70b-instruct:free", name: "Llama 3.3 70B (رایگان)", tag: "رایگان", note: "نسخهٔ رایگان" },
      { id: "qwen/qwen3-235b-a22b:free", name: "Qwen3 235B (رایگان)", tag: "رایگان", note: "مدل بزرگ رایگان" },
      { id: "google/gemini-2.0-flash-exp:free", name: "Gemini 2.0 Flash (رایگان)", tag: "رایگان", note: "رایگان" },
      { id: "openai/gpt-4o-mini", name: "GPT-4o mini", tag: "پولی", note: "از طریق OpenRouter" },
      { id: "anthropic/claude-sonnet-4.5", name: "Claude Sonnet 4.5", tag: "پولی", note: "از طریق OpenRouter" },
    ],
  },
  {
    id: "custom",
    name: "سرویس سفارشی (سازگار با OpenAI)",
    note: "هر اندپوینت OpenAI-سازگار — مثل Ollama لوکال (http://127.0.0.1:11434/v1)",
    hasKey: false,
    models: [
      { id: "custom-model", name: "مدل سفارشی", tag: "خودتان", note: "از تنظیمات ← هوش مصنوعی تغییر دهید" },
    ],
  },
];

const AI_IDEA_POOL = [
  "معرفی محصول جدید",
  "پشت صحنهٔ کار",
  "داستان موفقیت مشتری",
  "نکات سریع",
  "نظرسنجی هفتگی",
];

const AI_CHAT_REPLIES = [
  "با کمال میل! اگر همین ایده را در فرم «ماموریت جدید» بنویسید، برنامهٔ اجرایی، متن پست‌ها و زمان‌بندی انتشار را برایتان می‌سازم و آخر کار گزارش کامل می‌دهم.",
  "برای شروع، مدل‌های رایگان GLM-4.5-Flash یا GLM-4-Flash از Z.ai را پیشنهاد می‌کنم — بدون هزینه و با کیفیت مناسب.",
  "می‌توانم برای هر ایده چند پست بنویسم، ساعات انتشار را بچینم و استراتژی فالو را هم طراحی کنم؛ فقط بگویید برای کدام پلتفرم.",
  "بهترین ساعت انتشار برای مخاطب ایرانی معمولاً ۱۲، ۱۸ و ۲۱ است؛ در زمان‌بندی ماموریت همین ساعات را رعایت می‌کنم.",
  "سقف امن فالو روزانهٔ اینستاگرام را ۱۵۰ نفر در نظر می‌گیرم و آن را در چند نوبت پخش می‌کنم تا رفتار ایجنت طبیعی بماند.",
];

const AI_PLAN_MS = 1400;
const AI_STEP_MS = 1600;
const AI_CHAT_REPLY_MS = 800;

function aiTitle(instruction: string): string {
  const t = instruction.replace(/\s+/g, " ").trim();
  if (t.length <= 40) return t;
  const cut = t.slice(0, 40);
  const sp = cut.lastIndexOf(" ");
  return `${(sp > 20 ? cut.slice(0, sp) : cut).trim()}…`;
}

function aiAnalysis(instruction: string): string {
  const short = instruction.replace(/\s+/g, " ").trim().slice(0, 60);
  return (
    `خواستهٔ شما حول «${short}» دسته‌بندی شد؛ برنامهٔ سه‌گامی چیده شده است: ` +
    "ابتدا برای هر ایده محتوای متناسب هر پلتفرم تولید می‌شود، سپس انتشار در ساعات پرترافیک مخاطب ایرانی " +
    "(۱۲، ۱۸ و ۲۱) پخش می‌شود و در پایان گزارش نهایی با آمار کامل ارائه می‌گردد. سقف امن پست روزانه (۴ پست) رعایت می‌شود."
  );
}

function aiPickPlatforms(instruction: string): string[] {
  const has = (keywords: string[]) => keywords.some((k) => instruction.includes(k));
  const out: string[] = [];
  if (has(["تلگرام", "کانال", "telegram"])) out.push("telegram");
  if (has(["توییتر", "twitter"])) out.push("twitter");
  if (has(["لینکدین", "linkedin"])) out.push("linkedin");
  if (out.length === 0) out.push("telegram", "twitter");
  return out;
}

function aiPlanSteps(instruction: string): AiMissionStep[] {
  const excerpt = instruction.replace(/\s+/g, " ").trim().slice(0, 60);
  return [
    {
      action: "generate_content",
      params: {
        ideas: [excerpt],
        posts_per_idea: 1,
        platforms: aiPickPlatforms(instruction),
        tone: "دوستانه و حرفه‌ای فارسی",
      },
      reason: `تولید متن متناسب هر پلتفرم برای خواستهٔ «${excerpt}»`,
      status: "pending",
    },
    {
      action: "schedule_publish",
      params: { strategy: "spread_week", per_day: 3 },
      reason: "پخش پست‌ها در ساعات پرترافیک هفته با سقف امن روزانه",
      status: "pending",
    },
    {
      action: "report",
      params: { include: ["posts", "schedules"] },
      reason: "گزارش نهایی با آمار تولید و زمان‌بندی",
      status: "pending",
    },
  ];
}

function aiPostText(platform: string, idea: string): string {
  const short = idea.length > 56 ? `${idea.slice(0, 56)}…` : idea;
  switch (platform) {
    case "twitter":
      return `${short}\nبا پارس‌ایجنت همین کار خودکار شد — شما هم امتحان کنید. #اتوماسیون`;
    case "linkedin":
      return `${short}\n\nدر تجربهٔ ما، تکرارِ هوشمند کلید رشد پایدار است؛ این پست را به‌عنوان نقطهٔ شروع بحث با شما به اشتراک می‌گذاریم.\n\nنظر شما چیست؟ در کامنت‌ها بنویسید.\n\n#محتوا #رشد`;
    default:
      return `${short}\n\nاین هفته با هم قدم‌به‌قدم جلو می‌رویم؛ نظرتان را همین‌جا بنویسید تا دقیق‌ترش کنیم.\n\nبرای دوستانتان هم بفرستید.\n\n#پارس_ایجنت #اتوماسیون`;
  }
}

/** یک ماموریت نمونهٔ کامل — نشان می‌دهد کارت تمام‌شده چه شکلی است. */
function aiDemoMission(): AiMission {
  const t = now();
  return {
    id: "m001",
    title: "کمپین هفتگی فروشگاه",
    instruction:
      "برای فروشگاهم محتوای معرفی بساز و این هفته در تلگرام (کانال فروشگاه) و توییتر منتشر کن؛ آخر هفته گزارش بده",
    provider: "zai",
    model: "glm-4.6",
    autonomy: "semi",
    status: "completed",
    createdAt: t - 3600_000,
    updatedAt: t - 3500_000,
    plan: {
      title: "کمپین هفتگی فروشگاه",
      analysis:
        "محتوای معرفی فروشگاه برای تلگرام و توییتر تولید می‌شود؛ انتشار در ساعات پرترافیک (۱۲، ۱۸ و ۲۱) در طول هفته پخش می‌شود و آخر هفته گزارش عملکرد ارائه می‌گردد. سقف امن پست روزانه رعایت شده است.",
      steps: [
        {
          action: "generate_content",
          params: { ideas: ["معرفی محصولات پرفروش", "ارسال رایگان"], posts_per_idea: 1, platforms: ["telegram", "twitter"], tone: "دوستانه و حرفه‌ای فارسی" },
          reason: "برای شروع، برای هر ایده یک پست برای تلگرام و توییتر",
          status: "done",
        },
        {
          action: "schedule_publish",
          params: { strategy: "spread_week", per_day: 2, channels: { telegram: "فروشگاه من" } },
          reason: "پخش پست‌ها در ساعات پرترافیک هفته",
          status: "done",
        },
        {
          action: "report",
          params: { include: ["posts", "schedules"] },
          reason: "گزارش عملکرد آخر هفته",
          status: "done",
        },
      ],
    },
    stepIndex: 3,
    counts: { posts: 4, scheduled: 4, published: 0 },
    report: {
      summary:
        "• ۴ پست در ۲ پلتفرم (تلگرام، توییتر (X)) تولید و زمان‌بندی شد.\n" +
        "• انتشار در ساعات پرترافیک (۱۲، ۱۸ و ۲۱) در طول هفته پخش شده است.\n" +
        "• متن‌ها با لحن دوستانه و حرفه‌ای و هشتگ‌های متناسب هر پلتفرم نوشته شده‌اند.\n\n" +
        "گام بعدی پیشنهادی: نتیجهٔ پست‌ها را جمعه مرور کنید و ایدهٔ پربازدید را هفتهٔ بعد تکرار کنید.\n" +
        "جمع‌بندی: کمپین روی ریل رفته و تا پایان هفته خودکار اجرا می‌شود.",
      stats: { posts_generated: 4, scheduled: 4, published_now: 0 },
    },
    log: [
      { t: "۱۰:۱۲:۰۴", level: "info", msg: "🧠 در حال فهمیدن ماموریت و ساخت برنامهٔ اجرایی…" },
      { t: "۱۰:۱۲:۰۶", level: "ok", msg: "📋 برنامه آماده شد: ۳ گام — کمپین هفتگی فروشگاه" },
      { t: "۱۰:۱۲:۰۹", level: "info", msg: "✍️ تولید محتوا برای ایده: «معرفی محصولات پرفروش»" },
      { t: "۱۰:۱۲:۱۲", level: "ok", msg: "✅ ۲ پست برای «معرفی محصولات پرفروش» تولید شد (مجموع: ۲)" },
      { t: "۱۰:۱۲:۱۴", level: "info", msg: "✍️ تولید محتوا برای ایده: «ارسال رایگان»" },
      { t: "۱۰:۱۲:۱۶", level: "ok", msg: "✅ ۲ پست برای «ارسال رایگان» تولید شد (مجموع: ۴)" },
      { t: "۱۰:۱۲:۱۸", level: "ok", msg: "📅 ۴ پست در صف انتشار قرار گرفت" },
      { t: "۱۰:۱۲:۱۹", level: "info", msg: "📝 در حال نوشتن گزارش مدیریتی…" },
      { t: "۱۰:۱۲:۲۱", level: "ok", msg: "✅ گزارش نهایی آماده است — تب هوش مصنوعی ← کارت ماموریت" },
    ],
    posts: [
      {
        id: "p1",
        platform: "telegram",
        idea: "معرفی محصولات پرفروش",
        text: "پرفروش‌های این ماه فروشگاه ما معرفی شدند — انتخاب‌هایی که مشتری‌ها بیشتر از همه دوست داشتند.\n\nتا پایان هفته، ارسال همهٔ سفارش‌ها رایگان است.\n\nبرای سفارش، همین‌جا پیام بدهید.\n\n#فروشگاه #پرفروش",
        status: "scheduled",
      },
      {
        id: "p2",
        platform: "twitter",
        idea: "معرفی محصولات پرفروش",
        text: "پرفروش‌های این ماه معرفی شدند و این هفته ارسال رایگان است. شما کدام را امتحان کرده‌اید؟ #فروشگاه",
        status: "scheduled",
      },
      {
        id: "p3",
        platform: "telegram",
        idea: "ارسال رایگان",
        text: "هفتهٔ ارسال رایگان شروع شد!\n\nهر سفارشی که این هفته ثبت کنید، بدون هزینهٔ پست به دستتان می‌رسد — فرصت تا جمعه.\n\nبرای ثبت سفارش پیام بدهید.\n\n#ارسال_رایگان #فروشگاه",
        status: "scheduled",
      },
      {
        id: "p4",
        platform: "twitter",
        idea: "ارسال رایگان",
        text: "این هفته ارسال همهٔ سفارش‌ها رایگان است — فقط تا جمعه. سفارش از پیام‌رسان ثبت می‌شود. #فروشگاه",
        status: "scheduled",
      },
    ],
  };
}

function aiDefaultState(): AiPanelState {
  return {
    provider: "zai",
    model: "glm-4.6",
    autonomy: "semi",
    catalog: structuredClone(AI_CATALOG),
    missions: [aiDemoMission()],
    chat: [],
  };
}

// --------------------------------------------------------------------------- //

export class PanelStore {
  private logs: PanelLog[] = [];
  private logSeq = 0;

  private platforms: Map<string, PlatformRuntime>;
  private tasks: PanelTask[] = [];
  private taskSeq = 0;

  private macros: Macro[] = [];
  private macroSeq = 0;

  private recorderEvents: MacroEvent[] = [];
  private recorderActive = false;
  private recorderStartedAt: number | null = null;

  private playback: PlaybackState | null = null;

  private settings: PanelSettings = structuredClone(DEFAULT_SETTINGS);

  private system: SystemSnapshot = {
    cpu: 8,
    ram: 38,
    mouse: { x: 960, y: 540 },
    clipboard: "https://github.com/pars-agent/parsagent",
    resolution: { w: 1920, h: 1080 },
    uptimeS: 0,
  };

  private startedAt = now();
  private lastTick = now();
  private screenshotSeq = 0;
  private playbackLogged = 0;

  // --- هوش مصنوعی ---
  private ai: AiPanelState = aiDefaultState();
  private aiMissionSeq = 1;
  private aiChatReplySeq = 0;
  private aiMissionTimers = new Map<
    string,
    { token: number; timers: ReturnType<typeof setTimeout>[] }
  >();

  constructor() {
    this.platforms = new Map(
      CATALOG.map((p) => [
        p.id,
        {
          id: p.id,
          running: false,
          loggedIn: false,
          loggingIn: false,
          loginStartedAt: null,
          loginDurationMs: 9000,
          channel: null,
          profile: `data/profiles/${p.id}`,
          lastAction: null,
          lastActiveAt: null,
          sessionAgeMin: 0,
        } satisfies PlatformRuntime,
      ]),
    );
    this.log("gate", "ok", `pars-agent ${VERSION} — web panel link established (simulator mode)`);
    this.log("gate", "info", "waiting for commands… (مرورگر وب به ایجنت متصل شد)");
  }

  // ------------------------------------------------------------------ logs --
  private log(tag: string, level: PanelLogLevel, text: string): PanelLog {
    const entry: PanelLog = { id: ++this.logSeq, ts: ts(), tag, level, text };
    this.logs.push(entry);
    if (this.logs.length > MAX_LOGS) this.logs.splice(0, this.logs.length - MAX_LOGS);
    return entry;
  }

  // ------------------------------------------------------------------ tick --
  /** Advances the simulation. `dt` is capped so long tab sleeps don't jump. */
  tick(): void {
    const t = now();
    let dt = t - this.lastTick;
    this.lastTick = t;
    if (dt <= 0) return;
    if (dt > 6000) dt = 6000;
    const dtS = dt / 1000;

    this.system.uptimeS += dtS;

    // ---- vitals random-walk (busier when tasks are running) ----
    const activeTasks = this.tasks.filter((task) => task.status === "running").length;
    const load = 6 + activeTasks * 22 + (this.recorderActive ? 6 : 0);
    this.system.cpu = clamp(this.system.cpu + rand(-4, 4) + (load - this.system.cpu) * 0.08, 2, 97);
    this.system.ram = clamp(this.system.ram + rand(-1.5, 1.6), 24, 88);

    // ---- login flows ----
    for (const p of this.platforms.values()) {
      if (!p.loggingIn) {
        if (p.loggedIn) p.sessionAgeMin += dtS / 60;
        continue;
      }
      const elapsed = t - (p.loginStartedAt ?? t);
      const dur = p.loginDurationMs;
      // staged progress logs at 35% and 70%
      if (elapsed >= dur * 0.35 && elapsed - dt < dur * 0.35) {
        this.log(p.id, "info", "waiting for your login in the opened window…");
      }
      if (elapsed >= dur * 0.7 && elapsed - dt < dur * 0.7) {
        this.log("playwright", "info", "storage state captured (localStorage + cookies)");
      }
      if (elapsed >= dur) {
        p.loggingIn = false;
        p.loggedIn = true;
        p.running = true;
        p.channel = p.channel ?? this.settings.channelFallbacks[0];
        p.sessionAgeMin = 0;
        p.lastActiveAt = t;
        this.log(p.id, "ok", `login complete — session saved → data/sessions/${p.id}.json`);
        this.log("playwright", "ok", "persistent profile will skip login next time");
      }
    }

    // ---- tasks ----
    for (const task of this.tasks) {
      if (task.status === "running") this.advanceTask(task, dt, t);
      // scheduler
      if (
        task.status !== "running" &&
        task.schedule.type !== "manual" &&
        task.nextRunAt !== null &&
        t >= task.nextRunAt
      ) {
        this.log("scheduler", "info", `schedule triggered → ${task.name}`);
        this.startTask(task, t);
      }
    }

    // ---- recorder ----
    if (this.recorderActive) this.generateRecordEvents(dt, t);

    // ---- playback ----
    if (this.playback) {
      const pb = this.playback;
      const elapsed = t - pb.startedAt;
      const frac = clamp(elapsed / pb.durationMs, 0, 1);
      // move the simulated mouse along the macro path
      const macro = this.macros.find((m) => m.id === pb.macroId);
      if (macro) {
        const idx = Math.min(
          macro.events.length - 1,
          Math.floor(frac * macro.events.length),
        );
        const ev = macro.events[idx];
        if (ev && ev.x !== undefined && ev.y !== undefined) {
          this.system.mouse = { x: ev.x, y: ev.y };
        }
      }
      const quarter = Math.floor(frac * 4);
      if (quarter > this.playbackLogged && quarter < 4) {
        this.playbackLogged = quarter;
        this.log(
          "desktop",
          "info",
          `replaying ${macro?.name ?? "macro"} — event ${Math.floor(frac * (pb.totalEvents || 1))}/${pb.totalEvents}`,
        );
      }
      if (elapsed >= pb.durationMs) {
        const macroName = pb.macroName;
        this.playback = null;
        this.playbackLogged = 0;
        this.log("desktop", "ok", `macro replayed — ${macroName} (${pb.totalEvents} events at ×${pb.speed})`);
      }
    }
  }

  // ------------------------------------------------------------- recorder --
  private generateRecordEvents(dt: number, t: number): void {
    const count = Math.min(4, Math.floor(dt / 550) + (Math.random() < 0.6 ? 1 : 0));
    for (let i = 0; i < count; i++) {
      const rel = Math.max(0, (this.recorderStartedAt ? t - this.recorderStartedAt : 0) - (count - i) * (dt / count));
      const roll = Math.random();
      if (roll < 0.66) {
        // wandering mouse move
        const nx = clamp(this.system.mouse.x + rand(-260, 260), 60, 1860);
        const ny = clamp(this.system.mouse.y + rand(-180, 180), 40, 1040);
        this.system.mouse = { x: Math.round(nx), y: Math.round(ny) };
        this.pushEvent({ type: "move", x: this.system.mouse.x, y: this.system.mouse.y, t: rel });
      } else if (roll < 0.84) {
        const button: "left" | "right" = Math.random() < 0.85 ? "left" : "right";
        this.pushEvent({
          type: "click",
          x: this.system.mouse.x,
          y: this.system.mouse.y,
          button,
          t: rel,
        });
        this.log(
          "desktop",
          "info",
          `captured ${button === "left" ? "click" : "right-click"} → (${this.system.mouse.x}, ${this.system.mouse.y})`,
        );
      } else if (roll < 0.94) {
        const key = pick(["a", "s", "Enter", "Backspace", "Space", "t", "e"]);
        this.pushEvent({ type: "key", key, t: rel });
        this.log("desktop", "info", `captured key → ${key}`);
      } else if (roll < 0.98) {
        this.pushEvent({ type: "scroll", x: this.system.mouse.x, y: this.system.mouse.y, t: rel });
      } else {
        const keys = pick(HOTKEY_SAMPLES);
        this.pushEvent({ type: "hotkey", keys, t: rel });
        this.log("desktop", "info", `captured hotkey → ${keys.join("+")}`);
      }
    }
  }

  private pushEvent(ev: MacroEvent): void {
    this.recorderEvents.push(ev);
    if (this.recorderEvents.length > MAX_EVENTS) this.recorderEvents.shift();
  }

  // ---------------------------------------------------------------- tasks --
  private buildSteps(
    platformId: string,
    actionId: string,
    engine: EngineId,
    params: { text: string; target: string; image: string },
  ): { steps: TaskStepState[]; totalWeight: number } {
    const platform = getPlatform(platformId);
    const action = platform.actions.find((a) => a.id === actionId) ?? platform.actions[0];
    const script = buildScript(platform, action, params, {
      engine,
      networkIssue: false,
    });
    const totalWeight = script.reduce((acc, s) => acc + s.weight, 0);
    let acc = 0;
    const steps: TaskStepState[] = script.map((s) => {
      acc += s.weight;
      return {
        tag: s.tag,
        level: s.level,
        text: s.text,
        at: acc / totalWeight,
        emitted: false,
      };
    });
    // emit the very first step instantly
    if (steps.length > 0) steps[0].emitted = true;
    return { steps, totalWeight };
  }

  private startTask(task: PanelTask, t: number): void {
    const built = this.buildSteps(task.platformId, task.actionId, task.engine, task.params);
    task.steps = built.steps;
    task.simDurationMs = built.totalWeight * 1350 * (SPEEDS[task.speed]?.mult ?? 1);
    task.status = "running";
    task.progress = 0;
    task.currentStep = 0;
    task.startedAt = t;
    task.runCount += 1;
    task.lastRunAt = t;
    const p = this.platforms.get(task.platformId);
    if (p) {
      p.lastAction = task.actionLabel;
      p.lastActiveAt = t;
      if (!p.running) {
        p.running = true;
        p.channel = p.channel ?? this.settings.channelFallbacks[0];
      }
    }
    this.log("gate", "info", `run → ${task.name} (engine=${task.engine}  speed=${SPEEDS[task.speed]?.label})`);
    // emit first log line
    const first = task.steps[0];
    if (first) this.log(first.tag, first.level, first.text);
  }

  private advanceTask(task: PanelTask, dt: number, t: number): void {
    const prev = task.progress;
    task.progress = clamp(task.progress + dt / task.simDurationMs, 0, 1);
    // emit crossed steps
    for (let i = 0; i < task.steps.length; i++) {
      const s = task.steps[i];
      if (!s.emitted && task.progress >= s.at * 0.999) {
        s.emitted = true;
        task.currentStep = i + 1;
        this.log(s.tag, s.level, s.text);
      }
    }
    if (task.progress >= 1 && prev < 1) {
      task.status = "done";
      task.lastDurationS = (t - (task.startedAt ?? t)) / 1000;
      task.progress = 1;
      this.scheduleNext(task, t);
    }
  }

  private scheduleNext(task: PanelTask, t: number): void {
    if (task.schedule.type === "every") {
      task.nextRunAt = t + task.schedule.seconds * 1000;
      this.log("scheduler", "info", `next run of ${task.name} in ${task.schedule.label}`);
    } else {
      task.nextRunAt = null;
    }
  }

  // ---------------------------------------------------------------- names --
  private taskName(platformId: string, actionId: string): string {
    return `${platformId}_${actionId}`;
  }

  private makeMacroName(): string {
    const existing = this.macros.length;
    return `macro_${String(existing + 1).padStart(2, "0")}`;
  }

  // ------------------------------------------------------------ AI (هوش مصنوعی) --
  /** Appends a line to a mission's own agent log (mirrors AiAgent._alog). */
  private aiMissionLog(m: AiMission, level: string, msg: string): void {
    m.log.push({ t: ts(), level, msg });
    if (m.log.length > 40) m.log.splice(0, m.log.length - 40);
    m.updatedAt = now();
  }

  /** Invalidates any running simulation chain for a mission; returns the fresh token. */
  private aiStopChain(id: string): number {
    const entry = this.aiMissionTimers.get(id);
    if (entry) for (const h of entry.timers) clearTimeout(h);
    const token = (entry?.token ?? 0) + 1;
    this.aiMissionTimers.set(id, { token, timers: [] });
    return token;
  }

  /** Schedules one guarded link of a mission's simulation chain. */
  private aiSchedule(
    id: string,
    token: number,
    delayMs: number,
    fn: (m: AiMission) => void,
  ): void {
    const entry = this.aiMissionTimers.get(id);
    if (!entry || entry.token !== token) return;
    const h = setTimeout(() => {
      const e = this.aiMissionTimers.get(id);
      if (!e || e.token !== token) return;
      const idx = e.timers.indexOf(h);
      if (idx !== -1) e.timers.splice(idx, 1);
      const m = this.ai.missions.find((x) => x.id === id);
      if (m) fn(m);
    }, delayMs);
    entry.timers.push(h);
  }

  /** Compiles the final Persian report for a mission. */
  private aiCompileReport(m: AiMission): void {
    const byPlatform: Record<string, number> = {};
    for (const p of m.posts) {
      byPlatform[p.platform] = (byPlatform[p.platform] ?? 0) + 1;
    }
    const platNames = Object.keys(byPlatform).map((pid) => AI_PLATFORM_FA[pid] ?? pid);
    const summary =
      `• ${faDigits(m.posts.length)} پست در ${faDigits(platNames.length)} پلتفرم (${platNames.join("، ")}) تولید و زمان‌بندی شد.\n` +
      "• ساعات انتشار بر اساس پیک بازدید مخاطب ایرانی (۱۲، ۱۸ و ۲۱) چیده شده و سقف امن روزانه رعایت شده است.\n" +
      "• متن‌ها با لحن دوستانه و حرفه‌ای برای هر پلتفرم بازنویسی شده‌اند؛ هشتگ‌ها هم مطابق قواعد همان پلتفرم.\n\n" +
      "گام بعدی پیشنهادی: عملکرد پست‌ها را پس از اولین انتشار مرور کنید و ایدهٔ پربازدید را در هفتهٔ بعد تکرار کنید.\n" +
      "جمع‌بندی: ماموریت کامل شد — از این پس انتشارها خودکار اجرا می‌شوند و گزارش بعدی، پایان هفتهٔ آینده آماده است.";
    m.report = {
      summary,
      stats: {
        posts_generated: m.posts.length,
        scheduled: m.counts.scheduled,
        published_now: m.counts.published,
      },
    };
    m.updatedAt = now();
  }

  /** Staged content generation for the generate_content step (2 ideas → 2-4 posts). */
  private aiGeneratePosts(m: AiMission, done: () => void): void {
    const id = m.id;
    const token = this.aiMissionTimers.get(id)?.token ?? -1;
    const platforms = aiPickPlatforms(m.instruction);
    const ideas = [
      m.instruction.replace(/\s+/g, " ").trim().slice(0, 80),
      pick(AI_IDEA_POOL),
    ];
    const emitIdea = (i: number): void => {
      const idea = ideas[i];
      this.aiMissionLog(m, "info", `✍️ تولید محتوا برای ایده: «${idea.slice(0, 60)}»`);
      this.aiSchedule(id, token, 650, () => {
        const targets = i === 0 ? platforms : [platforms[0]];
        for (const pid of targets) {
          m.posts.push({
            id: `p${m.posts.length + 1}`,
            platform: pid,
            idea: idea.slice(0, 120),
            text: aiPostText(pid, idea),
            status: "draft",
          });
        }
        m.counts.posts = m.posts.length;
        this.aiMissionLog(
          m,
          "ok",
          `✅ ${faDigits(targets.length)} پست برای «${idea.slice(0, 40)}» تولید شد (مجموع: ${faDigits(m.posts.length)})`,
        );
        this.log(
          "ai",
          "info",
          `✍️ ${faDigits(targets.length)} پست برای «${idea.slice(0, 40)}» تولید شد (مجموع: ${faDigits(m.posts.length)})`,
        );
        if (i + 1 < ideas.length) {
          this.aiSchedule(id, token, 650, () => emitIdea(i + 1));
        } else {
          this.aiSchedule(id, token, 500, done);
        }
      });
    };
    emitIdea(0);
  }

  /**
   * Runs (or resumes) a mission's simulation chain:
   * planning → generate_content → schedule_publish → report → completed.
   * Every callback re-validates the chain token, so pause/cancel stops instantly.
   */
  private aiRunMission(id: string): void {
    const m0 = this.ai.missions.find((x) => x.id === id);
    if (!m0 || ["completed", "failed", "cancelled"].includes(m0.status)) return;
    const token = this.aiStopChain(id);
    const alive = (m: AiMission): boolean =>
      m.status !== "paused" &&
      !["completed", "failed", "cancelled"].includes(m.status) &&
      this.aiMissionTimers.get(id)?.token === token;

    const runStep = (m: AiMission, idx: number): void => {
      if (!alive(m) || !m.plan) return;
      const steps = m.plan.steps;
      if (idx >= steps.length) return;
      const step = steps[idx];
      m.status = "running";
      m.stepIndex = idx;
      this.aiMissionLog(
        m,
        "info",
        `▶ گام ${faDigits(idx + 1)} از ${faDigits(steps.length)}: ${AI_TOOL_FA[step.action] ?? step.action} — ${step.reason}`,
      );

      if (step.action === "generate_content") {
        // a re-run after pause must not duplicate drafts of the interrupted attempt
        m.posts = m.posts.filter((p) => p.status !== "draft");
        m.counts.posts = m.posts.length;
        this.aiGeneratePosts(m, () => {
          if (!alive(m)) return;
          step.status = "done";
          m.stepIndex = idx + 1;
          this.aiSchedule(id, token, AI_STEP_MS, (m2) => runStep(m2, idx + 1));
        });
        return;
      }

      if (step.action === "schedule_publish") {
        const drafts = m.posts.filter((p) => p.status === "draft");
        for (const p of drafts) p.status = "scheduled";
        m.counts.scheduled = m.posts.filter((p) => p.status === "scheduled").length;
        if (drafts.length > 0) {
          this.aiMissionLog(m, "ok", `📅 ${faDigits(drafts.length)} پست در صف انتشار قرار گرفت`);
          this.log("ai", "ok", `📅 ${faDigits(drafts.length)} پست در صف انتشار قرار گرفت — «${m.title}»`);
        } else {
          this.aiMissionLog(m, "warn", "پست آماده‌ای برای زمان‌بندی نیست (اول تولید محتوا)");
        }
        step.status = "done";
        m.stepIndex = idx + 1;
        this.aiSchedule(id, token, AI_STEP_MS, (m2) => runStep(m2, idx + 1));
        return;
      }

      // report — پایان ماموریت
      this.aiMissionLog(m, "info", "📝 در حال نوشتن گزارش مدیریتی…");
      this.aiSchedule(id, token, 1000, (m2) => {
        if (!alive(m2)) return;
        this.aiCompileReport(m2);
        this.aiMissionLog(m2, "ok", "✅ گزارش نهایی آماده است — تب هوش مصنوعی ← کارت ماموریت");
        this.log(
          "ai",
          "ok",
          `✅ ماموریت «${m2.title}» تمام شد — ${faDigits(m2.posts.length)} پست تولید شد`,
        );
        step.status = "done";
        m2.stepIndex = steps.length;
        m2.status = "completed";
        m2.updatedAt = now();
      });
    };

    if (!m0.plan) {
      this.aiSchedule(id, token, AI_PLAN_MS, (m) => {
        if (!alive(m)) return;
        m.title = aiTitle(m.instruction);
        m.plan = {
          title: m.title,
          analysis: aiAnalysis(m.instruction),
          steps: aiPlanSteps(m.instruction),
        };
        this.aiMissionLog(m, "ok", `📋 برنامه آماده شد: ${faDigits(m.plan.steps.length)} گام — ${m.title}`);
        this.log("ai", "ok", `📋 برنامه آماده شد: ${faDigits(m.plan.steps.length)} گام — ${m.title}`);
        if (m.autonomy === "manual") {
          m.status = "wait_approval";
          this.aiMissionLog(m, "warn", "⏸ سطح «پیشنهادی» فعال است — برنامه را ببینید و «تأیید و اجرا» را بزنید");
          return;
        }
        m.status = "running";
        this.aiSchedule(id, token, 700, (m2) => runStep(m2, 0));
      });
      return;
    }

    // resume / approve — از همان گامِ در میانه ادامه بده
    const resumeIdx = m0.plan ? Math.min(m0.stepIndex, m0.plan.steps.length - 1) : 0;
    this.aiSchedule(id, token, 600, (m2) => runStep(m2, resumeIdx));
  }

  // --------------------------------------------------------------- actions --
  dispatch(type: PanelActionType, payload: Record<string, unknown> = {}): {
    ok: boolean;
    message?: string;
    notify?: string;
    data?: unknown;
  } {
    const t = now();
    switch (type) {
      case "launch": {
        const id = String(payload.platformId ?? "");
        const p = this.platforms.get(id);
        if (!p) return { ok: false, message: "پلتفرم ناشناخته است" };
        if (p.running) return { ok: false, message: "مرورگر این پلتفرم از قبل باز است" };
        p.running = true;
        p.channel = p.channel ?? this.settings.channelFallbacks[0];
        p.lastActiveAt = t;
        this.log("playwright", "info", `resilient launch — trying: ${this.settings.channelFallbacks.join(" → ")}`);
        this.log("playwright", "ok", `channel=${p.channel} up (installed browser — no download needed)`);
        this.log("playwright", "info", `persistent context → ${p.profile} (headless=${this.settings.headless ? "on" : "off"})`);
        this.log(id, "ok", `browser opened — ${getPlatform(id).url}`);
        return { ok: true, message: `مرورگر ${getPlatform(id).name} باز شد` };
      }

      case "closeBrowser": {
        const id = String(payload.platformId ?? "");
        const p = this.platforms.get(id);
        if (!p) return { ok: false, message: "پلتفرم ناشناخته است" };
        if (!p.running) return { ok: false, message: "مرورگر این پلتفرم باز نیست" };
        p.running = false;
        this.log("playwright", "info", `closing context → ${p.profile}`);
        this.log(id, "ok", "browser closed — profile state saved to disk");
        return { ok: true, message: `مرورگر ${getPlatform(id).name} بسته شد` };
      }

      case "login": {
        const id = String(payload.platformId ?? "");
        const p = this.platforms.get(id);
        if (!p) return { ok: false, message: "پلتفرم ناشناخته است" };
        if (p.loggingIn) return { ok: false, message: "فرایند ورود از قبل در جریان است" };
        if (p.loggedIn) return { ok: false, message: "قبلاً وارد شده‌اید — ابتدا «خروج» بزنید" };
        p.loggingIn = true;
        p.loginStartedAt = t;
        p.loginDurationMs = randInt(8000, 11000);
        p.channel = this.settings.channelFallbacks[0];
        p.running = true;
        this.log("playwright", "info", `resilient launch — trying: ${this.settings.channelFallbacks.join(" → ")}`);
        this.log("playwright", "ok", `channel=${p.channel} up (installed browser — no download needed)`);
        this.log("stealth", "ok", "anti-detection script injected (webdriver, languages, plugins)");
        this.log(id, "info", "login page opened — لطفاً در پنجرهٔ بازشده وارد شوید");
        return { ok: true, message: `فرایند ورود ${getPlatform(id).name} شروع شد — در پنجرهٔ مرورگر وارد شوید` };
      }

      case "logout": {
        const id = String(payload.platformId ?? "");
        const p = this.platforms.get(id);
        if (!p) return { ok: false, message: "پلتفرم ناشناخته است" };
        if (!p.loggedIn) return { ok: false, message: "از قبل خارج بوده‌اید" };
        p.loggedIn = false;
        p.sessionAgeMin = 0;
        this.log(id, "warn", "session cleared — login required for next action");
        return { ok: true, message: `سشن ${getPlatform(id).name} پاک شد` };
      }

      case "createTask": {
        const platformId = String(payload.platformId ?? "instagram");
        const platform = CATALOG.find((p) => p.id === platformId);
        if (!platform) return { ok: false, message: "پلتفرم ناشناخته است" };
        const actionId = String(payload.actionId ?? platform.actions[0].id);
        const action = platform.actions.find((a) => a.id === actionId) ?? platform.actions[0];
        const engine = (payload.engine as EngineId) ?? "browser";
        const speed = (payload.speed as SpeedId) ?? "normal";
        const schedule = (payload.schedule as ScheduleSpec) ?? { type: "manual" };
        const runNow = payload.runNow !== false;
        const task: PanelTask = {
          id: ++this.taskSeq,
          name: this.taskName(platformId, actionId),
          platformId,
          actionId,
          actionLabel: action.label,
          engine,
          speed,
          params: {
            text: String(payload.text ?? ""),
            target: String(payload.target ?? ""),
            image: String(payload.image ?? ""),
          },
          status: "idle",
          progress: 0,
          steps: [],
          currentStep: 0,
          simDurationMs: 1,
          startedAt: null,
          runCount: 0,
          lastRunAt: null,
          lastDurationS: null,
          schedule,
          nextRunAt:
            schedule.type === "every" ? t + schedule.seconds * 1000 : null,
          createdAt: t,
        };
        this.tasks.unshift(task);
        this.log(
          "gate",
          "ok",
          `task created → ${task.name} (${platform.name} · ${action.label} · ${engine === "browser" ? "موتور مرورگر" : "موتور دسکتاپ"})`,
        );
        if (runNow) {
          this.startTask(task, t);
        } else if (schedule.type === "every") {
          this.log("scheduler", "info", `scheduled ${task.name} — every ${schedule.label}`);
        }
        return { ok: true, message: runNow ? `تسک «${task.name}» ساخته و اجرا شد` : `تسک «${task.name}» ساخته شد`, data: { taskId: task.id } };
      }

      case "runTask": {
        const task = this.tasks.find((x) => x.id === Number(payload.taskId));
        if (!task) return { ok: false, message: "تسک یافت نشد" };
        if (task.status === "running") return { ok: false, message: "تسک در حال اجراست" };
        const p = this.platforms.get(task.platformId);
        if (p && !p.loggedIn) {
          return { ok: false, message: `ابتدا وارد ${getPlatform(task.platformId).name} شوید` };
        }
        this.startTask(task, t);
        return { ok: true, message: `اجرای «${task.name}» شروع شد` };
      }

      case "stopTask": {
        const task = this.tasks.find((x) => x.id === Number(payload.taskId));
        if (!task) return { ok: false, message: "تسک یافت نشد" };
        if (task.status !== "running") return { ok: false, message: "تسک در حال اجرا نیست" };
        task.status = "idle";
        task.progress = 0;
        task.steps = [];
        task.nextRunAt = task.schedule.type === "every" ? t + task.schedule.seconds * 1000 : null;
        this.log("gate", "warn", `task aborted → ${task.name}`);
        return { ok: true, message: `«${task.name}» متوقف شد` };
      }

      case "deleteTask": {
        const idx = this.tasks.findIndex((x) => x.id === Number(payload.taskId));
        if (idx === -1) return { ok: false, message: "تسک یافت نشد" };
        const [removed] = this.tasks.splice(idx, 1);
        this.log("gate", "info", `task deleted → ${removed.name}`);
        return { ok: true, message: `تسک «${removed.name}» حذف شد` };
      }

      case "loadSampleTasks": {
        const samples: Array<{
          platformId: string;
          actionId: string;
          text: string;
          target: string;
          engine: EngineId;
          schedule: ScheduleSpec;
        }> = [
          {
            platformId: "instagram",
            actionId: "post_photo",
            text: "Hello World از پارس‌ایجنت 🤖 #automation",
            target: "",
            engine: "browser",
            schedule: { type: "manual" },
          },
          {
            platformId: "telegram",
            actionId: "send_message",
            text: "گزارش روزانه ثبت شد ✅",
            target: "ParsAgent Devs",
            engine: "browser",
            schedule: { type: "every", seconds: 300, label: "۵ دقیقه" },
          },
          {
            platformId: "bale",
            actionId: "send_message",
            text: "یادآوری جلسه ساعت ۱۴ ⏰",
            target: "تیم محصول",
            engine: "browser",
            schedule: { type: "daily", at: "09:30", label: "هر روز ۰۹:۳۰" },
          },
        ];
        for (const s of samples) {
          const platform = getPlatform(s.platformId);
          const action = platform.actions.find((a) => a.id === s.actionId) ?? platform.actions[0];
          this.tasks.unshift({
            id: ++this.taskSeq,
            name: this.taskName(s.platformId, s.actionId),
            platformId: s.platformId,
            actionId: s.actionId,
            actionLabel: action.label,
            engine: s.engine,
            speed: "normal",
            params: { text: s.text, target: s.target, image: "assets/photo.jpg" },
            status: "idle",
            progress: 0,
            steps: [],
            currentStep: 0,
            simDurationMs: 1,
            startedAt: null,
            runCount: 0,
            lastRunAt: null,
            lastDurationS: null,
            schedule: s.schedule,
            nextRunAt: s.schedule.type === "every" ? t + s.schedule.seconds * 1000 : null,
            createdAt: t,
          });
        }
        this.log("gate", "ok", "loaded sample tasks → tasks/examples.json (۳ تسک)");
        return { ok: true, message: "۳ تسک نمونه بارگذاری شد" };
      }

      case "recordStart": {
        if (this.recorderActive) return { ok: false, message: "ضبط از قبل فعال است" };
        this.recorderActive = true;
        this.recorderStartedAt = t;
        this.recorderEvents = [];
        this.log("desktop", "info", "recorder armed — pynput listeners attached");
        this.log("desktop", "ok", "recording… (F9 ذخیره، F10 لغو)");
        return { ok: true, message: "ضبط ماکرو شروع شد — در ویندوز واقعی با F9 تمام می‌شود" };
      }

      case "recordStop": {
        if (!this.recorderActive) return { ok: false, message: "ضبط فعال نیست" };
        this.recorderActive = false;
        this.log("desktop", "info", "listeners detached — flushing buffer");
        return { ok: true, message: `ضبط پایان یافت (${this.recorderEvents.length} رخداد)` };
      }

      case "recordClear": {
        this.recorderActive = false;
        this.recorderEvents = [];
        this.recorderStartedAt = null;
        this.log("desktop", "warn", "recording discarded (F10)");
        return { ok: true, message: "رخدادهای ضبط‌شده پاک شدند" };
      }

      case "saveMacro": {
        if (this.recorderEvents.length === 0) return { ok: false, message: "رخدادی برای ذخیره نیست" };
        this.recorderActive = false;
        const macro: Macro = {
          id: ++this.macroSeq,
          name: String(payload.name ?? "").trim() || this.makeMacroName(),
          events: [...this.recorderEvents],
          durationMs: Math.max(
            500,
            this.recorderEvents[this.recorderEvents.length - 1]?.t ?? 1000,
          ),
          createdAt: t,
        };
        this.macros.unshift(macro);
        this.recorderEvents = [];
        this.recorderStartedAt = null;
        this.log("desktop", "ok", `macro saved → macros/${macro.name}.json (${macro.events.length} events, ${(macro.durationMs / 1000).toFixed(1)}s)`);
        return { ok: true, message: `ماکرو «${macro.name}» ذخیره شد` };
      }

      case "deleteMacro": {
        const idx = this.macros.findIndex((m) => m.id === Number(payload.macroId));
        if (idx === -1) return { ok: false, message: "ماکرو یافت نشد" };
        const [removed] = this.macros.splice(idx, 1);
        if (this.playback?.macroId === removed.id) this.playback = null;
        this.log("desktop", "info", `macro deleted → macros/${removed.name}.json`);
        return { ok: true, message: `ماکرو «${removed.name}» حذف شد` };
      }

      case "playMacro": {
        const macro = this.macros.find((m) => m.id === Number(payload.macroId));
        if (!macro) return { ok: false, message: "ماکرو یافت نشد" };
        if (this.playback) return { ok: false, message: "یک بازپخش در جریان است" };
        const speed = Number(payload.speed ?? 1) || 1;
        this.playback = {
          macroId: macro.id,
          macroName: macro.name,
          speed,
          startedAt: t,
          durationMs: Math.max(600, macro.durationMs / speed),
          totalEvents: macro.events.length,
        };
        this.playbackLogged = 0;
        this.log("desktop", "info", `playing macros/${macro.name}.json (speed ×${speed})`);
        return { ok: true, message: `بازپخش «${macro.name}» با سرعت ×${speed} شروع شد` };
      }

      case "stopPlayback": {
        if (!this.playback) return { ok: false, message: "بازپخشی در جریان نیست" };
        this.log("desktop", "warn", `playback aborted → ${this.playback.macroName}`);
        this.playback = null;
        this.playbackLogged = 0;
        return { ok: true, message: "بازپخش متوقف شد" };
      }

      case "loadSampleMacro": {
        if (this.macros.some((m) => m.name === "نمونه-فرم-پر کردن")) {
          return { ok: false, message: "ماکروی نمونه قبلاً بارگذاری شده است" };
        }
        const events: MacroEvent[] = [];
        let time = 0;
        const pts: Array<[number, number]> = [
          [240, 220], [520, 190], [760, 260], [980, 420], [1180, 380],
          [1420, 300], [1520, 520], [1240, 640], [940, 720], [640, 660],
          [420, 760], [300, 560],
        ];
        pts.forEach(([x, y], i) => {
          events.push({ type: "move", x, y, t: Math.round(time) });
          time += rand(220, 420);
          if (i === 2 || i === 6 || i === 9) {
            events.push({ type: "click", x, y, button: "left", t: Math.round(time) });
            time += rand(260, 380);
          }
          if (i === 4) {
            events.push({ type: "hotkey", keys: ["ctrl", "a"], t: Math.round(time) });
            time += 240;
          }
        });
        SAMPLE_TEXTS[0]
          .slice(0, 12)
          .split("")
          .forEach((ch) => {
            events.push({ type: "key", key: ch === " " ? "Space" : ch, t: Math.round(time) });
            time += rand(90, 190);
          });
        events.push({ type: "hotkey", keys: ["ctrl", "s"], t: Math.round(time) });
        const macro: Macro = {
          id: ++this.macroSeq,
          name: "نمونه-فرم-پر-کردن",
          events,
          durationMs: time,
          createdAt: t,
        };
        this.macros.unshift(macro);
        this.log("desktop", "ok", `sample macro loaded → macros/${macro.name}.json (${events.length} events)`);
        return { ok: true, message: "ماکروی نمونه بارگذاری شد" };
      }

      case "systemAction": {
        return this.systemAction(String(payload.kind ?? ""), payload);
      }

      case "saveSettings": {
        const incoming = payload.settings as Partial<PanelSettings> | undefined;
        if (!incoming) return { ok: false, message: "تنظیماتی ارسال نشد" };
        const fb = Array.isArray(incoming.channelFallbacks)
          ? incoming.channelFallbacks.filter((c) => typeof c === "string" && c.trim())
          : this.settings.channelFallbacks;
        if (fb.length === 0) fb.push("msedge");
        this.settings = {
          channelFallbacks: fb.slice(0, 4),
          headless: Boolean(incoming.headless),
          proxy: String(incoming.proxy ?? ""),
          human: {
            enabled: incoming.human?.enabled ?? this.settings.human.enabled,
            minDelayS: Number(incoming.human?.minDelayS ?? this.settings.human.minDelayS),
            maxDelayS: Number(incoming.human?.maxDelayS ?? this.settings.human.maxDelayS),
            typingMinMs: Number(incoming.human?.typingMinMs ?? this.settings.human.typingMinMs),
            typingMaxMs: Number(incoming.human?.typingMaxMs ?? this.settings.human.typingMaxMs),
          },
          gateway: {
            url: String(incoming.gateway?.url ?? this.settings.gateway.url),
            token: String(incoming.gateway?.token ?? this.settings.gateway.token),
          },
        };
        this.log("gate", "ok", `config.json saved — fallbacks: ${this.settings.channelFallbacks.join(" → ")}`);
        return { ok: true, message: "تنظیمات ذخیره شد (config.json)" };
      }

      case "resetSettings": {
        this.settings = structuredClone(DEFAULT_SETTINGS);
        this.log("gate", "info", "settings restored to defaults");
        return { ok: true, message: "تنظیمات به حالت پیش‌فرض بازگشت" };
      }

      case "clearLogs": {
        this.logs = [];
        this.log("gate", "ok", "log buffer cleared");
        return { ok: true, message: "لاگ‌ها پاک شدند" };
      }

      case "aiSetProvider": {
        const id = String(payload.provider ?? "");
        const p = this.ai.catalog.find((x) => x.id === id);
        if (!p || p.models.length === 0) return { ok: false, message: "سرویس ناشناخته است" };
        this.ai.provider = p.id;
        if (!p.models.some((mm) => mm.id === this.ai.model)) {
          this.ai.model = p.models[0].id;
        }
        return { ok: true };
      }

      case "aiSetModel": {
        const id = String(payload.model ?? "");
        const p = this.ai.catalog.find((x) => x.id === this.ai.provider);
        if (!p || !p.models.some((mm) => mm.id === id)) {
          return { ok: false, message: "مدل ناشناخته است" };
        }
        this.ai.model = id;
        return { ok: true };
      }

      case "aiSetAutonomy": {
        const v = String(payload.autonomy ?? "");
        if (v !== "manual" && v !== "semi" && v !== "auto") {
          return { ok: false, message: "سطح خودمختاری نامعتبر است" };
        }
        this.ai.autonomy = v;
        return { ok: true };
      }

      case "aiCreateMission": {
        const instruction = String(payload.instruction ?? "").trim();
        if (!instruction) return { ok: false, message: "اول متن ماموریت/ایده را بنویسید" };
        const provider = this.ai.catalog.some((x) => x.id === payload.provider)
          ? String(payload.provider)
          : this.ai.provider;
        const pp = this.ai.catalog.find((x) => x.id === provider);
        const model = pp?.models.some((mm) => mm.id === payload.model)
          ? String(payload.model)
          : (pp?.models[0]?.id ?? this.ai.model);
        const rawAutonomy = String(payload.autonomy ?? this.ai.autonomy);
        const autonomy: "manual" | "semi" | "auto" =
          rawAutonomy === "manual" || rawAutonomy === "auto" ? rawAutonomy : "semi";
        const t0 = now();
        this.aiMissionSeq += 1;
        const mission: AiMission = {
          id: `m${String(this.aiMissionSeq).padStart(3, "0")}`,
          title: "ماموریت جدید",
          instruction,
          provider,
          model,
          autonomy,
          status: "planning",
          createdAt: t0,
          updatedAt: t0,
          stepIndex: 0,
          counts: { posts: 0, scheduled: 0, published: 0 },
          log: [],
          posts: [],
        };
        this.aiMissionLog(mission, "info", "🧠 در حال فهمیدن ماموریت و ساخت برنامهٔ اجرایی…");
        this.ai.missions.unshift(mission);
        this.log("ai", "ok", `🚀 ماموریت ساخته شد — مدل: ${provider}/${model} · خودمختاری: ${autonomy}`);
        this.aiRunMission(mission.id);
        return {
          ok: true,
          message: "🚀 ماموریت ساخته شد — ایجنت شروع کرد؛ کارت پایین را دنبال کنید",
          data: { missionId: mission.id },
        };
      }

      case "aiMissionControl": {
        const id = String(payload.missionId ?? "");
        const cmd = String(payload.cmd ?? "");
        const m = this.ai.missions.find((x) => x.id === id);
        if (!m) return { ok: false, message: "ماموریت پیدا نشد" };
        if (cmd === "approve") {
          if (m.status !== "wait_approval") {
            return { ok: false, message: "این ماموریت منتظر تأیید نیست" };
          }
          m.status = "running";
          this.aiMissionLog(m, "ok", "✅ کاربر برنامه را تأیید کرد — ادامه می‌دهم");
          this.log("ai", "ok", `✅ برنامهٔ «${m.title}» تأیید شد — اجرا ادامه می‌یابد`);
          this.aiRunMission(id);
          return { ok: true, message: "برنامه تأیید شد — اجرا ادامه می‌یابد" };
        }
        if (cmd === "pause") {
          if (m.status !== "running" && m.status !== "planning") {
            return { ok: false, message: "این ماموریت در حال اجرا نیست" };
          }
          this.aiStopChain(id);
          m.status = "paused";
          this.aiMissionLog(m, "warn", "⏸ درخواست توقف ثبت شد — با «ادامه» از همین‌جا ادامه دهید");
          this.log("ai", "warn", `⏸ ماموریت «${m.title}» متوقف شد`);
          return { ok: true, message: "ماموریت متوقف شد" };
        }
        if (cmd === "resume") {
          if (m.status !== "paused") return { ok: false, message: "این ماموریت قابل ادامه نیست" };
          m.status = "running";
          this.aiMissionLog(m, "ok", "▶ ادامهٔ اجرا");
          this.aiRunMission(id);
          return { ok: true, message: "اجرای ماموریت ادامه یافت" };
        }
        if (cmd === "cancel") {
          this.aiStopChain(id);
          m.status = "cancelled";
          this.aiMissionLog(m, "warn", "🛑 ماموریت لغو شد");
          this.log("ai", "warn", `🛑 ماموریت «${m.title}» لغو شد`);
          return { ok: true, message: "ماموریت لغو شد" };
        }
        return { ok: false, message: "فرمان ناشناخته" };
      }

      case "aiSendChat": {
        const content = String(payload.content ?? "").trim();
        if (!content) return { ok: false, message: "پیام خالی است" };
        this.ai.chat.push({ role: "user", content });
        const reply = AI_CHAT_REPLIES[this.aiChatReplySeq % AI_CHAT_REPLIES.length];
        this.aiChatReplySeq += 1;
        setTimeout(() => {
          this.ai.chat.push({ role: "assistant", content: reply });
        }, AI_CHAT_REPLY_MS);
        return { ok: true };
      }

      case "aiReset": {
        for (const id of this.aiMissionTimers.keys()) this.aiStopChain(id);
        this.ai = aiDefaultState();
        this.log("ai", "info", "بخش هوش مصنوعی به حالت پیش‌فرض بازگشت");
        return { ok: true, message: "بخش هوش مصنوعی به حالت اولیه بازگشت" };
      }

      default:
        return { ok: false, message: "دستور ناشناخته" };
    }
  }

  // -------------------------------------------------------- system actions --
  private systemAction(kind: string, payload: Record<string, unknown>): {
    ok: boolean;
    message?: string;
    notify?: string;
    data?: unknown;
  } {
    const t = now();
    switch (kind) {
      case "screenshot": {
        const stamp = `${new Date(t).getFullYear()}${pad(new Date(t).getMonth() + 1)}${pad(new Date(t).getDate())}_${pad(new Date(t).getHours())}${pad(new Date(t).getMinutes())}${pad(new Date(t).getSeconds())}`;
        const path = `data/screenshots/panel_${stamp}.png`;
        this.screenshotSeq += 1;
        this.log("desktop", "info", "capturing screen → mss.grab() (1920×1080)");
        this.log("desktop", "ok", `screenshot saved → ${path}`);
        return { ok: true, message: "اسکرین‌شات گرفته شد", data: { path } };
      }
      case "clipboardWrite": {
        const text = String(payload.text ?? "");
        this.system.clipboard = text;
        this.log("desktop", "ok", `clipboard set → ${text.length} chars`);
        return { ok: true, message: "متن در کلیپ‌بورد کپی شد", data: { text } };
      }
      case "clipboardRead": {
        this.log("desktop", "info", "clipboard read (pyperclip)");
        return { ok: true, message: "کلیپ‌بورد خوانده شد", data: { text: this.system.clipboard } };
      }
      case "openApp": {
        const app = String(payload.app ?? "notepad").trim() || "notepad";
        this.log("desktop", "info", `launching → ${app}.exe`);
        this.log("desktop", "ok", `window activated (pid ${randInt(1000, 9999)}, focus=true)`);
        return { ok: true, message: `برنامه «${app}» باز شد`, data: { app } };
      }
      case "hotkey": {
        const keys = Array.isArray(payload.keys) ? (payload.keys as string[]) : ["win", "r"];
        this.log("desktop", "info", `hotkey → ${keys.join("+")} (human delay ${Math.round(rand(this.settings.human.typingMinMs, this.settings.human.typingMaxMs))}ms)`);
        this.log("desktop", "ok", "hotkey delivered");
        return { ok: true, message: `هاتکی ${keys.join("+")} اجرا شد`, data: { keys } };
      }
      case "typeText": {
        const text = String(payload.text ?? "");
        if (!text.trim()) return { ok: false, message: "متنی برای تایپ وارد کنید" };
        const total = text.length * this.settings.human.typingMinMs;
        this.log("desktop", "info", `typing ${text.length} chars (${(total / 1000).toFixed(1)}s at ${this.settings.human.typingMinMs}–${this.settings.human.typingMaxMs}ms/char)`);
        this.log("desktop", "ok", "text delivered");
        return { ok: true, message: "متن تایپ شد", data: { length: text.length } };
      }
      case "clickAt": {
        const x = Math.round(Number(payload.x ?? 960));
        const y = Math.round(Number(payload.y ?? 540));
        if (Number.isNaN(x) || Number.isNaN(y)) return { ok: false, message: "مختصات نامعتبر است" };
        this.system.mouse = { x: clamp(x, 0, 1920), y: clamp(y, 0, 1080) };
        this.log("desktop", "info", `moving mouse → (${x}, ${y}) with jitter`);
        this.log("desktop", "ok", `click delivered (${x}, ${y})`);
        return { ok: true, message: `کلیک در (${x}، ${y}) انجام شد` };
      }
      case "wait": {
        const seconds = Math.min(60, Math.max(1, Math.round(Number(payload.seconds ?? 3))));
        this.log("scheduler", "info", `sleep(${seconds}s)`);
        this.log("scheduler", "ok", "wait completed");
        return { ok: true, message: `${seconds} ثانیه صبر شد`, data: { seconds } };
      }
      case "notify": {
        const message = String(payload.message ?? "").trim();
        if (!message) return { ok: false, message: "پیام اعلان را وارد کنید" };
        this.log("notify", "info", `windows toast → ${message}`);
        return { ok: true, message: "اعلان ویندوز ارسال شد", notify: message };
      }
      case "lock": {
        this.log("desktop", "warn", "hotkey win+l — workstation locked");
        return { ok: true, message: "دستور قفل صفحه ارسال شد (win+l)" };
      }
      default:
        return { ok: false, message: "اکشن سیستمی ناشناخته" };
    }
  }

  // ---------------------------------------------------------------- export --
  exportState(): PanelState {
    const activeTasks = this.tasks.filter((task) => task.status === "running").length;
    return {
      version: VERSION,
      mode: "simulator",
      startedAt: this.startedAt,
      system: { ...this.system, mouse: { ...this.system.mouse } },
      settings: structuredClone(this.settings),
      platforms: [...this.platforms.values()].map((p) => ({ ...p })),
      tasks: this.tasks.map((task) => ({ ...task, steps: task.steps.map((s) => ({ ...s })) })),
      macros: this.macros.map((m) => ({ ...m, events: m.events })),
      recorder: {
        active: this.recorderActive,
        startedAt: this.recorderStartedAt,
        events: this.recorderEvents,
      },
      playback: this.playback ? { ...this.playback } : null,
      logs: this.logs.slice(-220),
      ai: structuredClone(this.ai),
      stats: {
        activeTasks,
        doneTasks: this.tasks.filter((task) => task.status === "done").length,
        totalRuns: this.tasks.reduce((acc, task) => acc + task.runCount, 0),
        macroCount: this.macros.length,
        logCount: this.logs.length,
        openBrowsers: [...this.platforms.values()].filter((p) => p.running).length,
        loggedIn: [...this.platforms.values()].filter((p) => p.loggedIn).length,
      },
    };
  }
}

// ------------------------------------------------------------------ global --
// Survives dev-server HMR reloads like a proper singleton.
const g = globalThis as unknown as { __parsPanelStore?: PanelStore };

export function getPanelStore(): PanelStore {
  if (!g.__parsPanelStore) {
    g.__parsPanelStore = new PanelStore();
  }
  return g.__parsPanelStore;
}

export type { PanelLog };
export { logTimestamp };
