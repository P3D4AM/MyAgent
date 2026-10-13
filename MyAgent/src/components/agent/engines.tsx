"use client";

import { Check, Cpu, Globe } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { FadeIn, SectionHeader } from "./section-header";

const ENGINES = [
  {
    id: "desktop",
    icon: Cpu,
    title: "موتور دسکتاپ",
    subtitle: "PyAutoGUI + pynput",
    tint: "amber",
    iconBox: "bg-amber-400/10 ring-amber-400/30 text-amber-300",
    bullets: [
      "ورودی واقعی سیستم — هر اپی را کنترل می‌کند",
      "تطبیق تصویری UI بدون نیاز به API",
      "ضبط و بازپخش ماکرو",
      "failsafe گوشهٔ صفحه برای توقف اضطراری",
    ],
    chip: "مناسب: اپ‌های ویندوز، محیط‌های بدون API",
    recommended: false,
  },
  {
    id: "browser",
    icon: Globe,
    title: "موتور مرورگر",
    subtitle: "Playwright + Stealth",
    tint: "emerald",
    iconBox: "bg-emerald-500/10 ring-emerald-500/30 text-emerald-400",
    bullets: [
      "عملیات DOM و شبکه بدون موس و کیبورد",
      "لانچر مقاوم: Edge ← Chrome ← کرومیوم",
      "headless و اجرا در پس‌زمینه",
      "پروفایل ماندگار جدا برای هر پلتفرم",
    ],
    chip: "مناسب: شبکه‌های اجتماعی و وب — حتی زیر تحریم",
    recommended: true,
  },
];

export function Engines() {
  return (
    <section id="engines" className="scroll-mt-24 py-16 sm:py-20">
      <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeader
          index="۰۲"
          en="engines"
          title="دو موتور، یک ایجنت"
          subtitle="بسته به هدف تسک، موتور مناسب را انتخاب کنید؛ پارس‌ایجنت با هر دو یک زبان مشترک دارد."
        />

        <div className="mt-12 grid gap-4 lg:grid-cols-2 lg:gap-6">
          {ENGINES.map((engine, i) => (
            <FadeIn key={engine.id} delay={i * 0.1} className="h-full">
              <Card className="relative flex h-full flex-col border-zinc-800/80 bg-zinc-900/50 transition-colors hover:border-zinc-700">
                <CardContent className="flex h-full flex-col p-6 sm:p-8">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-4">
                      <span className={`flex size-14 items-center justify-center rounded-2xl ring-1 ${engine.iconBox}`}>
                        <engine.icon className="size-7" aria-hidden="true" />
                      </span>
                      <div>
                        <h3 className="text-lg font-extrabold text-zinc-100">{engine.title}</h3>
                        <p dir="ltr" className="mt-1 font-mono text-xs text-zinc-500">
                          {engine.subtitle}
                        </p>
                      </div>
                    </div>
                    {engine.recommended ? (
                      <Badge className="shrink-0 bg-emerald-500 text-zinc-950 hover:bg-emerald-500">
                        پیشنهادی
                      </Badge>
                    ) : null}
                  </div>

                  <ul className="mt-6 flex-1 space-y-3">
                    {engine.bullets.map((bullet) => (
                      <li key={bullet} className="flex items-start gap-2.5 text-sm leading-7 text-zinc-300">
                        <Check
                          className={`mt-1.5 size-4 shrink-0 ${engine.recommended ? "text-emerald-400" : "text-amber-300"}`}
                          aria-hidden="true"
                        />
                        {bullet}
                      </li>
                    ))}
                  </ul>

                  <div className="mt-6 border-t border-zinc-800 pt-4">
                    <span
                      className={`inline-flex items-center rounded-md px-2.5 py-1 text-xs font-medium ring-1 ${
                        engine.recommended
                          ? "bg-emerald-500/10 text-emerald-300 ring-emerald-500/30"
                          : "bg-amber-400/10 text-amber-300 ring-amber-400/30"
                      }`}
                    >
                      {engine.chip}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </FadeIn>
          ))}
        </div>
      </div>
    </section>
  );
}
