"use client";

import { motion } from "framer-motion";
import {
  ArrowDown,
  Cpu,
  Database,
  FileCode2,
  FileJson,
  FileText,
  Globe,
  Image,
  LayoutDashboard,
  MonitorSmartphone,
  SquareTerminal,
  Workflow,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { SectionHeader } from "./section-header";
import { cn } from "@/lib/utils";

const fadeUp = {
  initial: { opacity: 0, y: 18 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-40px" },
};

function DiagramBox({
  icon: Icon,
  title,
  sub,
  tone = "emerald",
  className,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  sub: string;
  tone?: "emerald" | "amber";
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex items-center gap-3.5 rounded-xl border px-4 py-3.5 backdrop-blur-sm",
        tone === "emerald"
          ? "border-emerald-500/25 bg-emerald-500/[0.07]"
          : "border-amber-400/25 bg-amber-400/[0.07]",
        className,
      )}
    >
      <span
        className={cn(
          "flex size-11 shrink-0 items-center justify-center rounded-lg ring-1",
          tone === "emerald"
            ? "bg-emerald-500/10 text-emerald-300 ring-emerald-500/30"
            : "bg-amber-400/10 text-amber-300 ring-amber-400/30",
        )}
      >
        <Icon className="size-5" aria-hidden="true" />
      </span>
      <div className="min-w-0">
        <h4 className="text-sm font-bold text-zinc-100">{title}</h4>
        <p dir="ltr" className="truncate text-left font-mono text-[11px] text-zinc-500">
          {sub}
        </p>
      </div>
    </div>
  );
}

function Arrow({ delay = 0 }: { delay?: number }) {
  return (
    <motion.div {...fadeUp} transition={{ duration: 0.4, delay }} className="flex justify-center py-1.5">
      <ArrowDown className="size-5 text-emerald-500/60" aria-hidden="true" />
    </motion.div>
  );
}

const PLATFORM_MODULES = [
  "instagram.py",
  "twitter.py",
  "telegram.py",
  "facebook.py",
  "linkedin.py",
  "bale.py",
  "rubika.py",
  "eitaa.py",
];

const DATA_FLOWS = [
  { icon: Database, path: "data/sessions/", desc: "سشن‌های ماندگار مرورگر برای هر پلتفرم" },
  { icon: FileJson, path: "macros/", desc: "ماکروهای ضبط‌شدهٔ موس و کیبورد (JSON)" },
  { icon: FileText, path: "logs/", desc: "لاگ چرخشی اجرا با جزئیات کامل" },
  { icon: Image, path: "assets/", desc: "تصاویر مرجع برای تطبیق تصویری دسکتاپ" },
];

export function Architecture() {
  return (
    <section id="architecture" className="scroll-mt-24 py-16 sm:py-20">
      <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeader
          index="۰۵"
          en="architecture"
          title="معماری پارس‌ایجنت"
          subtitle="از دستور کاربر تا موتورهای اجرا و ماژول‌های پلتفرم — یک خط‌لولهٔ ساده و قابل‌توسعه."
        />

        <div className="mt-12 grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
          {/* diagram */}
          <div className="mx-auto w-full max-w-3xl">
            {/* layer A */}
            <motion.div
              {...fadeUp}
              transition={{ duration: 0.5 }}
              className="grid gap-3 sm:grid-cols-2"
            >
              <DiagramBox
                icon={SquareTerminal}
                title="رابط CLI"
                sub="run · record · play · schedule"
              />
              <DiagramBox
                icon={LayoutDashboard}
                title="پنل وب"
                sub="websocket gateway · telemetry"
              />
            </motion.div>

            <Arrow />

            {/* layer B */}
            <motion.div {...fadeUp} transition={{ duration: 0.5, delay: 0.05 }}>
              <DiagramBox
                icon={Workflow}
                title="موتور تسک + زمان‌بند"
                sub="TaskEngine (JSON tasks) · Scheduler (jitter)"
              />
            </motion.div>

            {/* two arrows */}
            <motion.div
              {...fadeUp}
              transition={{ duration: 0.4 }}
              className="grid gap-3 py-1.5 sm:grid-cols-2"
            >
              <div className="flex justify-center">
                <ArrowDown className="size-5 text-emerald-500/60" aria-hidden="true" />
              </div>
              <div className="hidden justify-center sm:flex">
                <ArrowDown className="size-5 text-emerald-500/60" aria-hidden="true" />
              </div>
            </motion.div>

            {/* layer C */}
            <motion.div
              {...fadeUp}
              transition={{ duration: 0.5, delay: 0.05 }}
              className="grid gap-3 sm:grid-cols-2"
            >
              <DiagramBox icon={Cpu} title="موتور دسکتاپ" sub="PyAutoGUI · pynput" tone="amber" />
              <DiagramBox icon={Globe} title="موتور مرورگر" sub="Playwright + Stealth" />
            </motion.div>

            <Arrow />

            {/* layer D */}
            <motion.div
              {...fadeUp}
              transition={{ duration: 0.5 }}
              className="rounded-xl border border-zinc-800/80 bg-zinc-900/40 p-4"
            >
              <p className="mb-3 text-center text-[11px] text-zinc-500">
                ماژول‌های پلتفرم
              </p>
              <div className="flex flex-wrap justify-center gap-2" dir="ltr">
                {PLATFORM_MODULES.map((mod) => (
                  <span
                    key={mod}
                    className="rounded-md border border-zinc-700/80 bg-zinc-800/70 px-2.5 py-1 font-mono text-[11px] text-emerald-200/90"
                  >
                    <FileCode2 className="me-1 inline size-3 text-emerald-400/80" aria-hidden="true" />
                    {mod}
                  </span>
                ))}
              </div>
            </motion.div>

            <Arrow />

            {/* layer E */}
            <motion.div {...fadeUp} transition={{ duration: 0.5 }}>
              <DiagramBox
                icon={MonitorSmartphone}
                title="اهداف"
                sub="windows apps · social networks"
                className="justify-center sm:justify-center"
              />
            </motion.div>
          </div>

          {/* side note */}
          <motion.div
            {...fadeUp}
            transition={{ duration: 0.5, delay: 0.15 }}
            className="lg:sticky lg:top-24"
          >
            <Card className="border-zinc-800 bg-zinc-900/50">
              <CardContent className="p-5 sm:p-6">
                <h3 className="text-base font-extrabold text-zinc-100">جریان داده‌ها</h3>
                <p className="mt-1.5 text-xs leading-6 text-zinc-500">
                  همهٔ داده‌های ایجنت به‌صورت محلی روی سیستم شما ذخیره می‌شود.
                </p>
                <ul className="mt-4 space-y-3.5">
                  {DATA_FLOWS.map((flow) => (
                    <li key={flow.path} className="flex items-start gap-3">
                      <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-zinc-800/80 ring-1 ring-zinc-700">
                        <flow.icon className="size-4 text-emerald-400" aria-hidden="true" />
                      </span>
                      <div className="min-w-0">
                        <p dir="ltr" className="text-left font-mono text-xs text-zinc-200">
                          {flow.path}
                        </p>
                        <p className="mt-0.5 text-xs leading-6 text-zinc-500">{flow.desc}</p>
                      </div>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
