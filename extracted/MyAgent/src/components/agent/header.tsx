"use client";

import * as React from "react";
import { Bot, Download, LayoutDashboard, Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

const NAV_LINKS = [
  { href: "#features", label: "قابلیت‌ها" },
  { href: "#engines", label: "موتورها" },
  { href: "#platforms", label: "پلتفرم‌ها" },
  { href: "#demo", label: "دموی زنده" },
  { href: "#architecture", label: "معماری" },
  { href: "#code", label: "سورس‌کد" },
  { href: "#guide", label: "راهنما" },
];

export function Header({ onOpenPanel }: { onOpenPanel: () => void }) {
  const [scrolled, setScrolled] = React.useState(false);
  const [open, setOpen] = React.useState(false);

  React.useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={cn(
        "sticky top-0 z-50 w-full border-b bg-zinc-950/80 backdrop-blur-md transition-colors",
        scrolled ? "border-zinc-800" : "border-transparent",
      )}
    >
      <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between gap-3 px-4 sm:px-6 lg:px-8">
        {/* brand */}
        <a href="#" className="flex items-center gap-3" aria-label="پارس‌ایجنت — صفحهٔ اصلی">
          <span className="flex size-10 items-center justify-center rounded-lg bg-emerald-500/15 ring-1 ring-emerald-500/40">
            <Bot className="size-5.5 text-emerald-400" aria-hidden="true" />
          </span>
          <span className="flex flex-col leading-none">
            <span className="text-base font-extrabold text-zinc-100">پارس‌ایجنت</span>
            <span dir="ltr" className="mt-1 font-mono text-[10px] tracking-wider text-emerald-400/80">
              PARSAGENT · v2.15.0
            </span>
          </span>
        </a>

        {/* desktop nav */}
        <nav aria-label="ناوبری اصلی" className="hidden items-center gap-1 lg:flex">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="rounded-md px-3 py-2 text-sm text-zinc-400 transition-colors hover:bg-zinc-900 hover:text-emerald-300"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <Button
            onClick={onOpenPanel}
            className="h-11 border-emerald-500/40 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20 hover:text-emerald-200"
            variant="outline"
          >
            <LayoutDashboard className="size-4" aria-hidden="true" />
            <span className="hidden sm:inline">پنل کنترل</span>
            <span className="sm:hidden">پنل</span>
          </Button>
          <Button asChild className="h-11 bg-emerald-500 text-zinc-950 hover:bg-emerald-400">
            <a href="/api/download" download>
              <Download className="size-4" aria-hidden="true" />
              <span className="hidden sm:inline">دانلود ایجنت</span>
              <span className="sm:hidden">دانلود</span>
            </a>
          </Button>

          {/* mobile menu */}
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                className="size-11 border-zinc-800 bg-zinc-900/60 text-zinc-300 lg:hidden"
                aria-label="باز کردن منو"
              >
                <Menu className="size-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-72 border-zinc-800 bg-zinc-950 p-0">
              <SheetHeader className="border-b border-zinc-800">
                <SheetTitle className="text-right text-zinc-100">فهرست</SheetTitle>
              </SheetHeader>
              <nav aria-label="ناوبری موبایل" className="flex flex-col gap-1 p-3">
                {NAV_LINKS.map((link) => (
                  <a
                    key={link.href}
                    href={link.href}
                    onClick={() => setOpen(false)}
                    className="rounded-lg px-4 py-3 text-sm text-zinc-300 transition-colors hover:bg-zinc-900 hover:text-emerald-300"
                  >
                    {link.label}
                  </a>
                ))}
                <button
                  onClick={() => {
                    setOpen(false);
                    onOpenPanel();
                  }}
                  className="mt-1 flex items-center gap-2 rounded-lg bg-emerald-500/10 px-4 py-3 text-sm font-bold text-emerald-300 ring-1 ring-emerald-500/30 transition-colors hover:bg-emerald-500/20"
                >
                  <LayoutDashboard className="size-4" aria-hidden="true" />
                  ورود به پنل کنترل
                </button>
                <a
                  href="/api/download"
                  download
                  className="mt-2 flex items-center justify-center gap-2 rounded-lg bg-emerald-500 px-4 py-3 text-sm font-bold text-zinc-950 hover:bg-emerald-400"
                >
                  <Download className="size-4" aria-hidden="true" />
                  دانلود ایجنت
                </a>
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}
