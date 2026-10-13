"use client";

// -----------------------------------------------------------------------------
// Platforms — per-platform control cards: browser launch, login flow,
// action shortcuts, persistent-profile info.
// -----------------------------------------------------------------------------

import * as React from "react";
import {
  ExternalLink,
  FolderOpen,
  LogIn,
  LogOut,
  MonitorX,
  Rocket,
  Wand2,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { usePanel } from "./panel-provider";
import { Chip, StatusBadge } from "./widgets";
import { PLATFORMS } from "@/components/agent/data";
import { PlatformIcon } from "@/components/agent/platform-icons";
import { cn } from "@/lib/utils";

export function PlatformsView({
  onRunAction,
}: {
  onRunAction: (platformId?: string, actionId?: string) => void;
}) {
  const { state, dispatch } = usePanel();
  if (!state) return null;

  return (
    <div className="grid gap-4 xl:grid-cols-2">
      {PLATFORMS.map((platform) => {
        const rt = state.platforms.find((x) => x.id === platform.id);
        if (!rt) return null;
        const loginProgress =
          rt.loggingIn && rt.loginStartedAt
            ? Math.min(
                97,
                Math.round(((Date.now() - rt.loginStartedAt) / rt.loginDurationMs) * 100),
              )
            : 0;

        return (
          <article
            key={platform.id}
            className={cn(
              "flex flex-col gap-4 rounded-xl border bg-zinc-900/50 p-5 transition-colors",
              rt.running ? "border-emerald-500/40" : "border-zinc-800",
            )}
          >
            {/* header */}
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-3">
                <span
                  className={cn(
                    "flex size-12 items-center justify-center rounded-xl ring-1",
                    "bg-emerald-500/10 text-emerald-300 ring-emerald-500/30",
                  )}
                >
                  <PlatformIcon id={platform.id} className="size-6" />
                </span>
                <div>
                  <h3 className="text-base font-extrabold text-zinc-100">{platform.name}</h3>
                  <a
                    href={platform.url}
                    target="_blank"
                    rel="noreferrer"
                    dir="ltr"
                    className="mt-0.5 inline-flex items-center gap-1 font-mono text-[10px] text-zinc-500 hover:text-emerald-400"
                  >
                    {platform.url}
                    <ExternalLink className="size-3" aria-hidden="true" />
                  </a>
                </div>
              </div>
              <div className="flex flex-col items-end gap-1.5">
                <StatusBadge
                  state={rt.running ? "ok" : "off"}
                  label={rt.running ? `مرورگر باز (${rt.channel})` : "مرورگر بسته"}
                />
                {rt.loggingIn ? (
                  <StatusBadge state="busy" label="در انتظار ورود شما…" />
                ) : (
                  <StatusBadge
                    state={rt.loggedIn ? "ok" : "warn"}
                    label={
                      rt.loggedIn
                        ? `سشن فعال (${Math.max(1, Math.round(rt.sessionAgeMin))} دقیقه)`
                        : "بدون سشن"
                    }
                  />
                )}
              </div>
            </div>

            {/* login progress */}
            {rt.loggingIn ? (
              <div>
                <Progress value={loginProgress} className="h-1.5 bg-zinc-800" />
                <p className="mt-1.5 text-[11px] text-amber-300/80">
                  پنجرهٔ مرورگر باز شده — پس از ورود، سشن ذخیره می‌شود.
                </p>
              </div>
            ) : null}

            {/* actions */}
            <div className="flex flex-wrap items-center gap-2">
              {rt.running ? (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => void dispatch("closeBrowser", { platformId: platform.id })}
                  className="h-8 border-zinc-800 bg-zinc-900/60 text-xs hover:bg-zinc-800"
                >
                  <MonitorX className="size-3.5" aria-hidden="true" />
                  بستن مرورگر
                </Button>
              ) : (
                <Button
                  size="sm"
                  onClick={() => void dispatch("launch", { platformId: platform.id })}
                  className="h-8 bg-emerald-500 text-xs text-zinc-950 hover:bg-emerald-400"
                >
                  <Rocket className="size-3.5" aria-hidden="true" />
                  اجرای مرورگر
                </Button>
              )}

              {rt.loggedIn ? (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => void dispatch("logout", { platformId: platform.id })}
                  className="h-8 border-rose-500/30 bg-rose-500/5 text-xs text-rose-300 hover:bg-rose-500/10"
                >
                  <LogOut className="size-3.5" aria-hidden="true" />
                  خروج (پاک کردن سشن)
                </Button>
              ) : (
                <Button
                  size="sm"
                  variant="outline"
                  disabled={rt.loggingIn}
                  onClick={() => void dispatch("login", { platformId: platform.id })}
                  className="h-8 border-amber-500/30 bg-amber-500/5 text-xs text-amber-300 hover:bg-amber-500/10"
                >
                  <LogIn className="size-3.5" aria-hidden="true" />
                  ورود اول + ذخیرهٔ سشن
                </Button>
              )}

              <Button
                size="sm"
                variant="outline"
                disabled={rt.loggingIn}
                onClick={() => onRunAction(platform.id)}
                className="h-8 border-zinc-800 bg-zinc-900/60 text-xs hover:bg-zinc-800"
              >
                <Wand2 className="size-3.5" aria-hidden="true" />
                اجرای اکشن…
              </Button>
            </div>

            {/* action chips */}
            <div className="flex flex-wrap gap-1.5">
              {platform.actions.map((a) => (
                <Chip
                  key={a.id}
                  onClick={() => onRunAction(platform.id, a.id)}
                >
                  {a.label}
                </Chip>
              ))}
            </div>

            {/* footer info */}
            <div className="flex items-center justify-between border-t border-zinc-800/70 pt-3 text-[10px] text-zinc-500">
              <span dir="ltr" className="inline-flex items-center gap-1 font-mono">
                <FolderOpen className="size-3" aria-hidden="true" />
                {rt.profile}
              </span>
              {rt.lastAction ? (
                <span className="text-zinc-600">آخرین اکشن: {rt.lastAction}</span>
              ) : (
                <span className="text-zinc-600">بدون فعالیت</span>
              )}
            </div>
          </article>
        );
      })}

      <CliNote />
    </div>
  );
}

/** Hint card aligned with the grid. */
function CliNote() {
  return (
    <aside className="flex flex-col justify-center gap-3 rounded-xl border border-dashed border-zinc-800 bg-zinc-900/30 p-5 xl:col-span-2">
      <div className="flex items-center gap-2 text-sm font-bold text-zinc-300">
        <X className="size-4 text-zinc-600" aria-hidden="true" />
        هر پلتفرم، پروفایل مرورگر مستقل خودش را دارد
      </div>
      <p className="text-xs leading-6 text-zinc-500">
        پارس‌ایجنت برای هر پلتفرم یک
        <span dir="ltr" className="mx-1 font-mono text-emerald-400/90">
          user_data_dir
        </span>
        جدا نگه می‌دارد؛ کوکی‌ها و لاگین‌ها بین پلتفرم‌ها قاطی نمی‌شوند و بعد از بستن مرورگر
        باقی می‌مانند. لانچر مقاوم هم به‌ترتیب Edge ← Chrome ← کرومیوم را امتحان می‌کند.
      </p>
    </aside>
  );
}
