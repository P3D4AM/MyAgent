"use client";

import { AlertTriangle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { PLATFORMS } from "./data";
import { PLATFORM_VISUALS, PlatformIcon } from "./platform-icons";
import { FadeIn, SectionHeader } from "./section-header";
import { cn } from "@/lib/utils";

/** Action chips displayed per platform card. */
const PLATFORM_CHIPS: Record<string, string[]> = {
  instagram: ["انتشار عکس", "استوری", "دایرکت", "فالو", "لایک", "کامنت"],
  twitter: ["توییت", "دایرکت", "فالو", "لایک", "ریتوییت"],
  telegram: ["پیام", "پست کانال"],
  facebook: ["پست پروفایل", "پست صفحه", "لایک", "کامنت"],
  linkedin: ["پست", "درخواست اتصال", "پیام"],
  bale: ["پیام", "پست کانال", "ارسال گروهی"],
  rubika: ["پیام", "پست کانال"],
  eitaa: ["پیام", "پست کانال"],
};

export function Platforms() {
  return (
    <section id="platforms" className="scroll-mt-24 py-16 sm:py-20">
      <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeader
          index="۰۳"
          en="platforms"
          title="ماژول‌های آمادهٔ شبکه‌های اجتماعی"
          subtitle="برای هر پلتفرم، ماژول اختصاصی با سلکتورهای چندگانه و fallback نوشته شده است؛ سشن شما بین اجراها حفظ می‌شود."
        />

        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4 lg:gap-5">
          {PLATFORMS.map((platform, i) => {
            const visual = PLATFORM_VISUALS[platform.id];
            return (
              <FadeIn key={platform.id} delay={i * 0.05} className="h-full">
                <Card className="h-full border-zinc-800/80 bg-zinc-900/50 transition-all duration-300 hover:-translate-y-1 hover:border-emerald-500/40 hover:bg-zinc-900/80">
                  <CardContent className="flex h-full flex-col gap-4 p-5">
                    <div className="flex items-center gap-3">
                      <span
                        className={cn(
                          "flex size-11 shrink-0 items-center justify-center rounded-full ring-1",
                          visual.cls,
                        )}
                        aria-hidden="true"
                      >
                        <PlatformIcon id={platform.id} className="size-5" />
                      </span>
                      <div>
                        <h3 className="text-sm font-bold text-zinc-100">{platform.name}</h3>
                        <p dir="ltr" className="font-mono text-[11px] text-zinc-500">
                          {platform.latin}
                        </p>
                      </div>
                    </div>

                    <div
                      className="flex flex-wrap gap-1.5"
                      aria-label={`اکشن‌های ${platform.name}`}
                    >
                      {(PLATFORM_CHIPS[platform.id] ?? []).map((chip) => (
                        <span
                          key={chip}
                          className="rounded-md border border-zinc-700 bg-zinc-800/80 px-2 py-0.5 text-[11px] text-zinc-300"
                        >
                          {chip}
                        </span>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </FadeIn>
            );
          })}
        </div>

        <FadeIn delay={0.15}>
          <div className="mt-8 flex items-start gap-3 rounded-xl border border-amber-400/30 bg-amber-400/5 p-4 sm:p-5">
            <AlertTriangle
              className="mt-0.5 size-5 shrink-0 text-amber-300"
              aria-hidden="true"
            />
            <p className="text-xs leading-6 text-amber-200/90 sm:text-sm sm:leading-7">
              خودکارسازی ممکن است با قوانین برخی پلتفرم‌ها در تعارض باشد؛ مسئولیت رعایت
              شرایط استفاده بر عهده کاربر است.
            </p>
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
