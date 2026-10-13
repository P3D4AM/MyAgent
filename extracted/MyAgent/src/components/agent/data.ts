// -----------------------------------------------------------------------------
// ParsAgent demo data: platform/action catalog + fake run-log script builders.
// Used by the hero terminal, platforms grid and the interactive live demo.
// -----------------------------------------------------------------------------

export type EngineId = "browser" | "desktop";
export type SpeedId = "fast" | "normal" | "slow";

export const SPEEDS: Record<SpeedId, { label: string; mult: number }> = {
  fast: { label: "سریع", mult: 0.4 },
  normal: { label: "عادی", mult: 1 },
  slow: { label: "آهسته", mult: 1.8 },
};

export type ActionKind =
  | "post_photo"
  | "story"
  | "post"
  | "dm"
  | "follow"
  | "connect"
  | "like"
  | "like_latest"
  | "comment"
  | "retweet"
  | "channel"
  | "broadcast";

export interface ActionDef {
  id: string;
  label: string;
  kind: ActionKind;
  /** label of the free-text field (message / caption / comment) */
  textLabel?: string;
  /** label of the target field (username / chat / channel) */
  targetLabel?: string;
  /** show the image path field */
  needsImage?: boolean;
}

export interface PlatformDef {
  id: string; // also the log tag
  name: string; // Persian display name
  latin: string; // English name
  url: string;
  actions: ActionDef[];
}

export const PLATFORMS: PlatformDef[] = [
  {
    id: "instagram",
    name: "اینستاگرام",
    latin: "Instagram",
    url: "https://www.instagram.com/",
    actions: [
      {
        id: "post_photo",
        label: "انتشار عکس",
        kind: "post_photo",
        textLabel: "کپشن عکس",
        needsImage: true,
      },
      // ۲.۱۰.۰ — «انتشار استوری» از اینستاگرام حذف شد: نسخهٔ وب اینستاگرام اجازهٔ استوری نمی‌دهد (فقط اپ موبایل)
      {
        id: "send_dm",
        label: "ارسال دایرکت",
        kind: "dm",
        textLabel: "متن پیام",
        targetLabel: "نام کاربری گیرنده",
      },
      { id: "follow", label: "فالو", kind: "follow", targetLabel: "نام کاربری" },
      { id: "like_latest", label: "لایک آخرین پست", kind: "like_latest" },
      { id: "comment", label: "کامنت", kind: "comment", textLabel: "متن کامنت" },
    ],
  },
  {
    id: "twitter",
    name: "توییتر (X)",
    latin: "X / Twitter",
    url: "https://x.com/",
    actions: [
      { id: "post_tweet", label: "ارسال توییت", kind: "post", textLabel: "متن توییت" },
      {
        id: "send_dm",
        label: "ارسال دایرکت",
        kind: "dm",
        textLabel: "متن پیام",
        targetLabel: "نام کاربری گیرنده",
      },
      { id: "follow", label: "فالو", kind: "follow", targetLabel: "نام کاربری" },
      { id: "like", label: "لایک توییت", kind: "like" },
      { id: "retweet", label: "ریتوییت", kind: "retweet" },
    ],
  },
  {
    id: "telegram",
    name: "تلگرام",
    latin: "Telegram",
    url: "https://web.telegram.org/",
    actions: [
      {
        id: "send_message",
        label: "ارسال پیام",
        kind: "dm",
        textLabel: "متن پیام",
        targetLabel: "نام کاربری / چت",
      },
      {
        id: "post_channel",
        label: "پست کانال",
        kind: "channel",
        textLabel: "متن پست",
        targetLabel: "شناسه کانال",
      },
    ],
  },
  {
    id: "whatsapp",
    name: "واتساپ",
    latin: "WhatsApp",
    url: "https://web.whatsapp.com/",
    actions: [
      {
        id: "send_message",
        label: "ارسال پیام به مخاطب/گروه",
        kind: "dm",
        textLabel: "متن پیام",
        targetLabel: "نام مخاطب / گروه",
      },
    ],
  },
  {
    id: "facebook",
    name: "فیسبوک",
    latin: "Facebook",
    url: "https://www.facebook.com/",
    actions: [
      { id: "post_status", label: "پست پروفایل", kind: "post", textLabel: "متن پست" },
      // ۲.۱۰.۰ — فیسبوک تنها پلتفرمی است که استوری عکس از نسخهٔ وب می‌پذیرد
      { id: "upload_story", label: "انتشار استوری (عکس)", kind: "story", needsImage: true },
      { id: "like_post", label: "لایک پست", kind: "like" },
      { id: "comment", label: "کامنت", kind: "comment", textLabel: "متن کامنت" },
    ],
  },
  {
    id: "linkedin",
    name: "لینکدین",
    latin: "LinkedIn",
    url: "https://www.linkedin.com/",
    actions: [
      { id: "post", label: "پست فید", kind: "post", textLabel: "متن پست" },
      { id: "connect", label: "درخواست اتصال", kind: "connect", targetLabel: "نام کاربری" },
      {
        id: "send_dm",
        label: "ارسال پیام",
        kind: "dm",
        textLabel: "متن پیام",
        targetLabel: "نام کاربری",
      },
    ],
  },
  {
    id: "bale",
    name: "بله",
    latin: "Bale",
    url: "https://ble.ir/",
    actions: [
      {
        id: "send_message",
        label: "ارسال پیام",
        kind: "dm",
        textLabel: "متن پیام",
        targetLabel: "نام کاربری / چت",
      },
      {
        id: "post_channel",
        label: "پست کانال",
        kind: "channel",
        textLabel: "متن پست",
        targetLabel: "شناسه کانال",
      },
      {
        id: "broadcast",
        label: "ارسال گروهی",
        kind: "broadcast",
        textLabel: "متن پیام",
        targetLabel: "فهرست گیرندگان",
      },
    ],
  },
  {
    id: "rubika",
    name: "روبیکا",
    latin: "Rubika",
    url: "https://rubika.ir/",
    actions: [
      {
        id: "send_message",
        label: "ارسال پیام",
        kind: "dm",
        textLabel: "متن پیام",
        targetLabel: "نام کاربری / چت",
      },
      {
        id: "post_channel",
        label: "پست کانال",
        kind: "channel",
        textLabel: "متن پست",
        targetLabel: "شناسه کانال",
      },
    ],
  },
  {
    id: "eitaa",
    name: "ایتا",
    latin: "Eitaa",
    url: "https://web.eitaa.com/",
    actions: [
      {
        id: "send_message",
        label: "ارسال پیام",
        kind: "dm",
        textLabel: "متن پیام",
        targetLabel: "نام کاربری / چت",
      },
      {
        id: "post_channel",
        label: "پست کانال",
        kind: "channel",
        textLabel: "متن پست",
        targetLabel: "شناسه کانال",
      },
    ],
  },
];

export function getPlatform(id: string): PlatformDef {
  return PLATFORMS.find((p) => p.id === id) ?? PLATFORMS[0];
}

// -----------------------------------------------------------------------------
// Log script engine
// -----------------------------------------------------------------------------

export type LogLevel = "info" | "ok" | "warn" | "error";

export interface LogStep {
  tag: string;
  level: LogLevel;
  text: string;
  /** relative duration share (drives the progress bar and pacing) */
  weight: number;
  /** animate this line char-by-char when printed */
  typing?: boolean;
}

export interface DemoParams {
  text: string;
  target: string;
  image: string;
}

export interface BuildOptions {
  networkIssue: boolean;
  engine: EngineId;
}

const AGENT_VERSION = "v2.15.0";

function s(
  tag: string,
  level: LogLevel,
  text: string,
  weight: number,
  typing = false,
): LogStep {
  return { tag, level, text, weight, typing };
}

const postDoneByPlatform: Record<string, string> = {
  twitter: "tweet posted (id=17845321)",
  linkedin: "post published (visibility: connections)",
  facebook: "post published (privacy: friends)",
};

function browserActionSteps(
  tag: string,
  kind: ActionKind,
  platform: PlatformDef,
  params: DemoParams,
): LogStep[] {
  const len = Math.max(1, params.text.trim().length);
  const target = params.target.trim() || "@parsagent";
  const image = params.image.trim() || "assets/photo.jpg";

  switch (kind) {
    case "post_photo":
      return [
        s(tag, "info", `compose → clicking "Create new post"`, 1.0),
        s(tag, "ok", `media attached → ${image} (1080×1350)`, 0.9),
        s(tag, "info", `typing caption (${len} chars, 45ms/char)`, 1.6, true),
        s(tag, "info", "submitting → waiting for confirmation", 1.8),
        s(tag, "ok", "post published (media_id=3421)", 0.8),
      ];
    case "story":
      return [
        s(tag, "info", `opening camera roll → ${image} (1080×1920)`, 1.0),
        s(tag, "info", "uploading → progress bar detected", 1.2),
        s(tag, "info", "submitting → closing composer", 1.0),
        s(tag, "ok", "story published (expires in 24h)", 0.8),
      ];
    case "post":
      return [
        s(tag, "info", "compose → focusing post editor", 1.0),
        s(tag, "info", `typing text (${len} chars, 45ms/char)`, 1.6, true),
        s(tag, "info", "submitting → waiting for confirmation", 1.8),
        s(tag, "ok", postDoneByPlatform[platform.id] ?? "post published", 0.8),
      ];
    case "dm":
      return [
        s(tag, "info", `opening messages → ${target}`, 1.1),
        s(tag, "info", `typing message (${len} chars)`, 1.4, true),
        s(tag, "info", "sending → encrypting payload", 1.0),
        s(tag, "ok", "message delivered (seen: no)", 0.8),
      ];
    case "follow":
      return [
        s(tag, "info", `navigating → profile ${target}`, 1.2),
        s(tag, "ok", "profile loaded (followers: 12.4k)", 0.9),
        s(tag, "info", "clicking follow → waiting for state change", 1.3),
        s(tag, "ok", "follow confirmed (mutual: no)", 0.8),
      ];
    case "connect":
      return [
        s(tag, "info", `navigating → ${target} profile`, 1.2),
        s(tag, "ok", "profile loaded (connections: 3.1k)", 0.9),
        s(tag, "info", "clicking connect → note skipped", 1.3),
        s(tag, "ok", "invitation sent (pending)", 0.8),
      ];
    case "like":
    case "like_latest":
      return [
        s(tag, "info", "navigating → home feed", 1.2),
        s(tag, "info", "locating latest post (nth=1)", 1.0),
        s(tag, "info", "hover → double-tap like zone", 0.9),
        s(tag, "ok", "like confirmed (state=active)", 0.8),
      ];
    case "comment":
      return [
        s(tag, "info", "opening post → focusing comment box", 1.1),
        s(tag, "info", `typing comment (${len} chars)`, 1.4, true),
        s(tag, "info", "submitting comment", 1.1),
        s(tag, "ok", "comment posted (replies: 0)", 0.8),
      ];
    case "retweet":
      return [
        s(tag, "info", "locating target tweet (scroll: 2 screens)", 1.2),
        s(tag, "info", "clicking repost → quote option", 1.0),
        s(tag, "info", "confirming repost", 1.0),
        s(tag, "ok", "repost confirmed (visibility: public)", 0.8),
      ];
    case "channel":
      return [
        s(tag, "info", `navigating → chat ${target}`, 1.2),
        s(tag, "info", `typing broadcast (${len} chars)`, 1.4, true),
        s(tag, "info", "sending → waiting for server ack", 1.4),
        s(tag, "ok", "post published (msg_id=4821)", 0.8),
      ];
    case "broadcast":
      return [
        s(tag, "ok", "loading target list (24 recipients)", 0.9),
        s(tag, "info", "sending → batch 1/3 (8 users)", 1.2),
        s(tag, "info", "sending → batch 2/3 (8 users)", 1.2),
        s(tag, "info", "sending → batch 3/3 (8 users)", 1.2),
        s(tag, "ok", "broadcast done (24/24 OK)", 0.9),
      ];
  }
}

function desktopActionSteps(
  tag: string,
  kind: ActionKind,
  params: DemoParams,
): LogStep[] {
  const len = Math.max(1, params.text.trim().length);

  switch (kind) {
    case "post_photo":
      return [
        s("desktop", "info", "moving mouse → (842, 231)", 1.0),
        s("desktop", "info", "click → compose button", 0.8),
        s("desktop", "info", "hotkey ctrl+v (clipboard: image)", 1.0),
        s("desktop", "info", `typing caption (${len} chars, 35ms/char)`, 1.5, true),
        s("desktop", "ok", "screenshot match assets/composer.png (confidence 0.97)", 1.0),
        s("desktop", "info", "click → submit (918, 402)", 1.0),
        s(tag, "ok", "post published (composer closed)", 0.7),
      ];
    case "story":
      return [
        s("desktop", "info", "click → camera icon (97, 61)", 1.0),
        s("desktop", "info", "hotkey ctrl+v (clipboard: image)", 1.0),
        s("desktop", "ok", "screenshot match assets/story_editor.png (confidence 0.95)", 1.0),
        s("desktop", "info", "click → your story (918, 402)", 0.9),
        s(tag, "ok", "story published", 0.7),
      ];
    case "post":
      return [
        s("desktop", "info", "moving mouse → (761, 189)", 1.0),
        s("desktop", "info", "click → post editor", 0.8),
        s("desktop", "info", `typing text (${len} chars, 35ms/char)`, 1.5, true),
        s("desktop", "ok", "screenshot match assets/editor.png (confidence 0.96)", 1.0),
        s("desktop", "info", "hotkey ctrl+enter", 0.9),
        s(tag, "ok", "post published (editor cleared)", 0.7),
      ];
    case "dm":
      return [
        s("desktop", "info", "click → messages icon (152, 88)", 1.0),
        s("desktop", "info", "typing target in search box", 1.0),
        s("desktop", "info", "click → first result (388, 214)", 0.9),
        s("desktop", "info", `typing message (${len} chars, 35ms/char)`, 1.4, true),
        s("desktop", "info", "hotkey enter", 0.8),
        s(tag, "ok", "message sent (chat active)", 0.7),
      ];
    case "follow":
    case "connect":
      return [
        s("desktop", "info", "typing target in search bar", 1.0),
        s("desktop", "info", "hotkey enter", 0.8),
        s("desktop", "ok", "screenshot match assets/follow_btn.png (confidence 0.94)", 1.0),
        s("desktop", "info", "click → follow (1104, 312)", 0.9),
        s(tag, "ok", "follow confirmed (button state: following)", 0.7),
      ];
    case "like":
    case "like_latest":
      return [
        s("desktop", "info", "scrolling feed (wheel ×3)", 1.0),
        s("desktop", "ok", "screenshot match assets/like_btn.png (confidence 0.98)", 1.0),
        s("desktop", "info", "click → like (640, 512)", 0.9),
        s(tag, "ok", "like confirmed (icon filled)", 0.7),
      ];
    case "comment":
      return [
        s("desktop", "info", "click → comment box (984, 677)", 1.0),
        s("desktop", "info", `typing comment (${len} chars, 35ms/char)`, 1.4, true),
        s("desktop", "info", "hotkey enter", 0.8),
        s(tag, "ok", "comment posted", 0.7),
      ];
    case "retweet":
      return [
        s("desktop", "info", "click → repost (1140, 318)", 1.0),
        s("desktop", "info", "click → confirm repost (1140, 402)", 1.0),
        s(tag, "ok", "repost confirmed (icon active)", 0.7),
      ];
    case "channel":
      return [
        s("desktop", "info", "typing channel in search", 1.0),
        s("desktop", "info", "click → chat (388, 214)", 0.9),
        s("desktop", "info", `typing broadcast (${len} chars, 35ms/char)`, 1.4, true),
        s("desktop", "info", "hotkey enter", 0.8),
        s(tag, "ok", "post published (msg_id=4821)", 0.7),
      ];
    case "broadcast":
      return [
        s("desktop", "info", "opening contacts panel", 1.0),
        s("desktop", "info", "selecting recipients (24)", 1.0),
        s("desktop", "info", `typing broadcast (${len} chars, 35ms/char)`, 1.4, true),
        s("desktop", "info", "hotkey enter ×24", 1.2),
        s(tag, "ok", "broadcast done (24/24 OK)", 0.8),
      ];
  }
}

/**
 * Builds the full, plausible console log of a ParsAgent task run.
 * Deterministic: no network issue → clean success; issue on → one retry then success.
 */
export function buildScript(
  platform: PlatformDef,
  action: ActionDef,
  params: DemoParams,
  opts: BuildOptions,
): LogStep[] {
  const tag = platform.id;
  const steps: LogStep[] = [];

  steps.push(
    s("gate", "info", `pars-agent ${AGENT_VERSION} — task: ${platform.id}.${action.id}`, 0.6),
  );

  if (opts.engine === "browser") {
    steps.push(s("gate", "info", `engine=browser  mode=stealth  profile=${platform.id}`, 0.6));
    steps.push(s("playwright", "info", "resilient launch — trying: msedge → chrome → chromium", 0.9));
    steps.push(
      s("playwright", "ok", "channel=msedge up (installed Edge — no download needed)", 1.1),
    );
    steps.push(
      s("stealth", "ok", "anti-detection script injected (webdriver, languages, plugins)", 1.0),
    );
    steps.push(s(tag, "info", `restoring session → data/sessions/${platform.id}.json`, 0.8));
    steps.push(s(tag, "ok", "session valid — login skipped", 0.8));
    steps.push(s(tag, "info", `navigating → ${platform.url}`, 1.4));
    steps.push(...browserActionSteps(tag, action.kind, platform, params));
  } else {
    steps.push(s("gate", "info", "engine=desktop  mode=human-like  profile=main", 0.6));
    steps.push(s("desktop", "info", "activating window → chrome.exe (pid 4021)", 1.2));
    steps.push(s("desktop", "info", "input pipeline ready (jitter=on  failsafe=corner)", 0.8));
    steps.push(...desktopActionSteps(tag, action.kind, params));
  }

  // Inject a recoverable network hiccup right before the final confirmation.
  if (opts.networkIssue) {
    const at = steps.length - 1;
    const retry = opts.engine === "browser"
      ? [
          s("scheduler", "warn", "timeout waiting selector → retrying (1/2)", 1.2),
          s("playwright", "info", "reconnected (3.2s)", 1.0),
        ]
      : [
          s("desktop", "warn", "window lost focus → restoring", 1.2),
          s("desktop", "info", "window re-focused (2.1s)", 1.0),
        ];
    steps.splice(at, 0, ...retry);
  }

  steps.push(s("notify", "info", "windows toast → task result", 0.6));

  const totalWeight = steps.reduce((acc, st) => acc + st.weight, 0);
  const simSeconds = (totalWeight * 1.35).toFixed(1);
  steps.push(
    s(
      "gate",
      "ok",
      `task completed — ${steps.length}/${steps.length} steps OK in ${simSeconds}s`,
      0.5,
    ),
  );

  return steps;
}

// -----------------------------------------------------------------------------
// Shared helpers
// -----------------------------------------------------------------------------

/** Converts latin digits to Persian digits. */
export function faDigits(value: string | number): string {
  return String(value).replace(/[0-9]/g, (d) => "۰۱۲۳۴۵۶۷۸۹"[Number(d)]);
}

/** Formats a number with Persian digits + separators (fa-IR locale). */
export function faNumber(value: number): string {
  return value.toLocaleString("fa-IR");
}

/** `HH:MM:SS` timestamp (24h, en-GB) used inside terminal lines. */
export function logTimestamp(): string {
  return new Date().toLocaleTimeString("en-GB", { hour12: false });
}

// -----------------------------------------------------------------------------
// Agent files API (shared, cached across components)
// -----------------------------------------------------------------------------

export interface AgentFile {
  path: string;
  name: string;
  dir: string;
  language: string;
  size: number;
  lines: number;
  content: string;
}

export interface AgentFilesResponse {
  ok: boolean;
  stats: {
    totalFiles: number;
    totalSize: number;
    totalLines: number;
  };
  files: AgentFile[];
}

let filesCache: Promise<AgentFilesResponse> | null = null;

export function fetchAgentFiles(): Promise<AgentFilesResponse> {
  if (!filesCache) {
    filesCache = fetch("/api/agent/files").then((res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json() as Promise<AgentFilesResponse>;
    });
    // allow a retry after a failure
    filesCache.catch(() => {
      filesCache = null;
    });
  }
  return filesCache;
}
