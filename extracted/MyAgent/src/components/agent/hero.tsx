"use client";

import { motion } from "framer-motion";
import { Download, LayoutDashboard, Play, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { HeroTerminal } from "./terminal";
import { faDigits } from "./data";

const STATS = [
  { value: faDigits(8), label: "پلتفرم" },
  { value: faDigits(2), label: "موتور اتوماسیون" },
  { value: `${faDigits(30)}+`, label: "اکشن آماده" },
  { value: `${faDigits(100)}٪`, label: "متن‌باز" },
];

export function Hero({ onOpenPanel }: { onOpenPanel: () => void }) {
  const scrollToDemo = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    document.getElementById("demo")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section className="relative overflow-hidden">
      {/* background layers */}
      <div className="bg-grid absolute inset-0" aria-hidden="true" />
      <div className="glow absolute inset-0" aria-hidden="true" />
      <div
        className="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-zinc-950 to-transparent"
        aria-hidden="true"
      />

      <div className="relative mx-auto w-full max-w-7xl px-4 py-16 sm:px-6 sm:py-20 lg:px-8 lg:py-28">
        <div className="grid items-center gap-10 lg:grid-cols-2 lg:gap-14">
          {/* copy */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center lg:text-right"
          >
            <span className="inline-flex items-center gap-2 rounded-full border border-amber-400/30 bg-amber-400/10 px-3.5 py-1.5 text-xs font-medium text-amber-300">
              <Sparkles className="size-3.5" aria-hidden="true" />
              ایجنت اتوماسیون متن‌باز برای ویندوز
            </span>

            <h1 className="mt-5 text-3xl font-extrabold leading-[1.35] tracking-tight text-zinc-100 sm:text-4xl sm:leading-[1.3] lg:text-5xl lg:leading-[1.25]">
              دستیار <span className="text-gradient">اتوماسیون</span> ویندوز شما
            </h1>

            <p className="mx-auto mt-5 max-w-xl text-sm leading-8 text-zinc-400 sm:text-base lg:mx-0">
              پارس‌ایجنت موس و کیبورد را کنترل و ضبط می‌کند و وب‌سایت‌ها را بدون دخالت
              موس و کیبورد، در سطح کد هدایت می‌کند — بهینه‌شده برای اینستاگرام،
              توییتر، تلگرام، فیسبوک، لینکدین و شبکه‌های ایرانی بله، روبیکا و ایتا.
            </p>

            <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center lg:justify-start">
              <Button asChild size="lg" className="h-12 w-full bg-emerald-500 px-7 text-zinc-950 hover:bg-emerald-400 sm:w-auto">
                <a href="/api/download" download>
                  <Download className="size-5" aria-hidden="true" />
                  دانلود نسخه ویندوز
                </a>
              </Button>
              <Button
                size="lg"
                onClick={onOpenPanel}
                className="h-12 w-full border-emerald-500/40 bg-emerald-500/10 px-7 text-emerald-300 hover:bg-emerald-500/20 hover:text-emerald-200 sm:w-auto"
              >
                <LayoutDashboard className="size-5" aria-hidden="true" />
                ورود به پنل کنترل
              </Button>
              <Button
                asChild
                size="lg"
                variant="ghost"
                className="h-12 w-full px-6 text-zinc-400 hover:text-emerald-300 sm:w-auto"
              >
                <a href="#demo" onClick={scrollToDemo}>
                  <Play className="size-4" aria-hidden="true" />
                  دموی زنده
                </a>
              </Button>
            </div>

            {/* stats */}
            <dl className="mt-10 grid grid-cols-2 gap-4 sm:grid-cols-4">
              {STATS.map((stat, i) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 14 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.25 + i * 0.09 }}
                  className="rounded-xl border border-zinc-800/80 bg-zinc-900/50 px-4 py-3 text-center lg:text-right"
                >
                  <dt className="order-2 mt-1 block text-xs text-zinc-500">{stat.label}</dt>
                  <dd className="order-1 text-xl font-extrabold text-emerald-400">
                    {stat.value}
                  </dd>
                </motion.div>
              ))}
            </dl>
          </motion.div>

          {/* terminal */}
          <motion.div
            initial={{ opacity: 0, y: 32, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.15 }}
            className="relative"
          >
            <div
              className="absolute -inset-6 rounded-3xl bg-emerald-500/10 blur-2xl"
              aria-hidden="true"
            />
            <HeroTerminal className="relative" />
          </motion.div>
        </div>
      </div>
    </section>
  );
}
