"use client";

// -----------------------------------------------------------------------------
// PanelProvider — polling state + action dispatch for the control panel.
// -----------------------------------------------------------------------------

import * as React from "react";
import { toast } from "sonner";
import type { PanelActionResult, PanelState } from "@/lib/panel/types";

export interface PanelDispatchResult {
  ok: boolean;
  message?: string;
  notify?: string;
  data?: unknown;
}

interface PanelContextValue {
  state: PanelState | null;
  connected: boolean;
  /** POST an action; toasts the returned message unless `silent`. */
  dispatch: (
    type: string,
    payload?: Record<string, unknown>,
    silent?: boolean,
  ) => Promise<PanelDispatchResult>;
  /** force an immediate state refresh */
  refresh: () => void;
}

const PanelContext = React.createContext<PanelContextValue | null>(null);

export function usePanel(): PanelContextValue {
  const ctx = React.useContext(PanelContext);
  if (!ctx) throw new Error("usePanel must be used inside <PanelProvider>");
  return ctx;
}

export function PanelProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = React.useState<PanelState | null>(null);
  const [connected, setConnected] = React.useState(false);
  const inflight = React.useRef(false);
  const prevTasks = React.useRef<Map<number, string>>(new Map());
  const prevNotifySent = React.useRef<Set<number>>(new Set());

  const applyState = React.useCallback((next: PanelState) => {
    // ---- toast transitions: task finished ----
    const nextMap = new Map<number, string>();
    for (const task of next.tasks) nextMap.set(task.id, task.status);
    const prev = prevTasks.current;
    for (const task of next.tasks) {
      const before = prev.get(task.id);
      if (before === "running" && task.status === "done") {
        toast.success(`تسک «${task.name}» کامل شد`, {
          description: `زمان اجرا: ${task.lastDurationS?.toFixed(1) ?? "?"} ثانیه · مجموع اجراها: ${task.runCount}`,
        });
      }
    }
    prevTasks.current = nextMap;
    setState(next);
  }, []);

  const refresh = React.useCallback(async () => {
    if (inflight.current) return;
    inflight.current = true;
    try {
      const res = await fetch("/api/panel/state", { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = (await res.json()) as PanelState;
      applyState(data);
      setConnected(true);
    } catch {
      setConnected(false);
    } finally {
      inflight.current = false;
    }
  }, [applyState]);

  React.useEffect(() => {
    void refresh();
    const id = window.setInterval(() => {
      if (document.visibilityState === "visible") void refresh();
    }, 1400);
    return () => window.clearInterval(id);
  }, [refresh]);

  const dispatch = React.useCallback(
    async (
      type: string,
      payload: Record<string, unknown> = {},
      silent = false,
    ): Promise<PanelDispatchResult> => {
      try {
        const res = await fetch("/api/panel/action", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ type, payload }),
        });
        const data = (await res.json()) as PanelActionResult;
        if (data.state) {
          setConnected(true);
          applyState(data.state);
        }
        if (!silent) {
          if (data.ok) {
            toast.success(data.message ?? "انجام شد");
          } else {
            toast.error(data.message ?? "خطا در انجام دستور");
          }
        }
        if (data.notify) {
          window.setTimeout(() => {
            toast(data.notify, {
              description: "اعلان ویندوز — plyer",
              icon: "🔔",
            });
          }, 350);
        }
        return { ok: data.ok, message: data.message, notify: data.notify, data: data.data };
      } catch {
        setConnected(false);
        if (!silent) toast.error("ارتباط با ایجنت برقرار نشد");
        return { ok: false };
      }
    },
    [applyState],
  );

  const value = React.useMemo<PanelContextValue>(
    () => ({ state, connected, dispatch, refresh }),
    [state, connected, dispatch, refresh],
  );

  return <PanelContext.Provider value={value}>{children}</PanelContext.Provider>;
}
