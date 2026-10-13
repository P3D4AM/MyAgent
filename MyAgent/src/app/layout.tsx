import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";

export const metadata: Metadata = {
  title: "پارس‌ایجنت — ایجنت اتوماسیون هوشمند ویندوز",
  description:
    "پارس‌ایجنت، ایجنت متن‌باز اتوماسیون برای ویندوز؛ کنترل و ضبط موس و کیبورد، اتوماسیون وب در سطح کد با Playwright و حالت استلث — بهینه‌شده برای اینستاگرام، توییتر، تلگرام، فیسبوک، لینکدین و شبکه‌های ایرانی بله، روبیکا و ایتا.",
  keywords: [
    "پارس‌ایجنت",
    "ParsAgent",
    "اتوماسیون",
    "ویندوز",
    "Playwright",
    "PyAutoGUI",
    "ایجنت",
    "شبکه‌های اجتماعی",
  ],
  icons: {
    icon: "https://z-cdn.chatglm.cn/z-ai/static/logo.svg",
  },
  openGraph: {
    title: "پارس‌ایجنت — ایجنت اتوماسیون هوشمند ویندوز",
    description:
      "کنترل موس و کیبورد، ضبط ماکرو و اتوماسیون وب شبکه‌های اجتماعی در یک ایجنت متن‌باز.",
    siteName: "ParsAgent",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fa" dir="rtl" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        {/* eslint-disable-next-line @next/next/no-page-custom-font */}
        <link
          href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased bg-background text-foreground">
        {children}
        <Toaster theme="dark" position="bottom-left" dir="rtl" />
      </body>
    </html>
  );
}
