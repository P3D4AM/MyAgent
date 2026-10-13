"use client";

import * as React from "react";
import { Download, DownloadCloud, FileCode2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FadeIn, SectionHeader } from "./section-header";
import { faNumber, fetchAgentFiles } from "./data";

const CHIPS = ["Python 3.10+", "Playwright", "MIT License", "نسخهٔ ۲.۱۵.۰"];

export function DownloadSection() {
  const [stats, setStats] = React.useState<{
    totalFiles: number;
    totalLines: number;
  } | null>(null);

  React.useEffect(() => {
    fetchAgentFiles()
      .then((res) =>
        setStats({
          totalFiles: res.stats.totalFiles,
          totalLines: res.stats.totalLines,
        }),
      )
      .catch(() => setStats(null));
  }, []);

  return (
    <section className="py-16 sm:py-20">
      <div className="mx-auto w-full max-w-5xl px-4 sm:px-6 lg:px-8">
        <SectionHeader
          index="۰۸"
          en="download"
          title="آمادهٔ نصب روی ویندوز"
        />

        <FadeIn className="relative mt-12">
          {/* halo */}
          <div
            className="absolute -inset-6 rounded-[2rem] bg-emerald-500/10 blur-2xl"
            aria-hidden="true"
          />
          {/* gradient border */}
          <div className="relative rounded-3xl bg-gradient-to-l from-emerald-500/50 via-zinc-800 to-amber-400/40 p-[1.5px]">
            <div className="rounded-[calc(1.5rem-1.5px)] bg-zinc-950/95 px-6 py-10 text-center sm:px-12 sm:py-14">
              <span className="mx-auto flex size-16 items-center justify-center rounded-2xl bg-emerald-500/10 ring-1 ring-emerald-500/40">
                <DownloadCloud className="size-8 text-emerald-400" aria-hidden="true" />
              </span>

              <h3 className="mt-5 text-xl font-extrabold text-zinc-100 sm:text-2xl">
                دانلود پارس‌ایجنت
              </h3>
              <p className="mx-auto mt-3 max-w-md text-sm leading-7 text-zinc-400">
                پکیج کامل و آمادهٔ اجرا: سرور پنل محلی + رابط فارسی + لانچر
                گرافیکی + راهنمای کامل — استخراج کن، اجرا کن.
              </p>

              {stats ? (
                <p className="mt-4 text-xs text-zinc-500">
                  <span className="font-mono text-emerald-400/90">
                    {faNumber(stats.totalFiles)}
                  </span>{" "}
                  فایل ·{" "}
                  <span className="font-mono text-emerald-400/90">
                    {faNumber(stats.totalLines)}
                  </span>{" "}
                  خط کد پایتون و JSON
                </p>
              ) : null}

              <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
                <Button
                  asChild
                  size="lg"
                  className="h-13 w-full bg-emerald-500 px-8 text-base font-bold text-zinc-950 hover:bg-emerald-400 sm:w-auto"
                >
                  <a href="/api/download" download>
                    <Download className="size-5" aria-hidden="true" />
                    دانلود سورس کامل (ZIP)
                  </a>
                </Button>
                <Button
                  asChild
                  size="lg"
                  variant="outline"
                  className="h-13 w-full border-zinc-700 bg-transparent px-8 text-base text-zinc-200 hover:border-emerald-500/50 hover:bg-emerald-500/10 hover:text-emerald-300 sm:w-auto"
                >
                  <a href="#code">
                    <FileCode2 className="size-5" aria-hidden="true" />
                    مرور سورس‌کد
                  </a>
                </Button>
              </div>

              <div className="mt-8 flex flex-wrap items-center justify-center gap-2">
                {CHIPS.map((chip) => (
                  <Badge
                    key={chip}
                    variant="outline"
                    className="border-zinc-700 bg-zinc-900/60 px-3 py-1 text-xs text-zinc-300"
                  >
                    {chip}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
