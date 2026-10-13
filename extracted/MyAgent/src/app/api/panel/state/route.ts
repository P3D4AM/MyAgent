import { NextResponse } from "next/server";
import { getPanelStore } from "@/lib/panel/store";

export const dynamic = "force-dynamic";

/** Advances the simulation one tick and returns the full panel snapshot. */
export async function GET() {
  const store = getPanelStore();
  store.tick();
  return NextResponse.json(store.exportState());
}
