"use client";

import {
  AlertTriangle,
  AppWindow,
  Keyboard,
  Package,
  Terminal,
} from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { FadeIn, SectionHeader } from "./section-header";
import { CopyButton } from "./copy-button";

const STEPS: { title: string; code: string; note?: string }[] = [
  {
    title: "نصب پایتون ۳.۱۰+",
    code: "winget install Python.Python.3.12",
    note: "در صورت نبود winget، آخرین نسخه را از python.org دانلود و نصب کنید (تیک Add to PATH را بزنید).",
  },
  {
    title: "اجرای لانچر گرافیکی",
    code: ':: دابل‌کلیک روی ParsAgent.bat\n:: یا معادل دستی:\npython launcher.py',
    note: "لانچر، نصب پیش‌نیازها و اجرا/توقف سرور پنل را با چند دکمه مدیریت می‌کند — بدون نیاز به ترمینال.",
  },
  {
    title: "اولین بار: نصب پیش‌نیازها",
    code: ':: در لانچر بزن:\n📦 نصب پیش‌نیازها',
    note: "همان pip install -r requirements.txt است با نمایش زندهٔ نصب. نصب کرومیوم معمولاً لازم نیست — لانچر مقاوم اول از Edge خود ویندوز استفاده می‌کند، بعد Chrome (msedge → chrome → chromium) و خطای 403 تحریمی را دور می‌زند.",
  },
  {
    title: "اجرای سرور ← پنل خودکار باز می‌شود",
    code: ':: در لانچر بزن:\n🚀 اجرای سرور\n:: مرورگر خودکار باز می‌شود:\nhttp://127.0.0.1:8765',
    note: "سرور فقط روی همین سیستم در دسترس است؛ از پنل، همهٔ پلتفرم‌ها/وظایف/ضبط/سیستم را با چند کلیک کنترل کن.",
  },
  {
    title: "سیستم بدون اینترنت؟ نصب آفلاین (۲.۵.۰)",
    code: ':: روی سیستم اینترنت‌دار، در لانچر:\n💾 ساخت بستهٔ آفلاین\n\n:: بعد از انتقال پروژه، روی سیستم بدون اینترنت:\n📀 نصب آفلاین',
    note: "همهٔ پیش‌نیازها (wheelها) و اختیاریاً کرومیوم داخل پوشهٔ offline_bundle پروژه ذخیره می‌شوند؛ سپس کل پروژه را با فلش ببرید و روی سیستم مقصد با یک دکمه، بدون حتی یک بایت دانلود نصب کنید. نصاب، نسخهٔ پایتون/۳۲-۶۴ بیتی/پایتون free-threaded (خطای cp313t و Rust) را با پیام فارسی چک می‌کند. معادل کنسلی: python launcher.py --build-bundle و --install-offline",
  },
];

function CodeBlock({ code }: { code: string }) {
  return (
    <div
      dir="ltr"
      className="relative mt-3 overflow-hidden rounded-lg border border-zinc-800 bg-zinc-950"
    >
      <pre className="overflow-x-auto p-4 pl-14 font-mono text-[13px] leading-7 text-emerald-200/90 scrollbar-thin">
        {code}
      </pre>
      <span className="absolute left-2 top-2">
        <CopyButton text={code} label="کپی دستور" />
      </span>
    </div>
  );
}

export function InstallGuide() {
  return (
    <section id="guide" className="scroll-mt-24 py-16 sm:py-20">
      <div className="mx-auto w-full max-w-4xl px-4 sm:px-6 lg:px-8">
        <SectionHeader
          index="۰۷"
          en="install"
          title="نصب در ۴ گام (+ بستهٔ آفلاین)"
          subtitle="از صفر تا پنل کنترل گرافیکی، کمتر از پنج دقیقه — فقط پایتون و ویندوز."
        />

        <ol className="mt-12 space-y-6">
          {STEPS.map((step, i) => (
            <FadeIn key={step.title} delay={i * 0.06}>
              <li className="relative flex gap-4">
                {/* connector line */}
                {i < STEPS.length - 1 ? (
                  <span
                    className="absolute bottom-[-24px] right-[17px] h-6 w-px bg-zinc-800"
                    aria-hidden="true"
                  />
                ) : null}
                <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-amber-400/15 text-sm font-extrabold text-amber-300 ring-1 ring-amber-400/40">
                  {["۱", "۲", "۳", "۴"][i]}
                </span>
                <div className="min-w-0 flex-1">
                  <h3 className="pt-1.5 text-base font-bold text-zinc-100">
                    {step.title}
                  </h3>
                  <CodeBlock code={step.code} />
                  {step.note ? (
                    <p className="mt-2 text-xs leading-6 text-zinc-500">{step.note}</p>
                  ) : null}
                </div>
              </li>
            </FadeIn>
          ))}
        </ol>

        {/* پیش‌نمایش پنل واقعی */}
        <FadeIn delay={0.08}>
          <div className="mt-8 flex flex-col gap-4 rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-5 sm:flex-row sm:items-center">
            <div className="flex-1">
              <h3 className="flex items-center gap-2 text-base font-bold text-zinc-100">
                <AppWindow className="size-5 text-emerald-300" aria-hidden="true" />
                پنل واقعی را از همین حالا ببین
              </h3>
              <p className="mt-2 text-xs leading-6 text-zinc-400 sm:text-sm">
                پنل کنترل پارس‌ایجنت روی سیستم خودت اجرا می‌شود (اینجا فقط پیش‌نمایش
                استاتیک ظاهر آن است — بدون سرور، دکمه‌ها اجرا نمی‌شوند). پس از اجرای
                لانچر و «اجرای سرور»، همین ظاهر با همهٔ امکانات در
                <span dir="ltr" className="mx-1 font-mono text-xs text-emerald-300">
                  http://127.0.0.1:8765
                </span>
                باز می‌شود.
              </p>
            </div>
            <a
              href="/panel.html"
              target="_blank"
              rel="noopener noreferrer"
              className="shrink-0 rounded-lg bg-emerald-500 px-5 py-3 text-sm font-extrabold text-zinc-950 transition hover:bg-emerald-400"
            >
              پیش‌نمایش پنل ↗
            </a>
          </div>
        </FadeIn>

        {/* extras */}
        <FadeIn delay={0.1}>
          <Accordion
            type="single"
            collapsible
            className="mt-10 rounded-xl border border-zinc-800 bg-zinc-900/50 px-5"
          >
            <AccordionItem value="run-direct" className="border-zinc-800">
              <AccordionTrigger className="py-4 text-right text-sm font-bold text-zinc-200 hover:text-emerald-300 hover:no-underline [&>svg]:text-zinc-500">
                <span className="flex items-center gap-2">
                  <Terminal className="size-4 text-amber-300" aria-hidden="true" />
                  اجرای مستقیم بدون لانچر
                </span>
              </AccordionTrigger>
              <AccordionContent className="pb-5 text-sm leading-7 text-zinc-400">
                برای اجرای مستقیم سرور پنل، در پوشهٔ برنامه تایپ کنید:{" "}
                <span dir="ltr" className="font-mono text-xs text-emerald-300">
                  python panel_server.py
                </span>{" "}
                — پنل روی{" "}
                <span dir="ltr" className="font-mono text-xs text-emerald-300">
                  http://127.0.0.1:8765
                </span>{" "}
                باز می‌شود. برای تغییر پورت، پیش از اجرا متغیر محیطی را ست کنید:
                <CodeBlock code={"python panel_server.py\n\n:: تغییر پورت (پیش از اجرا):\nset PANEL_PORT=8800\npython panel_server.py"} />
              </AccordionContent>
            </AccordionItem>
            <AccordionItem value="mirror" className="border-zinc-800">
              <AccordionTrigger className="py-4 text-right text-sm font-bold text-zinc-200 hover:text-emerald-300 hover:no-underline [&>svg]:text-zinc-500">
                <span className="flex items-center gap-2">
                  <Package className="size-4 text-amber-300" aria-hidden="true" />
                  نصب کرومیوم از آینه (ایران)
                </span>
              </AccordionTrigger>
              <AccordionContent className="pb-5 text-sm leading-7 text-zinc-400">
                فقط اگر نه Edge دارید نه Chrome — در آن صورت کرومیوم را از آینهٔ
                داخلی نصب کنید تا خطای 403 تحریمی را نبینید:
                <CodeBlock code={"set PLAYWRIGHT_DOWNLOAD_HOST=https://cdn.npmmirror.com/binaries/playwright\npython -m playwright install chromium"} />
              </AccordionContent>
            </AccordionItem>
            <AccordionItem value="data" className="border-b-0">
              <AccordionTrigger className="py-4 text-right text-sm font-bold text-zinc-200 hover:text-emerald-300 hover:no-underline [&>svg]:text-zinc-500">
                <span className="flex items-center gap-2">
                  <Keyboard className="size-4 text-amber-300" aria-hidden="true" />
                  داده‌ها کجا ذخیره می‌شوند؟
                </span>
              </AccordionTrigger>
              <AccordionContent className="pb-5 text-sm leading-7 text-zinc-400">
                همه‌چیز محلی است: <span dir="ltr" className="font-mono text-xs text-emerald-300">config/</span> (تنظیمات، حساب‌ها، زمان‌بندی‌ها)،{" "}
                <span dir="ltr" className="font-mono text-xs text-emerald-300">media/</span> (عکس/ویدیوها)،{" "}
                <span dir="ltr" className="font-mono text-xs text-emerald-300">macros/</span> (ماکروها) و{" "}
                <span dir="ltr" className="font-mono text-xs text-emerald-300">profiles/</span> (پروفایل مرورگر هر پلتفرم — لاگین‌ها ماندگارند).
                بکاپ = کپی همین پوشه‌ها.
                <CodeBlock code={"pars-agent/\n  panel_server.py   ← سرور پنل (FastAPI)\n  static/index.html ← رابط کاربری پنل\n  launcher.py       ← لانچر گرافیکی\n  ParsAgent.bat     ← اجرا با دابل‌کلیک\n  config/ media/ macros/ profiles/   ← داده‌ها (خودکار ساخته می‌شوند)"} />
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </FadeIn>

        {/* responsible use */}
        <FadeIn delay={0.15}>
          <div className="mt-8 flex items-start gap-3 rounded-xl border border-amber-400/30 bg-amber-400/5 p-4 sm:p-5">
            <AlertTriangle
              className="mt-0.5 size-5 shrink-0 text-amber-300"
              aria-hidden="true"
            />
            <p className="text-xs leading-6 text-amber-200/90 sm:text-sm sm:leading-7">
              استفادهٔ مسئولانه: پارس‌ایجنت فقط برای اتوماسیون حساب‌های شخصی و
              فعالیت‌های مجاز طراحی شده است. از آن برای اسپم، نقض قوانین پلتفرم‌ها
              یا هر فعالیت غیرقانونی استفاده نکنید؛ مسئولیت نحوهٔ استفاده کاملاً با
              شماست.
            </p>
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
