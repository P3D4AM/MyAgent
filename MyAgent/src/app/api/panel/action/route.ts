import { NextRequest, NextResponse } from "next/server";
import { getPanelStore } from "@/lib/panel/store";
import type { PanelActionType } from "@/lib/panel/types";

export const dynamic = "force-dynamic";

/**
 * Dispatches a control action to the simulated agent and returns the
 * refreshed panel snapshot so the client can update in one round-trip.
 */
export async function POST(req: NextRequest) {
  let body: { type?: string; payload?: Record<string, unknown> };
  try {
    body = (await req.json()) as { type?: string; payload?: Record<string, unknown> };
  } catch {
    return NextResponse.json({ ok: false, message: "بدنهٔ درخواست نامعتبر است" }, { status: 400 });
  }

  if (!body.type) {
    return NextResponse.json({ ok: false, message: "نوع دستور مشخص نشده است" }, { status: 400 });
  }

  const store = getPanelStore();
  store.tick();
  const result = store.dispatch(body.type as PanelActionType, body.payload ?? {});
  store.tick();

  return NextResponse.json({
    ok: result.ok,
    message: result.message,
    notify: result.notify,
    data: result.data,
    state: store.exportState(),
  });
}
