// -----------------------------------------------------------------------------
// ParsAgent Web Panel — shared types between the simulation store (server)
// and the React control panel (client).
// -----------------------------------------------------------------------------

import type { EngineId, SpeedId } from "@/components/agent/data";

export type PanelLogLevel = "info" | "ok" | "warn" | "error";

export interface PanelLog {
  id: number;
  /** HH:MM:SS (en-GB, 24h) */
  ts: string;
  tag: string;
  level: PanelLogLevel;
  text: string;
}

export interface PlatformRuntime {
  id: string;
  /** persistent-context browser is open for this platform */
  running: boolean;
  loggedIn: boolean;
  /** login flow in progress */
  loggingIn: boolean;
  loginStartedAt: number | null;
  loginDurationMs: number;
  /** resolved launch channel (msedge / chrome / chromium) */
  channel: string | null;
  /** data/profiles/<id> */
  profile: string;
  lastAction: string | null;
  lastActiveAt: number | null;
  /** session age in minutes (since login) */
  sessionAgeMin: number;
}

export interface TaskStepState {
  tag: string;
  level: PanelLogLevel;
  text: string;
  /** cumulative weight fraction where this step completes (0..1) */
  at: number;
  emitted: boolean;
}

export type TaskStatus = "idle" | "running" | "done";

export type ScheduleSpec =
  | { type: "manual" }
  | { type: "every"; seconds: number; label: string }
  | { type: "daily"; at: string; label: string };

export interface PanelTask {
  id: number;
  /** english task name used by the CLI: e.g. instagram_post_photo */
  name: string;
  platformId: string;
  actionId: string;
  actionLabel: string;
  engine: EngineId;
  speed: SpeedId;
  params: { text: string; target: string; image: string };
  status: TaskStatus;
  /** 0..1 */
  progress: number;
  steps: TaskStepState[];
  currentStep: number;
  simDurationMs: number;
  startedAt: number | null;
  runCount: number;
  lastRunAt: number | null;
  lastDurationS: number | null;
  schedule: ScheduleSpec;
  nextRunAt: number | null;
  createdAt: number;
}

export type MacroEventType = "move" | "click" | "key" | "scroll" | "hotkey";

export interface MacroEvent {
  type: MacroEventType;
  x?: number;
  y?: number;
  button?: "left" | "right";
  key?: string;
  keys?: string[];
  /** ms from recording start */
  t: number;
}

export interface Macro {
  id: number;
  name: string;
  events: MacroEvent[];
  durationMs: number;
  createdAt: number;
}

export interface PlaybackState {
  macroId: number;
  macroName: string;
  speed: number;
  startedAt: number;
  /** effective duration (already divided by speed) */
  durationMs: number;
  totalEvents: number;
}

export interface RecorderRuntime {
  active: boolean;
  startedAt: number | null;
  events: MacroEvent[];
}

export interface PanelSettings {
  channelFallbacks: string[];
  headless: boolean;
  proxy: string;
  human: {
    enabled: boolean;
    minDelayS: number;
    maxDelayS: number;
    typingMinMs: number;
    typingMaxMs: number;
  };
  gateway: {
    url: string;
    token: string;
  };
}

export interface SystemSnapshot {
  cpu: number;
  ram: number;
  mouse: { x: number; y: number };
  clipboard: string;
  resolution: { w: number; h: number };
  uptimeS: number;
}

export interface PanelStats {
  activeTasks: number;
  doneTasks: number;
  totalRuns: number;
  macroCount: number;
  logCount: number;
  openBrowsers: number;
  loggedIn: number;
}

/* -------------------------------------------------------------------------- */
/* هوش مصنوعی (AI agent) — mirrors parsagent/ai_agent.py                        */
/* -------------------------------------------------------------------------- */

export interface AiModelInfo {
  id: string;
  name: string;
  tag: string;
  note: string;
}

export interface AiProviderInfo {
  id: string;
  name: string;
  note: string;
  hasKey: boolean;
  models: AiModelInfo[];
}

export interface AiMissionStep {
  action: string;
  params: Record<string, unknown>;
  reason: string;
  status: "pending" | "running" | "done" | "failed";
}

export interface AiPost {
  id: string;
  platform: string;
  idea: string;
  text: string;
  status: string;
}

export interface AiMissionLogEntry {
  t: string;
  level: string;
  msg: string;
}

export interface AiMission {
  id: string;
  title: string;
  instruction: string;
  provider: string;
  model: string;
  autonomy: "manual" | "semi" | "auto";
  status:
    | "planning"
    | "wait_approval"
    | "running"
    | "paused"
    | "waiting"
    | "completed"
    | "failed"
    | "cancelled";
  createdAt: number;
  updatedAt: number;
  plan?: { title: string; analysis: string; steps: AiMissionStep[] };
  stepIndex: number;
  counts: { posts: number; scheduled: number; published: number };
  report?: {
    summary: string;
    stats: { posts_generated: number; scheduled: number; published_now: number };
  };
  log: AiMissionLogEntry[];
  posts: AiPost[];
}

export interface AiChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface AiPanelState {
  provider: string;
  model: string;
  autonomy: "manual" | "semi" | "auto";
  catalog: AiProviderInfo[];
  missions: AiMission[];
  chat: AiChatMessage[];
}

/** Full serializable snapshot returned by GET /api/panel/state */
export interface PanelState {
  version: string;
  mode: "simulator";
  startedAt: number;
  system: SystemSnapshot;
  settings: PanelSettings;
  platforms: PlatformRuntime[];
  tasks: PanelTask[];
  macros: Macro[];
  recorder: RecorderRuntime;
  playback: PlaybackState | null;
  logs: PanelLog[];
  stats: PanelStats;
  ai: AiPanelState;
}

export type PanelActionType =
  | "launch"
  | "closeBrowser"
  | "login"
  | "logout"
  | "createTask"
  | "runTask"
  | "stopTask"
  | "deleteTask"
  | "loadSampleTasks"
  | "recordStart"
  | "recordStop"
  | "recordClear"
  | "saveMacro"
  | "deleteMacro"
  | "playMacro"
  | "stopPlayback"
  | "loadSampleMacro"
  | "systemAction"
  | "saveSettings"
  | "resetSettings"
  | "clearLogs"
  | "aiSetProvider"
  | "aiSetModel"
  | "aiSetAutonomy"
  | "aiCreateMission"
  | "aiMissionControl"
  | "aiSendChat"
  | "aiReset";

export interface PanelActionResult {
  ok: boolean;
  message?: string;
  /** when set, the client should show a desktop-style toast */
  notify?: string;
  data?: unknown;
  state: PanelState;
}
