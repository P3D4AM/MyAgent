"use client";

import { Bot, Github, Heart } from "lucide-react";

const QUICK_LINKS = [
  { href: "#features", label: "قابلیت‌ها" },
  { href: "#engines", label: "موتورها" },
  { href: "#platforms", label: "پلتفرم‌ها" },
  { href: "#demo", label: "دموی زنده" },
  { href: "#architecture", label: "معماری" },
  { href: "#code", label: "سورس‌کد" },
  { href: "#guide", label: "راهنمای نصب" },
];

export function Footer() {
  return (
    <footer className="mt-auto border-t border-zinc-800 bg-zinc-950">
      <div className="mx-auto w-full max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-10 md:grid-cols-3">
          {/* brand */}
          <div>
            <div className="flex items-center gap-3">
              <span className="flex size-10 items-center justify-center rounded-lg bg-emerald-500/15 ring-1 ring-emerald-500/40">
                <Bot className="size-5.5 text-emerald-400" aria-hidden="true" />
              </span>
              <div>
                <p className="text-base font-extrabold text-zinc-100">پارس‌ایجنت</p>
                <p dir="ltr" className="mt-0.5 font-mono text-[10px] tracking-wider text-emerald-400/80">
                  PARSAGENT · v2.15.0
                </p>
              </div>
            </div>
            <p className="mt-4 max-w-xs text-xs leading-6 text-zinc-500">
              ایجنت اتوماسیون متن‌باز ویندوز؛ کنترل موس و کیبورد، ضبط ماکرو و
              هدایت وب برای شبکه‌های اجتماعی — همهٔ پردازش‌ها به‌صورت محلی روی سیستم
              خودتان.
            </p>
          </div>

          {/* quick links */}
          <nav aria-label="لینک‌های سریع">
            <p className="text-sm font-bold text-zinc-200">دسترسی سریع</p>
            <ul className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2.5">
              {QUICK_LINKS.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-xs text-zinc-500 transition-colors hover:text-emerald-300"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>

          {/* disclaimer */}
          <div>
            <p className="text-sm font-bold text-zinc-200">سلب مسئولیت</p>
            <p className="mt-4 text-xs leading-6 text-zinc-500">
              پارس‌ایجنت صرفاً برای اتوماسیون قانونی حساب‌های شخصی است؛ رعایت
              قوانین پلتفرم‌ها بر عهده کاربر است. توسعه‌دهندگان هیچ مسئولیتی در
              قبال سوءاستفاده یا نقض شرایط استفادهٔ سرویس‌ها ندارند.
            </p>
          </div>
        </div>

        <div className="mt-10 flex flex-col items-center justify-between gap-4 border-t border-zinc-800/70 pt-6 sm:flex-row">
          <p className="text-xs text-zinc-600">
            © ۱۴۰۴ پارس‌ایجنت — ساخته‌شده با Next.js و پایتون
          </p>
          <div className="flex items-center gap-4 text-zinc-600">
            <Github className="size-4" aria-hidden="true" />
            <span className="flex items-center gap-1.5">
              <Heart className="size-4 text-rose-400/80" aria-hidden="true" />
              <span className="sr-only">ساخته‌شده با علاقه</span>
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
