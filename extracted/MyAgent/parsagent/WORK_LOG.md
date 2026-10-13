# Worklog — پروژه «پارس‌ایجنت» (ParsAgent)

پروژه: ساخت ایجنت اتوماسیون ویندوز (کنترل موس/کیبورد + ضبط ماکرو + اتوماسیون مرورگر با Playwright) به‌همراه پنل وب معرفی/کنترل در Next.js

- تاریخ شروع: 2025 (Asia/Tehran)
- محیط: Next.js 16 + TypeScript + Tailwind 4 + shadcn/ui — پورت 3000 (dev server در حال اجراست)

---
Task ID: 0
Agent: main-orchestrator (Z.ai Code)
Task: برنامه‌ریزی و راه‌اندازی پروژه

Work Log:
- بررسی ساختار پروژه (package.json، src/app، components/ui)
- تأیید اجرای dev server (پورت 3000، بدون خطا در dev.log)
- مشخص شدن وابستگی‌های موجود: react-syntax-highlighter، framer-motion، lucide-react، shadcn کامل

Stage Summary:
- معماری نهایی: (۱) پوشه `agent/` شامل سورس کامل ایجنت پایتون برای ویندوز (۲) دو API روت برای مرور کد و دانلود ZIP (۳) صفحه تک‌صفحه‌ای فارسی RTL به‌عنوان پنل معرفی/دمو
- نام محصول: ParsAgent (پارس‌ایجنت) نسخه ۱.۰.۰

---
Task ID: 1
Agent: main-orchestrator (Z.ai Code)
Task: نوشتن سورس کامل ایجنت ویندوز (Python) در پوشه agent/

Work Log:
- ایجاد ساختار agent/ شامل core/ ، platforms/ ، tasks/ ، macros/ ، data/ ، assets/
- core/logger.py — لاگ رنگی rich + فایل چرخشی logs/agent.log
- core/system_controller.py — کنترل موس/کیبورد واقعی با PyAutoGUI (jitter انسانی، failsafe، تطبیق تصویری)
- core/input_recorder.py — ضبط ورودی با pynput (F9 ذخیره/F10 لغو) + MacroPlayer بازپخش با سرعت دلخواه
- core/browser_engine.py — موتور Playwright: پروفایل ماندگار، تزریق STEALTH_JS (حذف navigator.webdriver و...)، تایپ انسانی، retry ناوبری، اسکرین‌شات خطا، export/import سشن
- core/task_engine.py — موتور تسک JSON با انواع گام platform/browser/desktop/wait/notify/shell + متغیر {{var}} + retry
- core/scheduler.py — زمان‌بندی every/daily با jitter
- core/gateway_client.py — کلاینت WebSocket کنترل از راه دور (hello/telemetry/log/result)
- core/notify.py — اعلان toast ویندوز با plyer
- platforms/: base + instagram + twitter + telegram + facebook + linkedin + بله + روبیکا + ایتا (هرکدام با login + اکشن‌های اصلی و سلکتورهای چندگانه fallback)
- main.py — CLI کامل: platforms / login / run / record / play / schedule / demo / gateway
- config.json ، requirements.txt ، build.bat (PyInstaller) ، tasks/examples.json (۵ تسک نمونه) ، README.md فارسی کامل

Stage Summary:
- کل سورس ایجنت در /home/z/my-project/agent (۲۰+ فایل پایتون/JSON)
- اعتبارسنجی: python3 -m py_compile همه فایل‌ها OK ، JSONها OK
- نصب adm-zip برای API دانلود ZIP در مرحله بعد

---
Task ID: 2
Agent: main-orchestrator (Z.ai Code)
Task: APIهای بک‌اند برای مرور سورس و دانلود ZIP

Work Log:
- نصب adm-zip + @types/adm-zip
- GET /api/agent/files — خواندن بازگشتی پوشه agent/ با مرتب‌سازی منطقی (main → README → core → platforms → tasks)، خروجی {stats, files[{path,name,dir,language,size,lines,content}]}
- GET /api/download — تولید ZIP پویا (pars-agent-v1.0.0.zip) از پوشه agent/ با adm-zip؛ رد کردن __pycache__
- تست: files=25 ، lines=3018 ، ZIP=44KB/34 entry — هر دو OK

Stage Summary:
- قرارداد API آماده است؛ فرانت‌اند باید /api/agent/files را در بخش «مرورگر سورس» و /api/download را در دکمه دانلود صدا بزند

---
Task ID: 3
Agent: full-stack-developer
Task: ساخت کامل فرانت‌اند تک‌صفحه‌ای فارسی RTL (پنل معرفی + دموی زنده پارس‌ایجنت)

Work Log:
- نصب @types/react-syntax-highlighter برای code viewer
- layout.tsx: تبدیل به `lang="fa" dir="rtl"`؛ حذف next/font (Geist)؛ افزودن preconnect + stylesheet گوگل‌فونت (Vazirmatn + JetBrains Mono) در head؛ متادیتای فارسی؛ Toaster از sonner با theme=dark و dir=rtl
- globals.css: فونت‌ساخت‌های `--font-sans`/`--font-mono` روی Vazirmatn/JetBrains Mono؛ کل توکن‌های shadcn به پالت dark mission-control (zinc-950/900/800 + emerald-500 primary + zinc text) — بدون indigo/blue؛ کلاس‌های سفارشی: text-gradient (emerald→amber)، bg-grid، glow، scrollbar-thin، cursor-blink؛ scroll-behavior smooth
- data.ts: کاتالوگ ۸ پلتفرم × اکشن‌ها (با فیلدهای شرطی text/target/image)، buildScript با اسکریپت‌ساز تمپلیتی برای هر kind اکشن در دو موتور browser/desktop (خطای شبکه → retry قطعی، weight-based pacing، خطوط typing انیمیشنی)؛ faDigits/faNumber/logTimestamp؛ fetchAgentFiles با کش ماژول‌سطحی
- کامپوننت‌ها در src/components/agent: header (sticky + backdrop-blur + Sheet موبایل + دکمه دانلود واقعی /api/download)، hero (bg-grid + glow + گرادیان + ۴ آمار + ترمینال)، terminal (TerminalWindow مشترک macOS-style + HeroTerminal با ماشین حالت تایپ async، loop بی‌نهایت، prefers-reduced-motion)، log-line (رنگ تگ‌ها: playwright=amber، platforms=emerald، desktop=orange، scheduler=yellow، notify=lime + مارکرهای ✓/!/✗)، features (۶ کارت)، engines (۲ کارت با badge «پیشنهادی»)، platforms (۸ کارت + چیپ‌های اکشن + هشدار amber)، demo (فرم کامل + موتور اجرای لاگ با progress/timer/step-counter/typing-line/stop/clear + toast موفقیت + بنر موفقیت فارسی)، recorder-demo (ضبط واقعی pointermove با throttle 30ms، بازپخش rAF با interpolation و سرعت 1.5x، مسیر SVG polyline + مارکرهای کلیک ping + شمارنده زنده — سازگار با قانون react-hooks/refs با flush state)، architecture (دیاگرام لایه‌ای با framer-motion whileInView + کارت جریان داده)، code-viewer (fetch + درخت فایل گروه‌بندی‌شده sidebar دسکتاپ / Select موبایل + Prism oneDark با شماره خط + کپی + skeleton + error/retry + نوار آمار fa-IR)، install-guide (۴ گام + Accordion شامل EXE/کلیدهای ضبط/CLI + هشدار مسئولانه)، download-section (کارت گرادیان emerald→amber + دکمه ZIP + آمار API)، footer (۳ ستون + sticky-bottom با mt-auto)
- page.tsx: ترکیب همه سکشن‌ها در wrapper `min-h-screen flex flex-col` با footer mt-auto
- تست مرورگر (agent-browser): صفحه بدون error/hydration-error لود شد؛ دموی زنده اجرا شد تا بنر «موفق» و toast؛ code-viewer با ۲۵ فایل رندر شد؛ ضبط‌کننده ضبط/بازپخش واقعی کار کرد؛ منوی Sheet موبایل OK؛ اسکرین‌شات full-page: پیکسل‌های emerald موجود، پیکسل blue-dominant صفر
- `bun run lint` بدون هیچ error/warning؛ dev.log بدون خطای کامپایل

Stage Summary:
- فرانت‌اند کامل فارسی RTL با پالت emerald/amber/zinc آماده است در `/` (پورت 3000)
- همهٔ مسیرهای فایل: src/app/{layout,page,globals.css} + ۱۵ فایل در src/components/agent/ (data, log-line, section-header, copy-button, terminal, header, hero, features, engines, platforms, platform-icons, demo, recorder-demo, architecture, code-viewer, install-guide, download-section, footer)
- APIهای Task 2 بدون تغییر مصرف شدند (GET /api/agent/files و GET /api/download)
- دمو کاملاً تعاملی است: انتخاب پلتفرم/اکشن/موتور/سرعت/خطای شبکه + لاگ واقع‌گرایانه با progress bar و زمان‌سنج؛ ضبط‌کننده ماکرو مرورگر نیز واقعی است
- انحراف کوچک از spec: Toaster نهایی از sonner استفاده کرد (نه toast قدیمی shadcn) چون دمو toast.success سانری لازم داشت؛ علامت‌های ✓ در خطوط لاگ به‌صورت prefix (طبق بخش icons) رندر می‌شوند نه suffix

---
Task ID: 4
Agent: main-orchestrator (Z.ai Code)
Task: بررسی نهایی با agent-browser + VLM و رفع خطاها

Work Log:
- باز کردن / با agent-browser: عنوان فارسی درست، صفر خطای کنسول/hydration
- تحلیل بصری ۶ اسکرین‌شات با VLM (بالا/میانی/موبایل/منو/فوتر/بخش‌های پایانی): RTL درست، بدون رنگ آبی/نیلی، بدون شکستگی
- تست مسیر طلایی دمو: انتخاب اینستاگرام + انتشار عکس + اجرا → لاگ استریم واقعی، نوار پیشرفت، بنر «تسک با موفقیت در ۱۱٫۴ ثانیه اجرا شد — ۱۴ از ۱۴ گام» ✓
- تست ضبط‌کننده: شروع ضبط → حرکت موس داخل کارد → ۱۳ رخداد ثبت → بازپخش با نقطه متحرک و مسیر SVG polyline (۱۳ نقطه) ✓
- تست مرورگر سورس: کلیک روی core/browser_engine.py → کد با شماره خط و هایلایت رندر شد ✓
- باگ پیدا شده: سرریز افقی ۸px در موبایل (390px) از عناصر glow تزئینی (-inset-6 blur-2xl در hero و download)
- رفع: افزودن `overflow-x: clip` برای html/body در globals.css → scrollWidth=390=clientWidth ✓
- تست منوی موبایل (Sheet): تمام لینک‌ها + دکمه دانلود ✓ — الگوی فوتر چسبان (min-h-screen flex-col + mt-auto) تأیید شد
- bun run lint: بدون خطا — dev.log: بدون خطا

Stage Summary:
- همه جریان‌های کلیدی در مرورگر واقعی تأیید شدند: دموی تسک، ضبط/بازپخش ماکرو، مرورگر کد، دانلود ZIP (curl 200)، واکنش‌گرایی موبایل/دسکتاپ، فوتر چسبان
- یک باگ رفع شد: سرریز افقی موبایل
- پروژه کامل و آماده تحویل است

---
Task ID: 5
Agent: main-orchestrator (Z.ai Code)
Task: پیاده‌سازی پیشنهاد معماری — لانچر مقاوم مرورگر (msedge → chrome → chromium) + پروفایل مستقل هر پلتفرم + رفع خطای 403 تحریمی

Work Log:
- بازنویسی core/browser_engine.py:
  * FALLBACK_CHANNELS = ("msedge", "chrome", "chromium") — قابل‌تنظیم از config.json (browser.channel اجبار یکی / browser.channel_fallbacks ترتیب دلخواه)
  * کلاس BrowserLaunchError با پیام راهنمای فارسی (۳ راه‌حل: Edge نصب‌شده / آینه / پروکسی) + گزارش خطای هر کانال
  * چند-پروفایلی: self._contexts به‌ازای هر پلتفرم (data/profiles/<platform>)، متد use_profile() با لانچ تنبل، پراپرتی _context با auto-open پروفایل main
  * start(headless, profile, lazy) — lazy برای TaskEngine تا کانتکست فقط با اولین گام پلتفرمی باز شود
  * بگ‌فیکس: __enter__ دیگر start را دوبار صدا نمی‌زند؛ import_session واقعاً کوکی‌ها را add_cookies می‌کند (قبلاً فقط export می‌کرد)
- core/task_engine.py: platform() حالا قبل از هر استفاده use_profile(name) را صدا می‌زند → new_page() همیشه در کانتکست همان پلتفرم باز می‌شود
- main.py:
  * build_engines → browser_factory با lazy=True
  * cmd_login → start(profile=args.platform) + نمایش کانال/پروفایل در خروجی؛ try/finally به‌جای with دابل-استارت
  * دستور جدید install: ست کردن PLAYWRIGHT_DOWNLOAD_HOST روی cdn.npmmirror.com و اجرای python -m playwright install (--browser/--mirror)
  * قالب پیش‌فرض config.json با channel/channel_fallbacks؛ docstring به‌روز
- فایل جدید agent/install_browsers.bat — نصب کرومیوم از آینه npmmirror (بدون فیلترشکن) با توضیح «اگر Edge/Chrome دارید اصلاً لازم نیست»
- config.json: افزودن "channel": null و "channel_fallbacks": ["msedge","chrome","chromium"]
- requirements.txt: کامنت هدر درباره لانچر مقاوم و دو روش نصب آینه‌ای
- README.md: جدول امکانات (لانچر مقاوم + پروفایل هر پلتفرم)، بخش کامل «نصب مرورگر در ایران — رفع خطای 403» با جدول ۳ راه‌حل، نصب ۴-گامی جدید، ردیف‌های عیب‌یابی (403 و crash پروفایل بعد از تعویض موتور)، python main.py install در استفاده سریع
- فرانت‌اند هم‌گام با واقعیت:
  * install-guide.tsx: گام ۳ → «نصب مرورگر — معمولاً لازم نیست!» با install_browsers.bat / python main.py install و نوت لانچر مقاوم؛ CLI accordion با install
  * engines.tsx: بولت «لانچر مقاوم: Edge ← Chrome ← کرومیوم» و «پروفایل ماندگار جدا برای هر پلتفرم» + چیپ «حتی زیر تحریم»
  * data.ts و terminal.tsx: خطوط لاگ دمو/هیرو به «resilient launch — trying: msedge → chrome → chromium» و «channel=msedge up (installed Edge — no download needed)» و profile=<platform>
- اعتبارسنجی:
  * python3 -m py_compile همه ۲۰ فایل پایتون OK؛ JSONها OK؛ اسکریپت AST: ۲۲ متد BrowserEngine، توکن‌های کلیدی و wiring (use_profile, cmd_install, PLAYWRIGHT_DOWNLOAD_HOST, lazy=True, profile=args.platform) تأیید
  * bun run lint بدون خطا
  * API: files=26 (قبلاً 25) و lines=3263؛ ZIP=49,585B با 35 entry شامل install_browsers.bat و browser_engine.py جدید
  * agent-browser: صفر خطای کنسول/هیدریشن؛ رندر متن‌های جدید (install-step، launcher-note، engines-bullet)؛ code-viewer فایل browser_engine.py جدید را با FALLBACK_CHANNELS/msedge/use_profile/BrowserLaunchError نشان داد؛ دموی زنده با لاگ‌های لانچر جدید تا بنر موفقیت و progress 100% اجرا شد؛ ترمینال هیرو «channel=msedge up» را تایپ کرد؛ موبایل 390px بدون سرریز افقی؛ فوتر چسبان درست (در بلندترین صفحه bottom=viewport، در بالای صفحه زیر دید)

Stage Summary:
- معماری پیشنهادی کامل پیاده و تأیید شد: ParsAgent حالا روی هر ویندوز ۱۰/۱۱ بدون هیچ دانلودی با Edge خود سیستم بالا می‌آید؛ در نبود آن Chrome؛ و در نهایت کرومیوم باندل (نصب از آینه بدون فیلترشکن با install_browsers.bat یا python main.py install)
- هر پلتفرم پروفایل ماندگار مستقل دارد (data/profiles/<platform>) — لاگین‌ها بین پلتفرم‌ها جدا و ماندگارند
- خطای 403 تحریمی کاربر به‌صورت معماری‌ای حل شد (نه فقط راهنما): fallback کانال + آینه + مستندسازی
- دو باگ قدیمی هم رفع شد: دابل-استارت در with، و import_session که export می‌کرد
- ZIP قابل دانلود از پنل (/api/download) و مرورگر سورس در صفحه، هر دو به‌روز و هم‌گام با سورس جدید

---
Task ID: 6
Agent: main-orchestrator (Z.ai Code)
Task: ساخت «پنل کنترل وب» کاربرپسند برای استفاده از همهٔ قابلیت‌های پارس‌ایجنت (درخواست کاربر: محیط یوزرفرندلی تحت وب)

Work Log:
- طراحی معماری: ایجنت واقعی پایتون روی ویندوز کاربر است → پنل به «شبیه‌ساز داخلی» متصل می‌شود که همهٔ قابلیت‌ها را وفادارانه شبیه‌سازی می‌کند (رفتار یکسان با python main.py gateway)
- بک‌اند:
  * src/lib/panel/types.ts — انواع مشترک سرور/کلاینت (PanelState, PanelTask, MacroEvent, PanelSettings…)
  * src/lib/panel/store.ts — موتور شبیه‌سازی singleton با globalThis (مقاوم به HMR): tick زمان‌محور (vitals random-walk، فلو ورود پله‌ای، پیشرفت تسک با انتشار لاگ گام‌ها، زمان‌بند every/daily، تولید رخداد ضبط، بازپخش با mouse-path)، dispatch کامل ۲۱ اکشن (launch/closeBrowser/login/logout/createTask/runTask/stopTask/deleteTask/loadSampleTasks/recordStart/recordStop/recordClear/saveMacro/deleteMacro/playMacro/stopPlayback/loadSampleMacro/systemAction/saveSettings/resetSettings/clearLogs)، تولید لاگ تسک با همان buildScript لندینگ (یکدستی کامل خروجی CLI و پنل)
  * GET /api/panel/state (tick + snapshot) و POST /api/panel/action (dispatch + state در یک round-trip) — هر دو force-dynamic
- فرانت‌اند (۱۲ فایل در src/components/agent/panel/):
  * panel-provider.tsx — polling هر ۱.۴ ثانیه (توقف در tab hidden) + dispatch با toast + toast انتقال وضعیت تسک (running→done)
  * widgets.tsx — StatCard، StatusDot/Badge، Chip، LogStream (auto-scroll هوشمند)، CliHint «معادل در ترمینال» + دکمه کپی، MiniBar، EmptyState، faUptime/faClock
  * control-panel.tsx — پوستهٔ mission-control: هدر sticky + سایدبار راست RTL (دسکتاپ) / پیل‌های افقی اسکرول (موبایل) + badge تعداد فعال + framer-motion ترنزیشن نماها + نوار وضعیت پایین (mt-auto) + بَج صادقانه «شبیه‌ساز داخلی» با tooltip راهنمای اتصال ایجنت واقعی
  * overview-view.tsx — ۴ آمار + اجرای سریع ۸ پلتفرم (toggle باز/بسته با tooltip) + vitals زنده (CPU/RAM/mouse/clipboard) + تسک‌های فعال با progress + جریان لاگ زنده
  * platforms-view.tsx — ۸ کارت: وضعیت مرورگر/سشن/کانال/پروفایل، دکمه‌های اجرا/بستن مرورگر/ورود اول/خروج/اجرای اکشن + چیپ اکشن‌ها + progress فلو ورود
  * action-runner.tsx — دیالوگ ساخت تسک: انتخاب پلتفرم/اکشن/موتور(browser|desktop)/سرعت انسانی/زمان‌بندی(دستی|هر۵m|۳۰m|۲h|روزانه) + گیت لاگین اینلاین (شروع ورود → progress → فرم خودکار ظاهر می‌شود) + پیش‌نمایش زندهٔ CLI
  * tasks-view.tsx — لیست تسک با status/progress/گام جاری/runCount/nextRunAt + اجرا/توقف/حذف + CLI هر تسک + بارگذاری ۳ تسک نمونه
  * recorder-view.tsx — صحنهٔ SVG 1920×1080 با grid + polyline مسیر + مارکرهای کلیک انیمیت + cursor بازپخش interpolate با rAF + لیست رخدادها + کتابخانهٔ ماکرو با سرعت ×0.5–×2 + یادداشت F9/F10 و pynput
  * system-view.tsx — ۷+ کارت دسکتاپ: اسکرین‌شات (مسیر خروجی)، کلیپ‌بورد خواندن/نوشتن، باز کردن برنامه، ۶ هاتکی آماده، تایپ متن، کلیک مختصات، اعلان ویندوز (toast واقعی وب)، انتظار، قفل + وضعیت زندهٔ موس
  * logs-view.tsx — فیلتر برچسب (داینامیک) + فیلتر سطح + خروجی .log + پاک‌کردن
  * settings-view.tsx — ویرایشگر ترتیب fallback chain (بالا/پایین/حذف/افزودن)، headless، پروکسی، اسلایدرهای تأخیر انسانی، gateway، پیش‌نمایش زندهٔ config.json، ذخیره/بازگردانی
- یکپارچه‌سازی: page.tsx سوییچ نما (landing↔panel) + دکمه «پنل کنترل» در Header (دسکتاپ+موبایل Sheet) + CTA «ورود به پنل کنترل» در Hero
- رفع باگ حین تست: faDigits از widgets صادر نشده بود → re-export (خطای ESM فقط در مرورگر ظاهر شد، نه در lint)
- اعتبارسنجی:
  * bun run lint: صفر خطا/هشدار
  * agent-browser E2E کامل: ورود پنل از Header ✓، اجرای سریع تلگرام (toast + تغییر دکمه) ✓، ActionRunner → اجرا → jump خودکار به وظایف + badge ✓، تکمیل تسک ۱۹.۷ ثانیه + toast ✓، فلو ورود «بله» کامل شد ✓، ضبط (۳۶ رخداد/۱۹.۴ ثانیه) → ذخیره → بازپخش ×۱.۵ با PLAY % ✓، اسکرین‌شات + اعلان ویندوز ✓، ذخیره تنظیمات ✓، خروج به لندینگ ✓
  * موبایل 390px: scrollW=clientW (بدون سرریز) + ناوبری پیل ✓؛ فوتر با mt-auto در محتوای بلند push می‌شود ✓
  * VLM روی ۴ اسکرین‌شات: RTL ✓، متن فارسی سالم ✓، بدون آبی/نیلی (پالت emerald) ✓، چیدمان منظم ✓، بدون شکستگی ✓
  * dev.log: صفر خطا — فقط GET/POST موفق panel API

Stage Summary:
- پنل کنترل وب کامل فارسی RTL با ۷ نما (کلی/پلتفرم‌ها/وظایف/ضبط/سیستم/لاگ/تنظیمات) روی همان مسیر / با سوییچ نما — همهٔ قابلیت‌های CLI اکنون با چند کلیک در مرورگر در دسترس است و هر اقدام «معادل ترمینال» خود را با دکمه کپی نشان می‌دهد
- موتور شبیه‌سازی وفادار: لانچر مقاوم (msedge→chrome→chromium از تنظیمات)، پروفایل ماندگار هر پلتفرم، فلو ورود با ذخیرهٔ سشن، زمان‌بند، ضبط/بازپخش ماکرو، اکشن‌های دسکتاپ — رفتار یکسان با ایجنت واقعی
- مسیر ارتقا به ایجنت واقعی مستند شده: python main.py gateway + config.json (درگاه در تنظیمات پنل قابل‌مشاهده)
- باگ رفع‌شده: export گم‌شدهٔ faDigits (۵ فایل درگیر)

---
Task ID: 7
Agent: main-orchestrator (Z.ai Code)
Task: درخواست کاربر — «لانچر/نصب GUI با دکمهٔ اجرای سرور که خودکار پنل وب را باز کند» + پنل واقعی (نه شبیه‌ساز) برای کنترل همهٔ قابلیت‌ها

Work Log:
- پاسخ به «روی کدوم صفحه»: پنل واقعی هیچ صفحهٔ اینترنتی نیست — روی سیستم خود کاربر روی http://127.0.0.1:8765 اجرا می‌شود
- معماری: FastAPI محلی (فقط 127.0.0.1) که مستقیماً ماژول‌های واقعی ایجنت را wrap می‌کند + تک‌نخم AgentWorker (چون Playwright sync بین‌نخ امن نیست) + لانچر tkinter
- agent/server.py (جدید، ~۱۲۰۰ خط):
  * قلاب لاگ: patch کردن core.logger.get_logger قبل از ایمپورت ماژول‌ها → همهٔ لاگرهای ایجنت (browser/desktop/recorder/tasks/پلتفرم‌ها) به WebSocket پنل استریم می‌شوند
  * AgentWorker: صف تک‌نخمی برای همهٔ عملیات مرورگری/تسک/پلتفرم
  * سیستم job با شناسه، وضعیت (running/done/failed/cancelled)، نتیجه، broadcast از WS + قابلیت لغو برای ماکروها
  * WebRecorder: ضبط pynput با شروع/توقف از وب یا F9/F10 — فرمت ماکرو ۱۰۰٪ سازگار با InputRecorder/MacroPlayer (پخش از CLI هم ممکن)
  * پخش‌کنندهٔ ماکروی قابل‌لغو + تایپ هوشمند فارسی (ASCII→typewrite، فارسی→کلیپ‌بورد+Ctrl+V) + نگاشت کلیدهای ویژه pynput→pyautogui + مدیریت درست modifierها (keyDown/keyUp)
  * REST کامل: health/state/platform(open/close/logged_in/screenshot)/action/run/tasks(run/save/content/load_samples)/record(start/stop/status)/macros(save/list/delete/play)/jobs/cancel + system(screenshot/mouse/keyboard/info/notify/open/cmd/lock/shutdown/abort) + config(get/save) + WS /ws/logs + سرو StaticFiles از web/
  * کاتالوگ اکشن‌های ۸ پلتفرم (از سورس واقعی platforms/ استخراج شد) با فیلدهای فارسی
- agent/web/index.html (جدید، ~۱۰۹۵ خط): پنل تک‌فایلی فارسی RTL بدون هیچ CDN (سازگار ایران/آفلاین) — ۷ نما: داشبورد/پلتفرم‌ها/وظایف/ضبط/سیستم/لاگ/تنظیمات؛ کلیک روی اسکرین‌شات = کلیک واقعی روی مختصات؛ حالت دمو در نبود سرور؛ فوتر چسبان؛ واکنش‌گرا (موبایل بدون سرریز)
- agent/launcher.py (جدید): لانچر گرافیکی tkinter — بررسی/نصب پیش‌نیازها (pip با لاگ زنده)، نصب کرومیوم از آینه npmmirror، اجرای uvicorn به‌صورت subprocess (بدون پنجرهٔ کنسول، NO_COLOR)، health-check → باز شدن خودکار پنل در مرورگر، توقف با taskkill /T، لینک پنل قابل کلیک
- agent/ParsAgent.bat (جدید): دابل‌کلیک → pythonw launcher.py (با fallback به python/py)
- core/browser_engine.py: افزودن open_profiles() و close_profile() برای پنل
- requirements.txt: + fastapi/uvicorn/pyperclip؛ README.md: مسیر لانچر به‌عنوان راه اول + فهرست فایل‌های جدید
- سندباکس: public/panel.html (پیش‌نمایش استاتیک پنل) + install-guide.tsx بازنویسی ۴ گام (لانچر گرافیکی مسیر اصلی) + کارت «پیش‌نمایش پنل» با لینک /panel.html
- اعتبارسنجی سخت‌گیرانه با هارنس (tests/tmp/agent_harness.py): اجرای واقعی server.py روی لینوکس با stub برای pyautogui/pynput/playwright/plyer:
  * GET / و /api/health و /api/state → 200؛ ۸ پلتفرم؛ فایل‌های تسک؛ ماژول‌ها
  * اجرای تسک notify از پنل → job done؛ WebSocket hello + push های job (running→done) + log واقعی موتور
  * ضبط شروع/توقف؛ ذخیرهٔ ماکرو با رد درستِ خالی؛ پخش ماکروی واقعی (events_played=4) + لغو (cancelled با پیام درست)
  * tasks/save + content + run file؛ platform/open → پروفایل telegram با channel=msedge در state؛ action/run wired؛ system/cmd + mouse + keyboard(فارسی) + info + config roundtrip همه OK
  * دو باگ واقعی پیدا و رفع شد: (۱) find_spec روی ماژول بی-spec → ValueError (روی ویندوز هم ممکن بود) — try/except در server و launcher؛ (۲) آرگومان جاافتادهٔ job_id در پخش ماکرو → پارامتر inject_id در _new_job
- agent-browser E2E: لندینگ بدون خطای کنسول؛ متن‌های جدید install (لانچر/پیش‌نمایش/8765) حاضر؛ /panel.html در حالت دمو: بنر زرد + ۷ تب سالم + ۸ کارت پلتفرم با اکشن‌ها + toast درست دمو؛ موبایل 390px بدون سرریز؛ پنل شبیه‌ساز قبلی بدون رگرسیون
- VLM روی ۳ اسکرین‌شات: RTL ✓، بدون شکستگی ✓، فوتر چسبان ✓، پالت emerald ✓، بنر + کارت‌ها ✓
- bun run lint: صفر خطا؛ py_compile همهٔ فایل‌های پایتون OK؛ ZIP دانلود: 43 entry شامل server.py/launcher.py/web/index.html/ParsAgent.bat

Stage Summary:
- ParsAgent حالا یک «اپ دسکتاپ واقعی» است: دابل‌کلیک ParsAgent.bat → دکمهٔ «اجرای سرور» → پنل کامل در مرورگر (http://127.0.0.1:8765) با کنترل واقعی مرورگرها/تسک‌ها/ضبط/دسکتاپ — همهٔ چیز از سورس قابل دانلود از سایت (ZIP به‌روز)
- پنل واقعی با شبیه‌ساز سایت متمایز است: پنل سایت فقط دمو است؛ پنل واقعی محلی است و همهٔ قابلیت‌های CLI را از مرورگر در دسترس می‌گذارد
- فرمت ماکروی پنل = فرمت CLI (سازگاری دوطرفه)؛ لاگ‌های ایجنت به‌صورت زنده در پنل استریم می‌شوند
- امنیت: سرور فقط روی 127.0.0.1؛ توقف اضطراری با گوشهٔ بالا-چپ موس (FAILSAFE)

---
Task ID: 8
Agent: main-orchestrator (Z.ai Code)
Task: درخواست کاربر — ۱) رفع نوار مزاحم (سرور محلی · بدون ارسال داده به بیرون) که وسط کارت‌های فیسبوک/دو کارت کناری و وسط داشبورد افتاده بود ۲) تنظیمات ضد شناسایی بات برای همهٔ پلتفرم‌ها با آخرین متدها ۳) ذخیرهٔ نام کاربری/رمز در تنظیمات + ورود خودکار + حل خودکار کپچا

Work Log:
- ریشه‌یابی باگ نوار: `html,body{height:100%}` قدِ body را قفل می‌کرد و `.wrap{flex:1;min-height:0}` اجازه می‌داد محتوای بلند روی فوتر overflow کند → کارت‌ها روی نوار وضعیت می‌افتادند
- رفع: حذف `html,body{height:100%}` + حذف `min-height:0` از `.wrap` (الگوی درست min-h-screen + mt-auto) در agent/web/index.html + public/panel.html — تأیید هندسی: footerTop=1278 > lastCardBottom=1260، overlap=false، ۸ کارت سالم
- agent/core/stealth.py (جدید، ~۴۵۰ خط): موتور ضد شناسایی v2 — ۱۰ ماژول JS (webdriver، chrome_runtime کامل با csi/loadTimes، Permissions، پلاگین‌های PDF واقعی ۵تایی + mimeTypes، languages/platform، hw_specs، نویز Canvas LSB، نویز AudioContext، ماسک WebGL با رندررهای ANGLE واقع‌نمای ویندوز، شیلد WebRTC) + سه سطح (basic/standard/max) + `disable_for` پلتفرمی + seed پایدار از نام پروفایل (اثر انگشت بین اجراها ثابت) + webrtc با پروکسی خودکار روشن + PROBE_JS برای تست و evaluate_probe مقاوم
- agent/core/credentials.py (جدید): مخزن data/credentials.json با FIELDS برای ۸ پلتفرم، merge-semantics (خالی=پاک، None=دست‌نزن)، masked() (رمز هرگز برنمی‌گردد)، fallback به config.json قدیمی، و totp_code با HMAC-SHA1 استاندارد RFC6238 بدون هیچ وابستگی
- agent/core/captcha.py (جدید، ~۳۰۰ خط): CaptchaSolver سازگار با پروتکل 2captcha/rucaptcha (urllib خالص، multipart برای base64، پول با مهلت) + detect_captcha در صفحه (recaptcha/hcaptcha/turnstile/funcaptcha/کپچای تصویری با استخراج sitekey از data-sitekey/URL/HTML) + solve_page_captcha با تزریق توکن و callback و پُرکردن کپچای تصویری
- agent/platforms/base.py: LOGIN_SELECTORS برای هر ۸ پلتفرم (user/pass/next/submit/code با کاندیداهای چندگانه) + BasePlatform.auto_login(creds, solver): فلوی کامل — is_logged_in → تایپ کاربر → دکمهٔ بعدی → رمز (secret) → submit/Enter → تشخیص+حل+تزریق کپچا → کد TOTP خودکار یا needs=code (SMS در پنجرهٔ باز) → رد کردن دیالوگ ذخیرهٔ ورود → بررسی نتیجه + export_session
- agent/core/browser_engine.py: اتصال به stealth.py — args از stealth_launch_args (شامل --disable-blink-features=AutomationControlled) و ctx.add_init_script(build_stealth_js(config, profile)) per-profile + لاگ stealth=✓
- agent/server.py v1.2.0: اندپوینت‌های جدید POST /api/platform/login، GET/POST /api/credentials (+delete)، POST /api/stealth/probe (تست ۷ نشانه در صفحهٔ محلی file://data/stealth-probe.html)، POST /api/stealth/test (bot.sannysoft.com + browserleaks در پروفایل)؛ state شامل credentials و has_creds در کاتالوگ؛ jobDetail پنل حالت‌های steps/checks دارد
- agent/web/index.html + public/panel.html: کارت «🛡️ ضد شناسایی بات» (۱۰ سوییچ با توضیح + ۳ سطح + تست سریع با چک‌لیست ✓/✗ + سایت تست) و کارت «🔑 حساب‌ها و ورود خودکار» (چیپ ۸ پلتفرم + فرم چابک username/password/TOTP + کارت کپچا با provider/کلید/auto) و دکمهٔ «⚡ ورود خودکار» در هر کارت پلتفرم + بَج 🔑 حساب؛ استایل‌های جدید sw/modrow/checkrow/chipcred؛ v1.1→v1.2
- agent/config.json: بخش‌های stealth (level=standard + modules) و captcha؛ data/stealth-probe.html؛ README.md به‌روز (جدول امکانات + بخش‌های «ضد شناسایی v2» و «ورود خودکار و حل کپچا» + عیب‌یابی)
- اعتبارسنجی:
  * validate_v12.py: stealth js تولید/seed/disable_for/پروکسی-webrtc/launch-args/probe all-pass+all-fail/TOTP/CRUD اعتبارنامه/masked/detect کپچا — همه پاس؛ auto_login با StubEngine: ۳ گام تایپ+submit تأیید
  * هارنس سرور + ۲۱ تست اندپوینت: همه پاس — شامل ورود خودکار بدون حساب (خطای فارسی «ذخیره نشده») و با حساب (job done با ۱۴ step)
  * agent-browser روی /panel.html: صفر خطا؛ فوتر بدون overlap در داشبورد و پلتفرم‌ها (اثبات هندسی)؛ ۱۰ سوییچ + سطح‌ها ۳→۹→۱۰؛ چیپ حساب‌ها (تلگرام ۲ فیلد، بله ۱ فیلد)؛ ۸ دکمهٔ ورود خودکار؛ toast دمو؛ موبایل 390px بدون سرریز؛ VLM: بدون شکستگی/هم‌پوشانی
  * bun run lint: صفر خطا؛ ZIP: ۵۰ entry شامل stealth.py/captcha.py/credentials.py/stealth-probe.html

Stage Summary:
- نوار مزاحم برای همیشه رفع شد (ریشهٔ واقعی: قفل قد body) — فوتر حالا در همهٔ نماها پایین محتوا یا پایین صفحه است
- ضد شناسایی v2 با ۱۰ ماژول قابل‌تنظیم از پنل، اثر انگشت پایدار per-profile، تست سریع داخلی و سایت تست واقعی — روی همهٔ پلتفرم‌ها به‌صورت پیش‌فرض فعال (سطح استاندارد)
- ورود خودکار کامل: حساب‌ها در data/credentials.json (رمز هرگز به مرورگر برنمی‌گردد)، فرم‌ها خودکار پر می‌شوند، کپچا با 2Captcha حل و تزریق می‌شود، کد 2FA با TOTP خودکار ساخته می‌شود، کد SMS در پنجرهٔ باز وارد می‌شود
- وابستگی جدیدی اضافه نشد (فقط stdlib) — برای کاربر فقط دانلود ZIP جدید کافی است

---
Task ID: 6
Agent: main-agent (Z.ai Code)
Task: ParsAgent پنل — رفع ۵ درخواست کاربر: باگ انتخاب اکشن در اجرای سریع، دکمه آپلود عکس، زمان‌بندی کارها + راهنمای طبیعی بودن، راهنمای کامل سایت/تست بات/تنظیمات، عدم شروع خودکار ضبط ماکرو

Work Log:
- بازنویسی کامل سه فایل پروژهٔ کاربر (پروژه روی ویندوز کاربر اجرا می‌شود، تحویل به‌صورت code block):
  1. panel_server.py — بک‌اند FastAPI کامل: state polling ایمن (فرم‌ها هرگز re-render نمی‌شوند)، آپلود multipart به پوشه media، زمان‌بند سه‌حالته (interval با jitter / daily با گرید ۲۴ ساعته / once)، راهنمای per-platform طبیعی بودن، تست بات ۸-موردی، credentials با mask، scheduler با guard عدم هم‌پوشانی، recorder فقط با POST /api/macro/start
  2. static/index.html — SPA فارسی RTL با ۸ تب: داشبورد/پلتفرم‌ها/اجرای سریع/زمان‌بندی/رسانه‌ها/ماکرو/تنظیمات/راهنما؛ دکمه «⬆ آپلود از سیستم» کنار هر فیلد media + تب رسانه با dropzone؛ دکمه «🛡 پیشنهاد ایمن»؛ ۱۰ بخش راهنمای کامل
  3. launcher.py — Tkinter، فقط سرور را بالا می‌آورد؛ هیچ ضبط خودکار
- تأیید سندباکسی: py_compile OK، سرور بالا آمد، ساخت/حذف زمان‌بندی OK، آپلود PNG OK، settings persist OK
- تأیید مرورگری (agent-browser): انتخاب «فالو کردن» بعد از ۷ ثانیه (۲+ چرخه poll) حفظ شد (رفع باگ تأییدشده)؛ گرید ۲۴ ساعته؛ پیشنهاد ایمن 35-120s؛ ۱۰ بخش راهنما؛ ۲۱ کنترل تنظیمات؛ thumbnail رسانه؛ بدون خطای JS؛ footer sticky

Stage Summary:
- ریشهٔ باگ اجرای سریع: poll قبلی کل فرم را بازسازی می‌کرد → حالا فقط chip/متن‌های data-dyn آپدیت می‌شوند
- ضبط ماکرو: صراحتاً فقط با دکمه شروع می‌شود؛ در startup فقط scheduler فعال است
- فایل‌های تحویلی در /home/z/my-project/parsagent/ (panel_server.py, static/index.html, launcher.py) آماده کپی روی ویندوز کاربر

---
Task ID: B
Agent: full-stack-developer
Task: اتصال سایت به بستهٔ نهایی parsagent/ (نسخهٔ ۲.۰.۰) — به‌روزرسانی APIهای دانلود/مرور سورس، ارتقای نسخه در UI و بازنویسی راهنمای نصب (حذف ارجاع‌های CLI/EXE)

Work Log:
- src/app/api/download/route.ts: AGENT_ROOT از agent → parsagent؛ فیلتر ZIP بازنویسی شد — adm-zip مسیر کامل با پیشوند ریشهٔ ZIP و جداکنندهٔ / به فیلتر می‌دهد (پوشه‌ها با اسلش انتهایی)، پس نرمال‌سازی done و چک سگمنت اول نسبت به RUNTIME_DIRS={config,media,macros,profiles,logs} انجام شد؛ نام فایل ZIP → ParsAgent-v2.0.zip؛ ریشهٔ داخلی ZIP همان pars-agent ماند
- src/app/api/agent/files/route.ts: AGENT_ROOT → parsagent؛ SKIP_DIRS += media, macros, profiles, config؛ LANG_BY_EXT += .html→markup؛ ORDER بازنویسی شد (panel_server.py → README.md → requirements.txt → launcher.py → ParsAgent.bat → static/)
- src/components/agent/code-viewer.tsx: فایل پیش‌فرض selected از main.py → panel_server.py
- src/components/agent/download-section.tsx: چیپ «نسخهٔ ۱.۰.۰» → «نسخهٔ ۲.۰.۰»؛ متن کارت دانلود → «پکیج کامل و آمادهٔ اجرا: سرور پنل محلی + رابط فارسی + لانچر گرافیکی + راهنمای کامل — استخراج کن، اجرا کن.»
- ارتقای نسخه: header.tsx و footer.tsx (PARSAGENT · v2.0.0) و data.ts (AGENT_VERSION="v2.0.0")
- install-guide.tsx: حذف جملهٔ «کاربر حرفه‌ای؟ CLI هم سر جایش است.» از گام ۴؛ سه آکاردئون قدیمی (exe/macro-keys/cli) با run-direct (اجرای مستقیم python panel_server.py + PANEL_PORT) و mirror (آینهٔ npmmirror برای کرومیوم) و data (نقشهٔ پوشه‌های داده) جایگزین شدند؛ import بلااستفادهٔ ChevronDown حذف شد — هیچ ارجاعی به build.bat/main.py/CLI/F9/F10/PyInstaller/EXE در این فایل نماند
- محدودهٔ ممنوعه دست‌نخورده ماند: parsagent/ ، public/panel.html ، شبیه‌سازها (demo/terminal/hero/panel/*) ، پالت emerald ، RTL/Vazirmatn
- اعتبارسنجی:
  * bun run lint: صفر خطا/هشدار (exit 0)
  * GET /api/download: 200 با filename="ParsAgent-v2.0.zip" — ZIP حاوی pars-agent/{panel_server.py, README.md, requirements.txt, launcher.py, ParsAgent.bat, static/, static/index.html} و صفر entry از config/media/macros/profiles/__pycache__
  * GET /api/agent/files: ۶ فایل، ۳۰۸۶ خط، ۱۵۸KB — ترتیب دقیقاً طبق ORDER جدید؛ static/index.html با language=markup
  * agent-browser: / بدون خطای کنسول/هیدریشن؛ PARSAGENT · v2.0.0 در هدر و فوتر؛ صفر v1.0.0؛ مرور سورس با panel_server.py پیش‌فرض رندر شد (badge=python، «۶ فایل»)؛ /panel.html بنر «پیش‌نمایش استاتیک» + ۸ تب (شامل راهنما) + ۵ خط لاگ تدریجی در #logfeed و بدون خطای JS؛ موبایل 390px روی هر دو صفحه scrollWidth=clientWidth=390؛ فوتر چسبان (footerBottom=viewportH در ویوپورت 3000)؛ آکاردئون‌های جدید هر سه باز و محتوا/CodeBlockها تأیید شدند
  * dev.log: صفر خطای کامپایل/رانتایم (فقط 404 قدیمی /api/health و هشدار dev از پیش موجود)

Stage Summary:
- سایت حالا به بستهٔ نهایی parsagent/ (v2.0.0) وصل است: ZIP دانلودی ParsAgent-v2.0.zip (۴۴.۵KB، ۷ entry، بدون داده‌های شخصی کاربر) و مرورگر سورس فایل‌های واقعی ۲.۰.۰ را نشان می‌دهد
- نکتهٔ فنی مهم: فیلتر adm-zip مسیر «کامل داخل ZIP» می‌گیرد نه مسیر نسبی — با نرمال‌سازی جداکننده/اسلش انتهایی و چک سگمنت اول، پوشه‌های ران‌تایم هم از ZIP حذف شدند (entryهای پوشهٔ خالی config/media/macros/profiles هم رفتند)
- راهنمای نصب با معماری جدید هم‌راستا شد: مسیر اصلی لانچر گرافیکی، اجرای مستقیم panel_server.py، آینهٔ کرومیوم برای ایران، و نقشهٔ ذخیره‌سازی داده‌ها

---
Task ID: A + A2
Agent: main-orchestrator (Z.ai Code)
Task: درخواست کاربر «خودت فایلهای پروژه رو مثل همیشه کامل کن بده دانلود کنم» — کامل‌کردن بستهٔ نهایی parsagent به یک پروژهٔ قابل‌دانلود کامل

Work Log:
- افزودن فایل‌های مکمل به parsagent/:
  * requirements.txt — fastapi + uvicorn[standard] + python-multipart + playwright + راهنمای آینهٔ ایران برای نصب کرومیوم
  * ParsAgent.bat — اجرا با دابل‌کلیک (python → py fallback) با chcp 65001 و پیام خطای فارسی در نبود پایتون
  * README.md — راهنمای کامل فارسی: نصب ۳-مرحله‌ای، ۳ روش اجرا، جدول تور ۸ تب پنل، قابلیت‌های کلیدی (Stealth/زمان‌بندی/حساب‌ها/کپچا)، نقشهٔ ذخیرهٔ داده‌ها، جدول عیب‌یابی، هشدار استفادهٔ مسئولانه
- launcher.py: افزودن دکمهٔ «📦 نصب پیش‌نیازها (فقط بار اول)» — روی ویندوز pip install -r requirements.txt را در پنجرهٔ کنسول قابل‌مشاهده اجرا می‌کند (cmd /k)؛ روی غیر ویندوز با capture و نمایش نتیجه؛ geometry 360→400؛ اصلاح متن هشدار requirements.txt؛ افزودن نوت «نصب مرورگر معمولاً لازم نیست»
- تست دودی panel_server.py در سندباکس: py_compile OK — بوت روی PANEL_PORT=8799 — اندپوینت‌های /api/ready /api/state /api/options /api/schedules /api/settings /api/credentials /api/media /api/macro/list و / همه 200؛ state شامل ۷ پلتفرم
- ساخت public/panel.html جدید (پیش‌نمایش استاتیک پنل ۲.۰.۰): snapshot واقعی همهٔ GET APIها (از سرور در حال اجرا) + shim جاوااسکریپت که fetch این‌ترسپت می‌کند (GET→snapshot، سایر→پاسخ دموی «ok») + WebSocket ساختگی (FakeWS) + ۵ خط لاگ نمونهٔ تدریجی در #logfeed + بنر نارنجی چسبان «پیش‌نمایش استاتیک» — اسکریپت سازنده در tests/tmp/build_demo_panel.py؛ state snapshot دستکاری شد تا اینستاگرام/تلگرام «باز» دیده شوند

Stage Summary:
- بستهٔ نهایی parsagent حالا پروژهٔ کامل و خودکفاست: panel_server.py + static/index.html + launcher.py + requirements.txt + README.md + ParsAgent.bat (۶ فایل، ~2913 خط)؛ پوشه‌های config/media/macros/profiles در اولین اجرا خودکار ساخته می‌شوند
- پیش‌نمایش استاتیک جدید پنل جایگزین panel.html قدیمی (v1.2) شد — ظاهر واقعی پنل ۲.۰.۰ با ۸ تب و لاگ زندهٔ نمونه

---
Task ID: C
Agent: main-orchestrator (Z.ai Code)
Task: تایید نهایی مستقل با agent-browser + بسته‌بندی نهایی

Work Log:
- لندینگ /: بدون خطا؛ v2.0.0 حاضر، v1.0.0 غایب؛ scrollWidth=clientWidth (بدون سرریز)
- مرور سورس: فایل پیش‌فرض panel_server.py رندر شد، main.py غایب
- /panel.html: بنر دمو ✓، ۸ تب (داشبورد/پلتفرم‌ها/اجرای سریع/زمان‌بندی/رسانه‌ها/ضبط ماکرو/تنظیمات/راهنما) ✓، ۱۴ chip پلتفرم ✓، لاگ‌های نمونه ظاهر شدند ✓، بدون خطای JS ✓
- تست باگ قبلی کاربر (پرش منوی اجرای سریع): در #qr-action گزینهٔ ۴ («لایک توییت‌های فید») انتخاب شد — بعد از ۵+ ثانیه و چند سیکل polling هنوز همان انتخاب بود ✓ (رفع تاییدشده)
- راهنمای نصب: آکاردئون‌های جدید (اجرای مستقیم/آینهٔ کرومیوم/داده‌ها) حاضر؛ صفر ارجاع به python main.py و build.bat
- موبایل 390px: هر دو صفحه بدون سرریز افقی (w=c=390)
- ZIP نهایی: ParsAgent-v2.0.zip (44,518 بایت، ۷ entry) — شامل هر ۶ فایل + پوشهٔ static؛ صفر entry از config/media/macros/profiles/__pycache__ (دیتای شخصی هرگز در ZIP نیست)
- dev.log: صفر خطای جدید؛ console: صفر error (فقط info های benign)

Stage Summary:
- همه‌چیز تایید شد: بستهٔ کامل ParsAgent v2.0.0 (با هر ۹ اصلاح کاربر) از دکمهٔ «دانلود سورس کامل (ZIP)» سایت قابل دانلود است؛ پیش‌نمایش واقعی پنل در /panel.html؛ سایت، ZIP و مرورگر سورس همگی با نسخهٔ نهایی هم‌گام‌اند

---
Task ID: D
Agent: main-orchestrator (Z.ai Code)
Task: درخواست کاربر — ۱) رفع گیرکردن لانچر روی «در حال راه‌اندازی سرور» ۲) همیشه کل سورس آپدیت شود (نه پچ) ۳) بازگشت ظاهر قبلی لانچر بدون دست‌زدن به ظاهر

Work Log:
- ریشه‌یابی باگ با دو آزمون مستقل در سندباکس:
  ۱) پروکسی/VPN سیستم (رایج در ایران) درخواست urllib به 127.0.0.1 را می‌ربود → بررسی سلامت هرگز موفق نمی‌شد (شبیه‌سازی: مسیر قدیمی=FAIL با timeout، مسیر جدید=OK در 0.00s)
  ۲) tk.after از نخِ دیگر روی این Tcl بی‌صدا نادیده گرفته می‌شد → حتی با سرور سالم، به‌روزرسانی وضعیت هیچ‌وقت اجرا نمی‌شد (اثبات: hits=0 در آزمون مستقل)
- بازنویسی کامل parsagent/launcher.py (۵۱۹ خط) — ظاهر محبوب نسل agent/ عیناً بازگردانده شد (همان پالت تیره، هدر، سه دکمهٔ بزرگ، ردیف ابزار، لاگ رنگی، فوتر) + سه تعمیر داخلی:
  * _DIRECT = build_opener(ProxyHandler({})) → همهٔ بررسی‌های سلامت مستقیم و بدون پروکسی
  * صف امن ui_q + پمپ _pump در نخ اصلی → صفر وابستگی به after از نخ دیگر (همهٔ self.post)
  * خروجی سرور PIPE و استریم زنده به لاگ لانچر (حذف DEVNULL) + تشخیص سرور از-قبل-روشن + پیام خطای فارسی با راهنمای ۴ مرحله‌ای در سقف ۹۰ ثانیه
- تست E2E واقعی لانچر زیر Xvfb با پروکسی ساختگی کاربر (تست‌ها در tests/tmp/test_launcher_v21.py):
  SERVER_READY=True در ~۱ ثانیه · وضعیت «سرور در حال اجرا — پنل آماده است» · «● پنل: روشن» · لاگ زندهٔ سرور در لانچر
- ارتقای نسخه کل پکیج به 2.1.0: panel_server.py (سطر docstring)، static/index.html و public/panel.html (فوتر ۲.۱.۰)، README.md (سطر عیب‌یابی جدید + نکتهٔ لاگ زندهٔ لانچر)
- سایت: data.ts (AGENT_VERSION)، header.tsx، footer.tsx، download-section.tsx (چیپ نسخه) → v2.1.0؛ download route → filename=ParsAgent-v2.1.0.zip
- اعتبارسنجی:
  * py_compile هر دو فایل پایتون OK؛ بوت panel_server در سندباکس OK
  * ZIP دانلودی: ۷ entry، شامل لانچر جدید (ui_q + _DIRECT، بدون DEVNULL)، فاقد پوشه‌های ران‌تایم — ۶/۶ چک PASS
  * agent-browser: / بدون خطا؛ v2.1.0 در هدر و فوتر، صفر v2.0.0؛ چیپ «نسخهٔ ۲.۱.۰»؛ مرور سورس → کلیک launcher.py → کد رفع باگ رندر شد؛ /panel.html: فوتر ۲.۱.۰ + ۸ تب + بدون خطا؛ موبایل 390px هر دو صفحه بدون سرریز افقی؛ فوتر چسبان OK؛ VLM: رندر سالم، بدون شکستگی/هم‌پوشانی
  * bun run lint: صفر خطا؛ dev.log: صفر خطا

Stage Summary:
- باگ «گیرکردن لانچر» برای همیشه رفع شد — دو ریشهٔ مستقل (پروکسی سیستم + ناامنی after بین‌نخ) هر دو تعمیر و با E2E زیر سناریوی VPN کاربر اثبات شد
- ظاهر لانچر همان نسل محبوب قبلی است؛ فقط منطق داخل تعمیر شد و به ظاهر دست زده نشد
- کل سورس (نه پچ) در ParsAgent-v2.1.0.zip از دکمهٔ دانلود سایت قابل دریافت است؛ سایت، مرورگر سورس و پیش‌نمایش پنل همگی با 2.1.0 هم‌گام شدند

---
Task ID: E
Agent: main-orchestrator (Z.ai Code)
Task: درخواست کاربر — ۱) توضیح معنی «باز/بسته» بودن پلتفرم ۲) چرا بخش ضد شناسایی کم شد؟ ۳) پیشرفته‌تر کردن ضد شناسایی بر اساس متد روز دنیا ۴) زمان‌بندی برای پخش ماکرو

Work Log:
- پاسخ سؤال «باز/بسته» در سه لایه: متن توضیحی زیر عنوان تب پلتفرم‌ها + tooltip روی همهٔ chipهای وضعیت (داشبورد و کارت‌ها) + بخش جدید در تب راهنما («معنی باز و بسته بودن پلتفرم»)
- parsagent/panel_server.py — موتور ضد شناسایی v3 (نوشتن از نو):
  * اصل «اثر انگشت پایدار»: fp_values() برای هر پروفایل seed دائمی (profiles/<p>/.fpseed) می‌سازد و از آن GPU (استخر رندررهای واقعی ANGLE: NVIDIA/Intel/AMD/Iris XE)، هستهٔ CPU (4..16)، رم (4..16)، جابجایی پیکسل Canvas و دامنهٔ نویز صدا تعیین می‌شود — همه بین اجراها ثابت (نویز تصادفیِ هر بار توسط CreepJS لو می‌رود)
  * ماژول‌های JS جدید: window.chrome کامل (app/runtime/loadTimes/csi)، تعمیر Permissions، حذف Headless از UA + جعل UA سفارشی (اختیاری/خاموش)، نویز پایدار AudioContext (getChannelData)، ماسک فونت (fonts.check: رایج=دارد/ساختگی=ندارد)، مشخصات سخت‌افزار واقع‌نما، شیلد WebRTC (کاندیدیت‌های محلی فیلتر — پیش‌فرض خاموش)، کلاک toString (همهٔ تابع‌های وصله‌شده native به نظر می‌رسند)
  * رفتار انسانی: htype با ۴ سرعت (off/fast/human/slow) + مکث «فکر کردن» ۴٪، hclick با مسیر موس منحنی بیزیه (۱۲-۲۴ گام)، goto با اسکرول تصادفی ۴۵٪، _night_now (مکث شبانهٔ ۱ تا ۷)
  * launch: ignore_default_args=["--enable-automation"] + لاگ «ضد شناسایی v3 فعال شد — اثر انگشت پایدار #N»
- DEFAULT_SETTINGS: گروه‌بندی جدید stealth (۴ گروه، ۱۹ کلید) — سازگار با settings قدیمی (merge)
- زمان‌بندی پخش ماکرو: POST /api/schedules حالا type=macro + macro=نام می‌پذیرد؛ _macro_replay مشترک (دکمهٔ اجرا + زمان‌بند)؛ Scheduler._run شاخهٔ macro؛ مکث شبانه در _loop قبل از dispatch
- تست بات: ۶ چک جدید — window.chrome کامل، نویز پایدار Canvas (دو خواندن یکسان)، AudioContext، ماسک فونت (Y/N)، سخت‌افزار واقع‌نما، toString native — مجموع ۱۳ چک
- باگ واقعی پیدا و رفع شد: state.macro.saved رشته برمی‌گرداند ولی renderMacros آبجکت می‌خواست → macro_names() حالا [{name, events}] برمی‌گرداند + shim سازگاری در فرانت (typeof m0 === "string")
- parsagent/static/index.html:
  * کارت «🥷 ضد شناسایی بات — پیشرفته»: ۳ عنوان گروه + ۱۹ سوییچ با tooltipهای کامل + ۳ دکمهٔ سطح سریع (پایه/استاندارد/حداکثر → applyLevel) + انتخاب سرعت تایپ + ردیف UA سفارشی شرطی
  * تب زمان‌بندی: select «نوع وظیفه» (اکشن پلتفرم/پخش ماکرو) + select ماکرو (از /api/macro/list) + مخفی‌سازی شرطی اکشن/پارامترها/pacing
  * renderSchedList: ردیف ماکرو با «🎬 پخش ماکرو …»؛ renderMacros: دکمهٔ «📅 زمان‌بندی» هر ماکرو → پرش به تب زمان‌بندی + kind=macro + پیش‌انتخاب + عنوان
  * راهنما: ۳ بخش جدید/بازنویسی‌شده (معنی باز/بسته؛ جدول کامل ۴ گروه ضد شناسایی؛ زمان‌بندی پخش ماکرو) + لیست تست بات به ۱۳ مورد
  * فوتر: نسخهٔ ۲.۲.۰
- parsagent/README.md: بخش «ضد شناسایی پیشرفته» با ۴ گروه + جدول تور پنل به‌روز + زمان‌بندی ۲-نوعه
- سایت: data.ts/header/footer/download-section → v2.2.0 و نسخهٔ ۲.۲.۰؛ download route → ParsAgent-v2.2.0.zip؛ features.tsx: کارت ضدشناسایی و کارت ماکرو بازنویسی شد
- public/panel.html بازسازی (اسکریپت build_demo_panel + snapshot واقعی سرور): پیش‌فرض‌های تمیز (webrtc خاموش/standard/human) + ۱ ماکروی نمونه + ۲ زمان‌بندی نمونه (۱ اکشن + ۱ ماکرو)
- اعتبارسنجی:
  * ۲ دور تست بک‌اند روی سرور واقعی در سندباکس: ۸/۸ + ۴/۴ پاس (کلیدهای جدید، roundtrip، seed پایدار fp_values، ساخت/رد زمان‌بندی ماکرو، سازگاری اکشن، state آبجکتی، نام فارسی ماکرو)
  * py_compile OK؛ node --check اسکریپت پنل OK؛ همهٔ IDهای JS در HTML موجود
  * agent-browser: لندینگ بدون خطا (v2.2.0 حاضر، v2.1.0 غایب)؛ /panel.html: ۸ تب، ۳ گروه، ۲۱ سوییچ، ۴ سرعت، سوییچ kind، jump دکمهٔ زمان‌بندی ماکرو (kind=macro + پیش‌انتخاب + عنوان درست بعد از رفع باگ)، پیش‌فرض webrtc خاموش، «حداکثر» → همه روشن + slow + UA خاموش؛ صفر خطای کنسول؛ موبایل 390px بدون سرریز؛ فوتر چسبان (3000/3000) و طبیعی در صفحات بلند؛ VLM: کارت تنظیمات بدون شکستگی/هم‌پوشانی، RTL سالم
  * ZIP نهایی: ParsAgent-v2.2.0.zip — ۷ entry، شامل v3 و رفع باگ macro، بدون دیتای شخصی؛ bun run lint: صفر خطا؛ dev.log: صفر خطا

Stage Summary:
- ضد شناسایی به v3 «پیشرفته» ارتقا یافت: ۴ گروه/۱۹ ماژول با اصل طلایی «اثر انگشت پایدار per-profile» + سطح‌سنج پایه/استاندارد/حداکثر + ۱۳ چک تست بات — پاسخ به «چرا کمش کردی» (حذف اشتباه در بازنویسی ۲.۰، حالا کامل‌تر از هر دو نسل قبل)
- پخش ماکرو هم‌سطح اکشن‌ها زمان‌بندی شد: تکرارشونده/روزانه/یک‌بار + جیتر + مکث شبانه، از دکمهٔ اختصاصی هر ماکرو
- «باز/بسته» در سه لایه مستند شد (متن تب + tooltip + راهنما)
- کل سورس (نه پچ) در ParsAgent-v2.2.0.zip از دکمهٔ دانلود سایت؛ ظاهر لانچر دست‌نخورده ماند
---
Task ID: 7
Agent: site-updater
Task: ارتقای سایت به v2.3.0 + افزودن نمای «هوش مصنوعی» به دموی پنل React (هم‌گام با تب جدید 🧠 ایجنت خودمختار دسکتاپ)

Work Log:
- مرور مرجع‌ها قبل از کد: parsagent/static/index.html (بخش tab-ai + بلوک JS «هوش مصنوعی (۲.۳.۰)»)، parsagent/ai_agent.py (کاتالوگ PROVIDERS با Z.ai/GLM-4.6 در صدر، TOOL_NAMES، معناشناسی AI_STATUS و جمله‌های لاگ ماموریت)
- نسخه v2.2.0 → v2.3.0 در ۶ نقطه: data.ts (AGENT_VERSION)، header.tsx، footer.tsx، download-section.tsx (چیپ «نسخهٔ ۲.۳.۰»)، api/download/route.ts (ParsAgent-v2.3.0.zip) و api/agent/files/route.ts (ai_agent.py با وزن ۱ درست بعد از panel_server.py؛ بقیه شیفت شدند)
- features.tsx: کارت جدید «ایجنت هوش مصنوعی خودمختار» با آیکن Brain به‌عنوان اولین کارت (۷ کارت در گرید فعلی)
- src/lib/panel/types.ts: اینترفیس‌های AiModelInfo/AiProviderInfo/AiMissionStep/AiPost/AiMissionLogEntry/AiMission/AiChatMessage/AiPanelState + فیلد ai در PanelState + ۷ اکشن جدید (aiSetProvider/aiSetModel/aiSetAutonomy/aiCreateMission/aiMissionControl/aiSendChat/aiReset)
- src/lib/panel/store.ts — بخش هوش مصنوعی شبیه‌ساز:
  * کاتالوگ ۹ سرویس عین PROVIDERS واقعی (zai با ۵ مدل GLM شامل دو Flash رایگان، zai_coding، openai، anthropic، gemini، groq، deepseek، openrouter، custom)؛ hasKey فقط برای zai (نمایش ✓)
  * یک ماموریت دمو کامل («کمپین هفتگی فروشگاه»، zai/glm-4.6، semi، ۳ گام done، ۴ پست تلگرام+توییتر در صف انتشار، گزارش با بولت، ۹ رخداد لاگ با واژگان پنل واقعی)
  * زنجیرهٔ شبیه‌سازی با setTimeout و توکن گاردشده به ازای هر ماموریت: ~۱٫۴ث برنامه‌ریزی (📋 برنامه آماده شد: ۳ گام) → هر گام ~۱٫۶ث با لاگ‌های ✍️/✅/📅/📝 → گزارش نهایی و وضعیت completed؛ رویدادهای مهم به لاگ اصلی پنل هم emit می‌شوند تا شمارنده‌ها (logCount، بج ناوبری ai) هم‌گام بمانند
  * کنترل کامل ماموریت: approve (wait_approval→running و ادامهٔ زنجیره)، pause (توقف با ابطال توکن)، resume (ادامه از همان گام)، cancel (لغو فوری)؛ رفع دوبرابر نشدن draftها هنگام resume وسط گام تولید
  * گفتگوی سریع با ۵ پاسخ فارسی چرخشی (~۸۰۰ms)؛ aiReset بازگشت به حالت پیش‌فرض + پاک‌سازی تایمرها
- فایل جدید src/components/agent/panel/ai-view.tsx (RTL، آینهٔ tab-ai دسکتاپ): هدر توضیحی، کارت سازندهٔ ماموریت (۳ Select: سرویس با پسوند ✓ / مدل با «tag» / خودمختاری + Textarea + ۴ چیپ 💡 نمونه با همان ۴ نمونهٔ پنل واقعی + دکمهٔ emerald «🚀 شروع ماموریت» که با خالی بودن disable می‌شود + hint کلید)، کارت گفتگوی سریع (بابل user راست/emerald در RTL)، لیست ماموریت‌ها با چیپ وضعیت رنگی (completed=emerald، wait_approval/running=amber/emerald pulse، paused/cancelled=zinc، failed=rose، waiting=sky)، گام‌های برنامه با ✅/⏳/• و نام فارسی ابزارها، Collapsible پست‌ها (متن کامل + پلتفرم + وضعیت) و لاگ ایجنت، بلوک گزارش emerald با آمار، دکمه‌های کنترل ✅ تأیید و اجرا / ⏸ توقف / ▶ ادامه / 🛑 لغو
- control-panel.tsx: ViewId «ai» بعد از tasks در NAV (آیکن Brain) + VIEW_META («ایجنت خودمختار — ایده بده، برنامه و محتوا و گزارش بگیر») + رندر AiView + بج شمار ماموریت‌های فعال روی آیتم ناوبری
- اعتبارسنجی:
  * bun run lint: صفر خطا؛ tsc --noEmit: صفر خطای جدید (۵ خطای باقی‌مانده pre-existing در examples/skills/overview-view هستند — با git-stash اثبات شد)
  * agent-browser لندینگ: v2.3.0 حاضر، v2.2.0 غایب (includes('2.2.0')=false)، چیپ «نسخهٔ ۲.۳.۰»، صفر خطای صفحه/کنسول
  * agent-browser دموی پنل → تب هوش مصنوعی: فرم (Z.ai (GLM) ✓ / GLM-4.6 «پیشرفته» / نیمه‌خودکار (توصیه))، ۴ چیپ نمونه، دکمهٔ غیرفعال تا پر شدن متن، ماموریت دمو کامل
  * چرخهٔ کامل ماموریت با «💡 نمونهٔ ۱» + «🚀 شروع ماموریت»: ~۹ ثانیه تا completed با ۳ گام، ۳ پست (تلگرام+توییتر)، ۱۲ رخداد لاگ (🧠/📋/▶/✍️/✅/📅/📝) و بلوک «📊 گزارش نهایی ماموریت» با بولت و آمار
  * تست همهٔ مسیرها: حالت «پیشنهادی» → «منتظر تأیید شما» → ✅ تأیید و اجرا → completed؛ ⏸ توقف → «متوقف» → ▶ ادامه → completed؛ 🛑 لغو → «لغو شد» (هر سه از store هم تایید شد)
  * تعویض سرویس به Groq → مدل‌های رایگان لیست شدند و hint «کلید سرویس را در تنظیمات وارد کنید» ظاهر شد؛ گفتگوی سریع: پیام user + پاسخ assistant چرخشی
  * api/agent/files: ai_agent.py دومین فایل؛ api/download: filename=ParsAgent-v2.3.0.zip؛ در پایان aiReset برای بازگشت دموی تمیز (zai/glm-4.6/semi + فقط ماموریت دمو)
- محدودیت‌ها: به parsagent/ و public/panel.html دست زده نشد (مالک ارکستریتور)

Stage Summary:
- سایت کامل به v2.3.0 ارتقا یافت و نمای «هوش مصنوعی» با همان واژگان/ساختار تب واقعی دسکتاپ به دموی پنل اضافه شد — از کاتالوگ ۹ سرویس (Z.ai اول) تا زنجیرهٔ زندهٔ ماموریت: برنامه → تولید محتوا → زمان‌بندی → گزارش نهایی، با کنترل کامل تأیید/توقف/ادامه/لغو و گفتگوی سریع
- همهٔ مسیرها با agent-browser روی سرور زنده تست شد (شامل هر دو سطح خودمختاری) و lint/tsc تمیز است؛ دموی پنل به حالت اولیهٔ تمیز بازگردانده شد

---
Task ID: 8
Agent: main-orchestrator (Z.ai Code)
Task: درخواست کاربر — افزودن تب «هوش مصنوعی» با ایجنت کاملاً خودمختار (تولید محتوا، زمان‌بندی، تصمیم فالو، گزارش) + پشتیبانی از APIهای رایگان/پولی + مدل‌های z.ai در تب AI و تنظیمات

Work Log:
- فایل جدید parsagent/ai_agent.py (~۷۰۰ خط، فقط کتابخانهٔ استاندارد — بدون پیش‌نیاز جدید):
  * کاتالوگ ۹ سرویس: Z.ai (GLM) اول لیست (glm-4.6/4.5/4.5-air/4.5-flash رایگان/glm-4-flash رایگان)، Z.ai طرح Coding، OpenAI، Anthropic، Gemini، Groq، DeepSeek، OpenRouter و «سرویس سفارشی» سازگار با OpenAI (Ollama)
  * کلاینت LLM یکپارچه (رابط OpenAI/Anthropic/Gemini) با urllib + to_thread — آدرس‌های لوکال بدون پروکسی، اینترنتی با پروکسی سیستم (VPN کاربر)؛ json_mode + extract_json مقاوم با یک تلاش مجدد
  * AgentSystem (تزریق وابستگی به پنل): چرخهٔ ماموریت planning → wait_approval/running → waiting → completed/failed/cancelled/paused با step_index قابل ازسرگیری
  * ابزارها: generate_content (قوانین هر پلتفرم: سقف نویسه/هشتگ/سبک)، schedule_publish (سه استراتژی پخش، سقف روزانه، اتصال عکس از media برای اینستاگرام/فیسبوک، کانال برای پیام‌رسان‌ها)، publish_now، follow_strategy (سقف امن: اینستاگرام ۱۵۰، توییتر ۱۰۰، فیسبوک ۱۵، لینکدین ۲۰ + تبدیل به زمان‌بندی روزانه)، wait_report (گزارش زمان‌دار از طریق نوع جدید زمان‌بندی ai_report)، report (خلاصهٔ مدیریتی فارسی)، status_check
  * سطوح خودمختاری: manual (تأیید برنامه) / semi (فقط انتشار فوری تأیید) / auto؛ recover() بعد از ری‌استارت → paused
- panel_server.py: import + AGENTS + _agent_add_schedule؛ DEFAULT_SETTINGS["ai"] کامل؛ شاخهٔ ai_report در Scheduler._run؛ recover در startup؛ ۸ اندپوینت جدید: /api/ai/{catalog,test,chat} + /api/ai/missions (GET/POST) + /{mid} + /{mid}/control؛ post_settings کلید ai؛ docstring نسخهٔ ۲.۳.۰
- static/index.html: تب نهم «🧠 هوش مصنوعی» (فرم ماموریت + ۴ نمونه + گفتگوی سریع + کارت ماموریت‌ها با گام‌ها/پست‌ها/لاگ زنده/گزارش/دکمه‌های تأیید-توقف-ادامه-لغو)، کارت «هوش مصنوعی» در تنظیمات (انتخاب سرویس/مدل پیش‌فرض + ۸ فیلد کلید + سرویس سفارشی + دما + سقف روزانه)، WS → type=agent، initAi، راهنمای کامل تب AI، فوتر ۲.۳.۰
- رفع دو باگ واقعی جاوااسکریپت که با node --check پیدا شد (نقل قول برچسب مدل + پرانتز اضافی ternary) + رفع سرریز افقی موبایل (badge با white-space:normal)
- README.md: بخش کامل «ایجنت خودمختار» + جدول ۹ سرویس + جدول داده‌ها/عیب‌یابی جدید + تور ۹-تبی
- تست‌های E2E بک‌اند با سرور LLM ساختگی (OpenAI-سازگار روی 3099): کاتالوگ ۹ سرویس؛ ماموریت کامل auto (برنامه → ۴ پست تلگرام/توییتر → ۴ زمان‌بندی با mission_id/post_id → گزارش)؛ تأیید manual؛ گفتگو؛ رویداد WS agent×۳؛ مسیر ai_report (waiting → finalize → completed + گزارش)
- سایت (ساب‌ایجنت): data/header/footer/download-section → v2.3.0؛ features.tsx کارت «ایجنت هوش مصنوعی خودمختار» (اول)؛ download route → ParsAgent-v2.3.0.zip؛ files route → ai_agent.py وزن ۱؛ دموی React: ai-view.tsx جدید + store/types/control-panel (کاتالوگ ۹ سرویس، مأموریت شبیه‌سازی‌شدهٔ کامل با تأیید/توقف/ادامه/لغو، چت) — همه در مرورگر تست شد
- public/panel.html بازسازی تمیز از پنل واقعی ۲.۳.۰ (شیم MOCKS با /api/ai/catalog واقعی + ماموریت دموی تکمیل‌شده؛ رفع باگ دو-اسکریپتی ناشی از استخراج شیم قدیمی)
- اعتبارسنجی نهایی: py_compile هر ۳ فایل پایتون OK؛ bun run lint صفر خطا؛ dev.log پاک؛ ZIP دانلودی ۸ entry شامل ai_agent.py و بدون دیتای ران‌تایم؛ پنل واقعی و دمو در agent-browser: تب AI، فرم، کارت، گزارش، تنظیمات AI، موبایل ۳90px بدون سرریز، فوتر چسبان، صفر خطای کنسول؛ VLM تأیید رندر سالم هر دو پنل

Stage Summary:
- ParsAgent 2.3.0: ایجنت کاملاً خودمختار «فقط ایده بگو» — برنامه‌سازی، تولید محتوای چند-پلتفرمی، زمان‌بندی انتشار، تصمیم فالو (چند نفر/چه ساعتی/از کجا) و گزارش نهایی فارسی
- مدل‌های z.ai (GLM-4.6 و …) اول لیست انتخاب در تب هوش مصنوعی و تب تنظیمات؛ ۹ سرویس رایگان/پولی + هر اندپوینت OpenAI-سازگار
- کل سورس کامل (نه پچ) در ParsAgent-v2.3.0.zip از دکمهٔ دانلود سایت؛ لانچر دست‌نخورده ماند

---
Task ID: 9 (main-orchestrator)
Agent: Z.ai Code
Task: درخواست کاربر — ۱) ساخت عکس و ویدیو با AI در تب هوش مصنوعی ۲) پیدا کردن پروژهٔ چینی «دستگاه چاپ پول» گیت‌هاب (MoneyPrinterTurbo) و افزودن همان قابلیت ۳) جواب طبیعی دایرکت/پیام‌ها در هر پلتفرم

Work Log:
- جستجوی وب: پروژهٔ موردنظر کاربر شناسایی شد → harry0703/MoneyPrinterTurbo (چین، متن‌باز) — «موضوع ← فیلم‌نامهٔ AI ← گوینده ← زیرنویس ← ترکیب MP4»
- جستجو: مدل‌های تصویرساز z.ai تأیید شدند (GLM-Image / CogView-4 / CogView-3-Flash رایگان؛ اندپوینت OpenAI-سازگار images/generations) و صداهای فارسی edge-tts (fa-IR-FaridNeural / DilaraNeural)
- فایل جدید parsagent/ai_media.py (۶۱۱ خط): کاتالوگ ۳ تصویرساز (Z.ai اول، OpenAI، Pollinations رایگان-بدون-کلید) با زنجیرهٔ جایگزین خودکار + retry + اندازه‌های مربع/عمودی/افقی
- چاپخانهٔ ویدیو به سبک MoneyPrinterTurbo: LLM صحنه‌به‌صحنه (متن فارسی + پرامپت تصویر) ← edge-tts با boundary=WordBoundary برای زمان‌بندی دقیق کلمات ← تصویر AI هر صحنه (fallback: کتابخانهٔ رسانه یا گرادیان) ← ترکیب PNG صحنه با نوار زیرنویس فارسی ← ffmpeg (imageio-ffmpeg باندل، zoompan+fade، aac) ← concat + موسیقی اختیاری media/music + SRT جدا + کاور
- باگ‌های حیاتی که در تست واقعی پیدا و رفع شد: ۱) alpha_composite با اندازهٔ ناهمسان ۲) edge-tts 7.x پیش‌فرض SentenceBoundary ۳) نویز حلقهٔ SRT ۴) **باگ دوبار-برگرداندن RTL**: Pillow ویندوز با موتور Raqm ساخته می‌شود؛ دادن متنِ از-قبل-شکل‌دهی‌شده = آینه شدن ترتیب کلمات! راه‌حل: تشخیص features.check("raqm") → متن خام + direction="rtl" وگرنه مسیر کلاسیک (reshaper+bidi). تأیید با مرورگر (ground truth): IoU=0.927
- فایل جدید parsagent/dm_reply.py (۳۳۸ خط): DMAuto — پاسخ‌گوی دایرکت در هر ۷ پلتفرم: تشخیص گفتگوهای بی‌جواب (آخرین پیام از مقابل)، خواندن با اکسترکتور عمومی + تشخیص جهت، جواب LLM با persona/لحن/FAQ کاربر، تایپ انسانی و ارسال؛ سقف روزانه/فاصلهٔ حداقلی/ساعت فعال/حالت پیش‌نمایش dry-run + سلکتورهای قابل بازنویسی
- ai_agent.py: مدل glm-5.3 به صدر لیست z.ai؛ ابزارهای جدید generate_image / generate_video / dm_autoreply در برنامه‌ریز LLM؛ generate_content برای هر پست image_prompt می‌سازد؛ schedule_publish حالا برای پست‌های اینستاگرام/فیسبوک خودش با AI عکس می‌سازد (رفع «needs_media»)
- panel_server.py: ۱۳ اندپوینت جدید (image/video/jobs/jobs/{id}/image-providers/voices/dmreply CRUD/start/stop/dryrun) + سیستم JOB با پیشرفت زندهٔ WS + media_list با پرچم video + wire شدن DMAUTO و هوک‌های رسانه به ایجنت
- static/index.html: تب هوش مصنوعی با ۴ کارت جدید (چاپخانهٔ ویدیو/ساخت عکس/پاسخ‌گوی دایرکت/کارهای ساخت رسانه) با پیشرفت زنده از طریق WS ai_job؛ رسانه‌ها پخش‌کنندهٔ ویدیو دارند؛ راهنما با ۲ بخش جدید + اعتبار MoneyPrinterTurbo؛ فوتر ۲.۴.۰
- requirements.txt: +edge-tts، Pillow، arabic-reshaper، python-bidi، imageio-ffmpeg | README.md: بخش‌های کامل چاپخانهٔ رسانه و پاسخ‌گوی دایرکت
- تست واقعی در سندباکس: نصب وابستگی‌ها ← دو ویدیوی کامل ۹:۱۶ با صوت فارسی فرید + عکس‌های Pollinations + زیرنویس حک‌شده تولید شد (MP4/SRT/کاور) ← VLM تأیید کرد زیرنویس «درست، خوانا و به‌هم‌پیوسته» است ← تست طلایی: POST /api/ai/image از خود پنل → job completed → فایل در media ✓
- سایت Next.js: v2.4.0 (header/footer/data/download-zip)؛ ai-view.tsx با ۳ دموی تعاملی (چاپخانهٔ ویدیو با مراحل زنده، ساخت عکس با ۴ تصویر واقعیِ تولیدشده در public/demo، پاسخ‌گوی دایرکت با تایپ انیمیشنی)؛ features.tsx با ۳ کارت جدید؛ ترتیب فایل‌های مرورگر سورس
- تأیید: lint صفر خطا · node --check اسکریپت پنل · py_compile همهٔ فایل‌ها · agent-browser (دسکتاپ+موبایل ۳90px، بدون خطای کنسول، فوتر سالم) · ZIP شامل هر ۹ فایل (۷۰۰۲ خط)

Stage Summary:
- ParsAgent ۲.۴.۰ آماده است: تب هوش مصنوعی حالا «عکس و ویدیو هم می‌سازد» (سبک MoneyPrinterTurbo — با اعتبار و لینک به پروژهٔ اصلی) و «دایرکت‌ها را در هر پلتفرم طبیعی جواب می‌دهد»
- سه باگ رندرینگ/زیرنویس که فقط با تست واقعی پیدا می‌شدند، رفع و با VLM + مقایسهٔ پیکسلی با مرورگر اثبات شدند
- بستهٔ کامل از دکمهٔ «دانلود سورس کامل (ZIP)» سایت قابل دریافت است (۹ فایل، بدون داده‌های شخصی)

---
Task ID: 10 (main-orchestrator)
Agent: Z.ai Code
Task: درخواست کاربر — «با توجه به این‌ها نسخهٔ جدید ارائه بده تا دانلود کنم»: ادغام ابزار آفلاین در launcher.py (طبق دو پیام قبلی چت) + عرضهٔ نسخهٔ ۲.۵.۰ قابل دانلود

Work Log:
- بازسازی کامل parsagent/launcher.py (۹۶۶ خط، ظاهر و رفتار UI حفظ شد: هدر/نوار وضعیت/دکمه‌های بزرگ/ابزار/لاگ/فوتر):
  * هستهٔ آفلاین ماژول‌سطحی: build_offline_bundle (pip download فقط-wheel با fallback + pip خودش + کپی کرومیوم/ffmpeg از کش با آینهٔ npmmirror) و install_from_bundle (pip --no-index --find-links + کپی مرورگر + تأیید ماژول‌ها)
  * محافظ‌ها: disk_msg (چک فضای دیسک، os error 112)، compat_problems (نسخهٔ پایتون/۳۲-۶۴ بیتی/free-threaded مثل cp313t با پیام فارسی — همان خطای Rust کاربر)، _is_free_threaded هشدار در شروع لانچر
  * UI جدید هم‌استایل: ردیف «💾 ساخت بستهٔ آفلاین» + «📀 نصب آفلاین» + چک‌باکس «مرورگر داخل بسته»؛ on_start اگر ماژول غایب و بسته هست → پیشنهاد نصب آفلاین (auto_start سرور بعد از نصب)
  * حالت کنسلی: --build-bundle [--no-browsers] و --install-offline و --help؛ فقط stdlib (روی سیستم خام هم بالا می‌آید)
  * تثبیت در start_server: اجرای مستقیم panel_server.py + سلامت /api/ready بدون پروکسی (رفع باگ قدیمی حفظ شد)
- panel_server.py: مدخل ۲.۵.۰ در docstring تغییرات
- static/index.html: فوتر ۲.۵.۰ + آیتم راهنمای جدید «💾 نصب آفلاین بدون اینترنت (جدید ۲.۵.۰)» بعد از شروع سریع
- README.md: بولت ۲.۵.۰ در صدر + بخش کامل «نصب آفلاین» (سه مرحلهٔ A/B/C + محافظ‌ها + معادل کنسلی) + ۳ ردیف جدید عیب‌یابی (os error 112، خطای Rust/free-threaded، ناسازگاری بسته)
- سایت Next.js → v2.5.0: data.ts AGENT_VERSION، header، footer، CHIPS دانلود (۲.۳.۰→۲.۵.۰)، download route → ParsAgent-v2.5.0.zip + افزودن offline_bundle به RUNTIME_DIRS (نشت ZIP محدود)، features.tsx کارت ۱۱م «نصب آفلاین بدون اینترنت (۲.۵.۰)» با HardDriveDownload، install-guide.tsx گام پنجم آفلاین + عنوان «نصب در ۴ گام (+ بستهٔ آفلاین)»
- تست واقعی end-to-end در سندباکس: python launcher.py --build-bundle --no-browsers → ۳۹ wheel واقعی (۹۵.۶MB) دانلود شد + bundle_info.json درست؛ سپس --install-offline → نصب کامل بدون اینترنت (حتی پکیج‌های غایب نصب شدند) و تأیید ۴ ماژول، exit 0؛ بعد پاکسازی بسته از مخزن
- تأییدها: py_compile هر ۵ فایل پایتون OK · پنل واقعی بوت شد (/api/ready، فوتر ۲.۵.۰، آیتم راهنمای آفلاین) · bun run lint صفر خطا · agent-browser: v2.5.0 و کارت و گام آفلاین حاضر، دکمهٔ دانلود → Content-Disposition ParsAgent-v2.5.0.zip، بدون خطای صفحه/کنسول، موبایل ۳90px بدون اسکرول افقی واقعی (کد داخل PRE ovx:auto، scrollX=0)، فوتر پایین صفحه · ZIP دانلودی شامل ۸ فایل با launcher جدید ۴۸.۶KB

Stage Summary:
- ParsAgent 2.5.0 آمادهٔ دانلود است: همان پنل ۲.۴.۰ + «نصب آفلاین بدون اینترنت» یکپارچه در launcher.py (ساخت بسته/نصب/محافظ سازگاری/حالت کنسلی) — چرخهٔ آن در سندباکس واقعاً اجرا و تأیید شد
- فقط فایل‌های تغییر‌یافته: launcher.py (کامل)، panel_server.py (docstring)، static/index.html (فوتر+راهنما)، README.md؛ بقیهٔ پروژه دست‌نخورده
- دکمهٔ «دانلود سورس کامل (ZIP)» سایت همیشه بستهٔ تازه می‌سازد (force-dynamic) و offline_bundle هرگز وارد ZIP نمی‌شود

---
Task ID: 11 (main-orchestrator)
Task: درخواست کاربر — ۱) خواندن کامل پروژهٔ آپلودشده در file.kiwi و حفظ همهٔ امکانات ۲) رفع سه باگ گزارش‌شده: خطای «Executable doesn't exist» کرومیوم + ورود خودکار ناقص (فقط پسورد پر می‌شد، یوزرنیم خالی و دکمهٔ ورود کلیک نمی‌شد) + اجرا نشدن کروم و افزودن Firefox/کرومیوم به تنظیمات ۳) ذخیرهٔ دائمی WORK LOG تا هیچ کاری فراموش نشود ۴) تحویل نسخهٔ کامل قابل دانلود (۲.۶.۰)

Work Log:
- دانلود بستهٔ file.kiwi از لینک کاربر (workspace-4865f4f3….tar، ~۷MB، رمزگشایی E2E خود سایت با agent-browser) — اسنپ‌شات workspace مربوط به دوران v2.3.0 (۴۴۵ خط worklog)
- مقایسه با sandbox فعلی: sandbox جدیدتر است (شامل v2.4.0 چاپخانهٔ رسانه/پاسخ‌گوی دایرکت و v2.5.0 نصب آفلاین) → مبنا همان sandbox؛ طبق خواستهٔ کاربر هیچ فیچری حذف نشد
- ریشه‌یابی سه باگ در parsagent/panel_server.py:
  * باگ کانال: در ensure قدیمی، وقتی کاربر کانال صریح (مثل chrome) انتخاب می‌کرد، شرط `elif ch and channel=="auto"` باعث می‌شد channel هرگز به launch_persistent_context پاس نشود → همیشه کرومیومِ نصب‌نشده صدا زده می‌شد (دقیقاً خطای chromium-1243 کاربر)
  * باگ لاگین: کل بلاک پر کردن فرم به وجود username گره خورده بود؛ سلکتورها بدون انتظار چک می‌شدند (count آنی)؛ کلیک submit فقط وقتی «هر دو» فیلد با موفقیت پر می‌شد؛ فرم‌های دومرحله‌ای (توییتر) و پیام‌رسان‌های تلفنی پشتیبانی نمی‌شدند؛ فیلد قبل از تایپ پاک نمی‌شد (اگر مرورگر خودش پر کرده بود متن‌ها روی هم می‌افتاد)
  * باگ کرومیوم: اگر هیچ مرورگری نبود، پیام خطای خام Playwright به کاربر می‌خورد
- اصلاحات panel_server.py (نسخهٔ ۲.۶.۰):
  * BotSession._launch جدید — کانال همیشه پاس داده می‌شود؛ firefox روی موتور p.firefox (پرچم‌های مخصوص کرومیوم فقط برای خانوادهٔ کرومیوم)؛ حالت خودکار: msedge → chrome → chromium
  * نصب خودکار مرورگر: _pw_missing_browser (تشخیص خطای Executable doesn’t exist) → _install_playwright_browser: اول کپی از offline_bundle/ms-playwright داخل پروژه (بدون اینترنت)، بعد دانلود از آینهٔ npmmirror با PLAYWRIGHT_DOWNLOAD_HOST — خروجی زنده در لاگ پنل + تلاش مجدد لانچ بعد از نصب
  * اندپوینت جدید POST /api/browser/install (chromium|firefox در پس‌زمینه با تسک مدیریت‌شده)
  * ورود خودکار کامل: LOGIN_USER_SEL/LOGIN_PASS_SEL/LOGIN_NEXT_SEL/LOGIN_SUBMIT_SEL برای هر ۷ پلتفرم با چند سلکتور کاندید؛ توابع جدید _first_visible (انتظار با مهلت)، _clear_and_type (پاک‌کردن کامل فیلد قبل از تایپ انسانی)، _login_error_text (خواندن خطای سایت مثل رمز اشتباه)، _do_login_fill (هستهٔ مشترک: کاربر → «بعدی» برای فرم‌های دومرحله‌ای → رمز → کلیک دکمهٔ ورود یا Enter)، _maybe_autologin (در «باز کردن سایت»: اگر فرم ورود ببیند و اطلاعات ذخیره باشد خودش وارد می‌شود — درخواست اصلی کاربر)
  * پیام‌های نتیجه گام‌به‌گام فارسی: «⌨ نام کاربری پر شد، 🔑 رمز عبور پر شد، 🖱 دکمهٔ ورود کلیک شد»؛ راهنمای OTP برای پیام‌رسان‌ها
  * تنظیم جدید auto_login_on_open (پیش‌فرض روشن) + docstring نسخهٔ ۲.۶.۰
- اصلاحات static/index.html: دراپ‌داون «مرورگر ترجیحی» به ۵ گزینه (خودکار (بهترین)/Edge/Chrome/کرومیوم داخلی/Firefox) + دکمهٔ «🔧 نصب کرومیوم داخلی» با confirm و toast + توضیح فارسی زیر آن؛ راهنما: دو بخش جدید («مرورگرها: کدام را انتخاب کنم؟ خطای مرورگر نصب نیست» و «ورود خودکار چطور کار می‌کند؟») + به‌روزرسانی شروع سریع؛ فوتر ۲.۶.۰ — اعتبارسنجی JS با node --check: OK، همهٔ IDها موجود
- README.md: بولت ۲.۶.۰ در فهرست امکانات + بازنویسی بخش «نصب مرورگر» (نصب خودکار + فرمان firefox) + بخش جدید «🔑 ورود خودکار»
- تست E2E واقعی (tests/tmp/test_v26.py + v26_server.py + v26_pages.py) — سرور واقعی + Playwright واقعی + صفحات ورود شبیه‌سازی‌شده با همان سلکتورهای واقعی پلتفرم‌ها: ۲۴/۲۴ پاس:
  * اینستاگرام (تک‌صفحه): یوزرنیم و رمز هر دو پر شد + دکمهٔ ورود کلیک شد + ناوبری به صفحهٔ موفقیت با مقادیر درست در query
  * توییتر (دومرحله‌ای): «بعدی» خودکار کلیک شد → رمز پر شد → Log in کلیک شد → موفقیت
  * تلگرام (تلفنی): شماره پر شد + Next کلیک شد → صفحهٔ کد OTP + پیام راهنمای فارسی
  * «باز کردن سایت» روی صفحهٔ ورود → ورود خودکار کامل بدون نیاز به اکشن جدا
  * «باز کردن سایت» روی صفحهٔ عادی → بدون خطا
  * بدون اطلاعات ذخیره → پیام راهنمای فارسی (نه خطای خام)
  * کانال صریح chromium کار کرد (اثبات رفع باگ پاس‌دادن کانال)؛ اندپوینت نصب: chrome رد ۴۰۰، chromium/firefox پذیرفته
  * بعد از تست، پوشه‌های دیتای تست (config/profiles/...) پاک شدند تا وارد ZIP نشوند
- سایت Next.js → v2.6.0: data.ts (AGENT_VERSION)، header، footer، download-section (چیپ «نسخهٔ ۲.۶.۰»)، api/download (ParsAgent-v2.6.0.zip)، engines.tsx (بولت‌های ۵ مرورگر + نصب خودکار)، api/agent/files (ORDER + WORK_LOG.md)، public/panel.html (دراپ‌داون ۵ گزینه + دکمهٔ نصب دمو + فوتر ۲.۶.۰)
- launcher.py: ارتقای برچسب نسخه به ۲.۶.۰ (هدر، app_version بستهٔ آفلاین، لیبل UI)
- WORK LOG: از این نسخه، کپی کامل worklog.md داخل خود بسته هم قرار می‌گیرد (parsagent/WORK_LOG.md) تا همراه دانلود کاربر همیشه همراهش باشد و هرگز گم نشود

Stage Summary:
- هر سه باگ گزارش‌شده ریشه‌یابی و با تست واقعی مرورگر اثبات‌شده رفع شدند: خطای کرومیوم (نصب خودکار از بستهٔ آفلاین/آینه)، باگ انتخاب مرورگر (کانال همیشه پاس داده می‌شود + Firefox و کرومیوم داخلی جدید)، ورود خودکار کامل (یوزرنیم+رمز+کلیک دکمه برای هر ۷ پلتفرم + ورود خودکار در «باز کردن سایت» + فرم دومرحله‌ای + پیام خطای سایت به فارسی)
- نسخهٔ کامل ParsAgent 2.6.0 با ZIP از دکمهٔ دانلود سایت قابل دریافت است؛ هیچ فیچر قبلی حذف نشد (طبق قاعدهٔ کاربر)
- WORK LOG دائمی در دو جا نگهداری می‌شود: sandbox + داخل بستهٔ دانلودی
---
Task ID: 12 (main-orchestrator)
Agent: Z.ai Code
Task: درخواست کاربر — گزارش خطای نصب آنلاین ناقص روی سیستم تازه: pip برای greenlet/pydantic-core/httptools/pyyaml/watchfiles کامپایل سورس شروع می‌کند و با «linker link.exe not found / Microsoft Visual C++ 14.0 or greater is required / maturin failed» شکست می‌خورد و آخر پیام: «بعضی ماژول‌ها هنوز نصب نشده‌اند: fastapi، uvicorn، multipart، playwright»

Work Log:
- ریشه‌یابی: لاگ کاربر نشان می‌داد pip با مفسرِ C:\...\Python313\python3.13t.exe اجرا شده — یعنی لانچر زیر پایتونِ free-threaded باز شده؛ برای cp313t هیچ wheel آماده‌ای وجود ندارد، پس pip سراغ کامپایل سورس می‌رود و چون MSVC/Rust نصب نیست، ۵ پکیج شکست می‌خورند. نسخهٔ ۲.۷ فقط «هشدار» می‌داد و باز هم نصب را شروع می‌کرد.
- parsagent/launcher.py — بازسازی کامل نسخهٔ ۲.۸.۰ (ظاهر/رفتار UI و همهٔ قابلیت‌های قبلی دست‌نخورده):
  * _py_probe(exe): پروب سبک هر مفسر (نسخه + Py_GIL_DISABLED + SOABI) برای تشخیص free-threaded
  * _candidate_interpreters(): جست‌وجوی ۴-لایه — python.exe کنار مفسر فعلی (python3.13t همیشه هم‌زدهٔ python.exe استاندارد است)، py -0p (رجکس مسیر exe؛ رد WindowsApps)، where python (ویندوز) / which (لینوکس)، مسیرهای نصب رایج (LOCALAPPDATA/ProgramFiles × Python3*)
  * find_standard_python(): بهترین پایتون استاندارد ۳.۱۰..۳.۱۳ (fallback: هر استاندارد ≥3.10) — tها و Store stubها و <3.10 رد می‌شوند
  * main(): اگر مفسر فعلی free-threaded بود و PARSAGENT_SWITCHED ست نبود → پیدا/تعویض با os.execv (آرگومان‌های کنسلی حفظ می‌شوند؛ گارد ضدحلقه) — قبل از GUI و قبل از همهٔ حالت‌های کنسلی
  * install_standard_python(): اگر هیچ پایتون استانداردی نبود → دانلود python-3.12.10-amd64.exe از python.org (~۲۶MB، با پیشرفت؛ اول با پروکسی سیستم بعد مستقیم) + نصب خاموش per-user (/quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1) + یافتن مفسر جدید؛ گارد ۳۲بیتی/غیرویندوز با پیام فارسی
  * GUI: دکمهٔ ابزار جدید «🐍 پایتون استاندارد» + _handle_free_threaded (دیالوگ تعویض یا نصب) + on_start مسیر ft را قبل از پیشنهاد نصب قطع می‌کند؛ بعد از نصب، بازگشایی خودکار با پایتون جدید
  * install_deps بازنویسی: pip فقط wheel آماده (--only-binary=:all:) + زنجیرهٔ ۳ تلاش: PyPI → آینهٔ Tsinghua → آینهٔ Aliyun (بدون فیلترشکن)؛ _install_failed با تشخیص فارسی (نسخهٔ پایتون + راه‌ها: دکمهٔ پایتون استاندارد / VPN / بستهٔ آفلاین) — دیگر هیچ کامپایل Rust/C++ (maturin/link.exe) اجرا نمی‌شود
  * _console_mode: سوییچ جدید --install-python (اول چک می‌کند استاندارد هست یا نه)؛ compat_problems با راهنمای دکمهٔ جدید
- parsagent/ParsAgent.bat: اول py launcher (هرگز نسخهٔ t را انتخاب نمی‌کند) → بعد python → پیام فارسی؛ چک سلامت py با py -c قبل از start
- parsagent/panel_server.py: فقط مدخل ۲.۸.۰ در docstring تغییرات
- parsagent/static/index.html: فوتر ۲.۸.۰ + بخش راهنمای جدید «🐍 نصب روی سیستم خام / خطای کامپایل Rust (جدید ۲.۸.۰)» (تعویض خودکار/نصب خودکار/فقط-wheel/آینه‌ها/--install-python)
- parsagent/README.md: بولت صدر لیست «نصب هوشمند روی سیستم خام (۲.۸.۰)» + نکتهٔ دابل‌کلیک bat در بخش نصب + ۲ ردیف عیب‌یابی بازنویسی/جدید (کامپایل Rust/C++ → رفع ۲.۸.۰؛ نصب ناقص/ایندکس)
- سایت Next.js → v2.8.0: data.ts AGENT_VERSION، header، footer، download-section (چیپ «نسخهٔ ۲.۸.۰»)، download route → ParsAgent-v2.8.0.zip؛ features.tsx کارت ۱۳م «نصب هوشمند روی سیستم خام (۲.۸.۰)» با آیکن Wrench بعد از کارت آفلاین؛ public/panel.html فوتر ۲.۸.۰
- اعتبارسنجی در سندباکس:
  * py_compile هر ۵ فایل پایتون OK
  * تست منطق (بدون GUI): پروب مفسر واقعی + تشخیص stubهای free-threaded (gil=1 و SOABI=cp313t) + رد exe نامعتبر؛ ترجیح 3.12 بر 3.14 و fallback به 3.14؛ رد <3.10؛ رجکس py -0p هر دو exe را می‌گیرد؛ main() با ft → re-exec با حفظ آرگومان‌ها؛ ft بدون استاندارد → پیام راهنما بدون exec؛ گارد PARSAGENT_SWITCHED ضدحلقه؛ --install-python از re-exec خودکار جا می‌ماند؛ install_deps مسیر ft را به دیالوگ رفع می‌برد؛ زنجیرهٔ pip: ۳ تلاش فقط-wheel با -i درست در تلاش ۲ و ۳، توقف بعد از موفقیت، دیالوگ خطا با یادآوری ۳ ایندکس؛ install_standard_python روی لینوکس → خطای فارسی «فقط روی ویندوز»
  * سرور پنل واقعی بوت شد: /api/ready → {"ok":true}، فوتر ۲.۸.۰، لاگ بوت پاک
  * bun run lint: صفر خطا؛ dev.log: صفر خطا
  * agent-browser: لندینگ v2.8.0 حاضر (هدر ×۲ + چیپ دانلود)، کارت جدید «نصب هوشمند روی سیستم خام» حاضر، صفر خطای صفحه/کنسول؛ /panel.html فوتر ۲.۸.۰، موبایل 390px بدون سرریز افقی (390=390)؛ GET /api/download → 200 با filename=ParsAgent-v2.8.0.zip
  * ZIP دانلودی: ۹ فایل کامل (نه پچ) شامل launcher.py با همهٔ توابع جدید (find_standard_python/install_standard_python/_reexec/آینه‌ها/only-binary/3.12.10) و ParsAgent.bat جدید — بدون پوشه‌های ران‌تایم و __pycache__
  * سه ایراد تست‌هارنس خودم (stub بدون shebang، اسنپ‌شات زنجیره، شمارندهٔ check_missing) پیدا و اصلاح شد؛ یکی نکتهٔ واقعی بود: پیام خطای نصب حالا می‌گوید ۳ ایندکس خودکار امتحان شد

Stage Summary:
- ParsAgent ۲.۸.۰ آمادهٔ دانلود از دکمهٔ «دانلود سورس کامل (ZIP)» سایت است (۹ فایل کامل — نه پچ)
- خطای امروز کاربر ریشه‌یابی و کامل رفع شد: اجرای لانچر با python3.13t (free-threaded) حالا خودکار به پایتون استانداردِ سیستم تعویض می‌شود؛ اگر نبود، با یک دکمه نسخهٔ ۳.۱۲ دانلود و خاموش نصب می‌شود؛ نصب اینترنتی فقط wheel آماده با ۳ ایندکس (PyPI + Tsinghua + Aliyun) — دیگر maturin/link.exe/MSVC هرگز اجرا نمی‌شود
- روی سناریوی دقیق کاربر (سیستم تازه، فقط پایتون t): دابل‌کلیک ParsAgent.bat → py استاندارد یا تعویض خودکار → نصب فقط-wheel موفق
- WORK LOG دائمی طبق قانون کاربر ادامه دارد — این بخش هرگز پاک نشود

---
Task ID: v2.9.0
Agent: main (Z.ai Code)
Task: رفع دو باگ گزارش‌شدهٔ کاربر: ①گزینه‌های «گروه ۴ — فعال برای کدام پلتفرم‌ها؟» در تنظیمات درست فعال/غیرفعال نمی‌شدند ②«فیلد ورود دیده نشد» روی اینستاگرام در اجرای سریع، در حالی که صفحه در Edge باز بود و فیلدها خالی می‌ماندند (عنوان صفحه: «Instagram»)

Work Log:
- ریشه‌یابی باگ ۱ (گروه ۴): چیپ‌های per-platform در static/index.html از <label class="chip"> با چک‌باکس display:none ساخته می‌شدند؛ کلیک روی label دو بار تاگل می‌کرد: یک‌بار هندلر onclick دستی (c.checked = !c.checked) و یک‌بار رفتار پیش‌فرض مرورگر (فوروارد کلیک به چک‌باکس داخل label) → نتیجهٔ خنثی؛ وضعیت همیشه به حالت اول برمی‌گشت و ذخیره هم همان مقدار قبلی را می‌فرستاد
  * رفع: e.preventDefault() در ابتدای هندلر onclick (خط ~1197 static/index.html) — با کامنت توضیحی فارسی
- ریشه‌یابی باگ ۲ (فیلد ورود اینستاگرام) — سه لایه روی هم:
  1) _wait_visible فقط «اولین» نتیجهٔ هر سلکتور (locator.first) را چک می‌کرد؛ اینستاگرام نسخهٔ مخفی/تکراری از فیلد (تغییر حساب) بالاتر از نسخهٔ مرئی دارد → is_visible روی مخفی False می‌شد و کل سلکتور دور می‌افتاد
  2) سلکتورها فقط انگلیسی بودند؛ ولی ضد شناسایی خودمان زبان مرورگر را fa-IR می‌گذارد و سایت‌ها (اینستاگرام) aria-label/placeholder را فارسی رندر می‌کنند → input[aria-label*='username' i] نمی‌گرفت
  3) ساختار جدید صفحهٔ ورود اینستاگرام (۲۰۲۵) ممکن است name/autocomplete نداشته باشد
  * رفع در panel_server.py:
    - تابع جدید _first_visible(page, sels): همهٔ نتایجِ هر سلکتور (تا سقف _SEL_CAP=10) برای «مرئی بودن» چک می‌شود و اولین المان مرئی به‌صورت رشتهٔ «sel >> nth=i» برمی‌گردد
    - _wait_visible بازنویسی با _first_visible (خروجی target با سینتکس nth)
    - click_first ارتقا یافت: به‌جای .first، همهٔ نتایج تا سقف ۱۰ چک و اولین دکمهٔ مرئی کلیک می‌شود (برای submit)
    - _dismiss_cookie_walls هم با _first_visible + hclick بازنویسی شد
    - LOGIN_FLOW همهٔ ۷ پلتفرم بازنویسی: سلکتورهای فارسی (aria-label/placeholder: «نام کاربری»، «شماره تلفن»، «رمز»، «ایمیل»، «موبایل») + انگلیسی + autocomplete/name + آخرین راه GENERIC_USER («اولین فیلد متنی مرئی داخل فرم»: form input[type='text'] / form input[type='email'] / form input:not([type])) و GENERIC_TEL برای پیام‌رسان‌ها
    - لاگ تشخیصی: اگر فیلد ورود پیدا نشد، صفات همهٔ inputهای صفحه (type/name/autocomplete/aria-label/placeholder/visible — بدون مقادیر حساس) در تب «لاگ‌ها» ثبت می‌شود (eval_on_selector_all)
    - رفع مثبت کاذب «از قبل وارد شده»: اینستاگرام گاهی از /accounts/login/ به صفحهٔ اصلی هدایت می‌کند ولی فرم ورود همان‌جاست؛ حالا قبل از اعلام «لاگین کامل»، ۳ ثانیه برای فرم ورود نظرسنجی می‌شود (پروب)
    - پیام خطای «فیلد ورود دیده نشد» به‌روز شد (اشاره به ثبت فیلدها در لاگ)
- افزایش نسخه ۲.۸.۰ → ۲.۹.۰:
  * parsagent/panel_server.py: بخش ۲.۹.۰ در docstring تغییرات
  * parsagent/launcher.py: APP_VERSION="2.9.0" + docstring بخش ۲.۹.۰ (بخش ۲.۸.۰ حفظ شد) + متن هدر GUI لانچر
  * parsagent/static/index.html: فوتر «نسخهٔ پنل ۲.۹.۰» + بازنویسی راهنمای «ورود خودکار چطور کار می‌کند؟» (رفتار جدید موتور فیلد + لاگ تشخیصی)
  * public/panel.html: فوتر ۲.۹.۰
  * سایت: data.ts AGENT_VERSION=v2.9.0، header.tsx، footer.tsx، download-section.tsx چیپ «نسخهٔ ۲.۹.۰»، download route → filename=ParsAgent-v2.9.0.zip
  * features.tsx: کارت ۱۴ «ورود خودکار مقاوم + تنظیمات درست (۲.۹.۰)» با آیکن LogIn بعد از کارت نصب هوشمند
  * parsagent/README.md: بولت «🔐 ورود خودکار مقاوم (۲.۹.۰)» + ۲ ردیف عیب‌یابی بازنویسی/جدید («فیلد ورود دیده نشد» با رفتار ۲.۹.۰ + ردیف جدید «چیپ‌های گروه ۴ تغییر نمی‌کردند»)
- اعتبارسنجی در سندباکس:
  * py_compile هر ۵ فایل پایتون OK (یک خطای سینتکس رشتهٔ JS لاگ تشخیصی حین کار پیدا و اصلاح شد)
  * تست Playwright واقعی (tests/test_login_engine.py): HTML شبیه ورود ۲۰۲۵ اینستاگرام (فیلد مخفی تکراری با name=username + فیلد مرئی فقط با لیبل فارسی) → موتور جدید فیلد مرئی فارسی را برمی‌گرداند (input[aria-label*='نام کاربری'] >> nth=0)، همان سلکتورهای قدیمی ۲.۸.۰ روی همان صفحه None برمی‌گردانند (اثبات ریشهٔ باگ)، یوزرنیم تایپ شد، رمز پیدا و تایپ شد، دکمهٔ «ورود» فارسی کلیک شد، fallback عمومی فیلد بی‌صفات را با nth=1 (رد نسخهٔ مخفی) پیدا کرد، لاگ تشخیصی خروجی داد، LOGIN_FLOW هر ۷ پلتفرم ساختار درست دارد — ALL TESTS PASSED
  * سرور پنل واقعی بوت شد (پورت 8765، /api/ready → {"ok":true})
  * agent-browser روی پنل: کلیک روی چیپ «📸 اینستاگرام» → on:false/checked:false؛ کلیک دوم → on:true/checked:true (دقیقاً یک تاگل در هر کلیک — قبلاً صفر)؛ «ذخیره همهٔ تنظیمات» → /api/settings برگرداند instagram:False و بقیه True؛ سپس تنظیمات به حالت اول برگشت
  * کنسول و خطاهای صفحه پنل: صفر
  * bun run lint: صفر خطا
  * وب‌سایت: v2.9.0 در هدر/فوتر/چیپ، کارت جدید «ورود خودکار مقاوم + تنظیمات درست» حاضر، موبایل 390px بدون سرریز (390=390)، صفر خطا؛ /panel.html فوتر ۲.۹.۰
  * GET /api/download → 200 با filename=ParsAgent-v2.9.0.zip؛ محتوای ZIP بررسی شد: ۹ فایل کامل + پوشهٔ static — شامل _first_visible، سلکتورهای فارسی، preventDefault گروه ۴ و APP_VERSION=2.9.0

Stage Summary:
- ParsAgent ۲.۹.۰ آمادهٔ دانلود از دکمهٔ «دانلود سورس کامل (ZIP)» سایت (ParsAgent-v2.9.0.zip — ۹ فایل کامل، نه پچ)
- باگ ۱ رفع شد: چیپ‌های گروه ۴ (per-platform ضد شناسایی) حالا با یک کلیک درست فعال/غیرفعال می‌شوند و بعد از «ذخیره» در settings.json می‌نشینند
- باگ ۲ رفع شد: موتور جدید فیلد ورود (همهٔ نتایج هر سلکتور + سلکتور فارسی/انگلیسی + fallback عمومی «اولین فیلد متنی مرئی داخل فرم» + لاگ تشخیصی صفات فیلدها + پروب ضد مثبت کاذب لاگین) — سناریوی کاربر (صفحه باز در Edge، لیبل فارسی، فیلد مخفی تکراری) در تست سندباکس بازتولیع و پاس شد؛ سلکتورهای قدیمی روی همان صفحه شکست می‌خوردند
- WORK LOG دائمی طبق قانون کاربر ادامه دارد — این بخش هرگز پاک نشود

---
Task ID: v2.10.0
Agent: main (Z.ai Code)
Task: سه درخواست کاربر — ①«لایک زدن کار نمی‌کنه» ②تحقیق: کدام پلتفرم‌ها با نسخهٔ وب استوری می‌گذارند (اکشن استوری فقط برای آن‌ها بماند) ③در تنظیمات «هوش مصنوعی — سرویس، مدل و کلیدها» زیر هر فیلد API لینک اخذ و آموزش در یک «؟» جداگانه

Work Log:
- تحقیق واقعی با ۵ جستجوی وب قبل از تغییر کد:
  * اینستاگرام: اجازهٔ انتشار استوری از نسخهٔ وب را نمی‌دهد — فقط اپ موبایل (یا Meta Business Suite برای اکانت تجاری؛ منابع متعدد ۲۰۲۵: «Instagram Stories cannot be created or published from a desktop computer (yet)»)
  * فیسبوک: از وب می‌شود استوری «عکس» گذاشت (راهنمای رسمی: Create story → Create a photo story → آپلود از سیستم)؛ ویدیو فقط از اپ
  * تلگرام: استوری فقط برای پریمیوم و فقط از اپ موبایل — وب آن را پشتیبانی نمی‌کند
  * لینکدین: استوریها از سپتامبر ۲۰۲۱ حذف شدند؛ توییتر/X: اصلاً استوری ندارد (Fleets از ۲۰۲۱ مرده)
  * بله/روبیکا: نسخهٔ وب استوری ندارد → جمع‌بندی: اکشن استوری فقط برای فیسبوک می‌ماند
- ریشه‌یابی «لایک کار نمی‌کند» — سه علت واقعی در موتور قدیمی:
  ①) چک نمی‌شد اصلاً وارد شده‌اید یا نه (فید بدون لاگین = هیچ دکمه‌ای؛ نتیجهٔ خام «لایک انجام شد: ۰»)
  ②) دکمهٔ لایک در «کل صفحه» جست‌وجو می‌شد → لایکِ کامنت/دکمه‌های جانبی به‌جای پست فید زده می‌شد
  ③) سلکتور «شاملِ Like» دکمهٔ «Liked» (پستِ قبلاً لایک‌شده!) را هم می‌گرفت → یعنی گاهی لایکِ شما را «برداشتن» می‌کرد
- parsagent/panel_server.py — موتور لایک مقاوم ۲.۱۰.۰ (بازنویسی کامل، مشترک بین ۴ پلتفرم):
  * LIKE_ENGINES (سلکتور posts/like/unlike هر پلتفرم) + LOGIN_URL_MARKERS + _looks_logged_out (آدرس لاگین یا فرم رمزِ نمایان — پوشش حالت اینستاگرام که فرم را روی آدرس اصلی می‌آورد)
  * _wait_feed: صبر تا ۲۵ ثانیه برای اولین پستِ مرئی (سلکتور برنده برگردانده می‌شود)
  * _like_click_in: کلیک اولین دکمهٔ مرئیِ لایک «فقط داخل همان پست» (نه کل صفحه) + scroll_into_view + مکث انسانی قبل از کلیک
  * _like_is_verified: بعد از کلیک، تغییر دکمه به Unlike/برداشتن پسند چک می‌شود (در لاگ ✓ می‌گیرد)
  * _like_feed: پیمایش پست‌به‌پست، پرش خودکار از لایک‌شده‌ها (سلکتورشان دیگر Like نیست)، اسکرول تدریجی برای پست‌های بعدی، توقف پس از ۳ دور بی‌نتیجه
  * _run_like: چک ورود → پیام فارسی واضح «اول دکمهٔ ورود را بزنید» به‌جای «لایک انجام شد: ۰»؛ پیام متمایز برای فیدِ بارگیری‌نشده و «همه از قبل لایک شده‌اند»
  * اینستاگرام: سلکتورهای section-دار اول امتحان می‌شوند (نوار اکشن پست — نه لایکِ کامنت) + فارسی/انگلیسی
  * توییتر: data-testid='like' مستقل از زبان + article[data-testid='tweet']
  * فیسبوک: aria-label دقیق 'Like' (نه شامل — چون «Liked» هم شامل است!) + :text-is + پست = div[role=article][aria-posinset] (کامنت‌های تودرتو match نمی‌شوند)
  * لینکدین: aria-label^='Like' برای برچسب داینامیک («Like John's post») + div[data-id^='urn:li:activity']
- parsagent/panel_server.py — استوری واقعی:
  * ACTIONS اینستاگرام: post_story حذف شد + کامنت دلیل؛ تابع ig_post_story حذف شد
  * ACTIONS فیسبوک: post_story (عکس) اضافه شد؛ fb_post_story جدید: /stories → «Create story» → «Create photo story» → ورودی فایل (accept=image) → «Share story» با سلکتورهای EN/FA و پیام‌های کمکی برای ادامهٔ دستی؛ ویدیو با پیام روشن رد می‌شود («ویدیو از وب ممکن نیست»)
  * جدول راهنمای طبیعی اینستاگرام: «استوری در روز» → «استوری در روز (فقط اپ موبایل)»
- parsagent/static/index.html — راهنمای کلیدهای API (درخواست ۳):
  * CSS جدید .keyhint (دکمهٔ «؟» سبز) + .keybox (جعبهٔ آموزش با لینک)؛ JS تاگل با کلیک
  * هر ۸ فیلد کلید بازسازی شد (zai/openai/anthropic/gemini/groq/deepseek/openrouter/custom): label → div (تا لینکِ داخل جعبه تداخل کلیکی با فیلد نداشته باشد) + دکمهٔ «؟» + جعبهٔ مخفی شامل ۲-۳ مرحلهٔ آموزش + لینک مستقیم اخذ کلید + نکته (رایگان بودن، پیشوند کلید، نیاز به فیلترشکن در ایران)
  * URLها با تحقیق تأیید شد: z.ai/manage-apikey/apikey-list · platform.openai.com/api-keys · console.anthropic.com/settings/keys · aistudio.google.com/apikey · console.groq.com/keys · platform.deepseek.com/api_keys · openrouter.ai/keys · ollama.com
  * عنوان بخش و پاراگراف مقدمه به «؟» اشاره می‌کند؛ فوتر ۲.۱۰.۰
- parsagent/static/index.html — راهنما: دو بخش جدید («❤ لایک چطور کار می‌کند؟ چرا قبلاً کار نمی‌کرد؟» با سه علت واقعی و «📸 استوری از کدام پلتفرم‌ها و با کدام نسخه؟» با جدول کامل ۷ پلتفرم) + به‌روزرسانی متن تب هوش مصنوعی (اشاره به «؟» هر فیلد)
- parsagent/launcher.py: APP_VERSION=2.10.0 + docstring بخش ۲.۱۰.۰ + هدر GUI
- parsagent/README.md: دو بولت جدید (موتور لایک + استوری واقعی + راهنمای کلیدها) + ۳ ردیف عیب‌یابی (لایک کار نمی‌کرد؛ استوری اینستاگرام نبود؛ کلید API را از کجا بگیرم)
- سایت Next.js → v2.10.0: data.ts AGENT_VERSION، header، footer، download-section (چیپ «نسخهٔ ۲.۱۰.۰»)، download route → ParsAgent-v2.10.0.zip؛ features.tsx کارت ۱۵ «موتور لایک بازنویسی‌شده + استوری واقعی + راهنمای کلیدها (۲.۱۰.۰)» با آیکون Heart؛ data.ts دموی تعاملی: استوری از اکشن‌های اینستاگرام حذف و به فیسبوک اضافه شد؛ public/panel.html: کل قابلیت «؟» (۸ جعبه + تاگل + لینک) + فوتر ۲.۱۰.۰
- اعتبارسنجی در سندباکس:
  * py_compile هر ۵ فایل پایتون OK · bun run lint صفر خطا
  * تست Playwright واقعی (tests/tmp/test_like_engine_v210.py) با Chromium و ماک‌های شبیه DOM روز هر پلتفرم — ۲۳/۲۳ پاس:
    - اینستاگرام: ۵ لایک از فیدِ بی‌نهایت (پست تازه با اسکرول می‌آید)؛ پستِ از‌قبل‌لایک‌شده دست نخورد (لایک برنداشته شد؟ نه)؛ دکویِ لایکِ کامنتِ مخفی هرگز کلیک نشد؛ تأیید ✓ بعد از هر کلیک
    - توییتر: ۴ لایک با data-testid (مستقل از زبان)؛ unlike رد شد
    - فیسبوک: دقیقاً ۲ کلیک از ۲ قابل‌لایک (پیام «۲ از ۵ … همه از قبل لایک شده‌اند»)؛ «Liked» → «Like» برنگشت؛ «Like Page» بیرون از پست‌ها کلیک نشد
    - لینکدین: ۲ لایک با برچسب داینامیک؛ Unlike رد شد
    - لاگین‌نشده: پیام فارسی «وارد نشده‌اید — دکمهٔ ورود» (هم از URL، هم از فرم رمز روی آدرس اصلی)
    - فید خالی: _wait_feed → None؛ همه‌لایک‌شده: پیام «هیچ پستِ لایک‌نشدنی»
    - استوری فیسبوک: فلو کامل (Create story → photo story → آپلود عکس واقعی → Share story) موفق؛ ویدیو با پیام روشن رد شد
    - دو ایراد ماکِ تست حین کار پیدا و اصلاح شد (article/svg بدون محتوا اندازهٔ صفر → نامرئی؛ textContent دکمهٔ FB باید همراه aria-label تغییر کند) — منطق موتور سالم بود چون سایت‌های واقعی هر دو را تغییر می‌دهند
  * سرور پنل واقعی بوت شد: /api/ready OK؛ /api/options: اینستاگرام بدون post_story، فیسبوک با post_story
  * agent-browser روی پنل واقعی: فوتر ۲.۱۰.۰؛ ۸ دکمهٔ «؟»؛ کلیک → جعبه با لینک z.ai/manage-apikey/apikey-list و ۳ مرحله باز و بسته می‌شود؛ دراپ‌داون اجرای سریع: اینستاگرام بدون «انتشار استوری» و فیسبوک با «انتشار استوری (عکس)»؛ دو بخش راهنمای جدید حاضر؛ صفر خطای صفحه/کنسول
  * agent-browser روی سایت: v2.10.0 (هدر/چیپ/فوتر) و v2.9.0 غایب؛ کارت جدید حاضر؛ موبایل 390px بدون سرریز افقی (390=390)؛ فوتر چسبان در هر دو حالت (صفحهٔ کوتاه → چسبیده به پایین با viewport 1400؛ صفحهٔ بلند → پایین محتوا بدون هم‌پوشانی)؛ /panel.html: ۸ «؟» + تاگل + فوتر ۲.۱۰.۰
  * GET /api/download → 200 با filename=ParsAgent-v2.10.0.zip؛ محتوای ZIP (۱۱ entry) تأیید شد: LIKE_ENGINES و fb_post_story و keyhint و z.ai لینک و APP_VERSION=2.10.0 همه حاضرند؛ بدون __pycache__ و پوشه‌های ران‌تایم
  * VLM روی اسکرین‌شات جعبهٔ راهنمای باز: «چیدمان صحیح است و هیچ هم‌پوشانی یا بهم‌ریختگی وجود ندارد»
- WORK LOG: دو ورودی گمشدهٔ v2.8.0/v2.9.0 در نسخهٔ همراه بسته (parsagent/WORK_LOG.md — که Task 11/2.7.0 آخرین ورودی‌اش بود) جبران و وارد شد تا قانون «هرگز گم نشود» کامل بماند

Stage Summary:
- هر سه درخواست کاربر انجام و با تست واقعی مرورگر اثبات شد: موتور لایک جدید (چک ورود + پست‌به‌پست + سلکتور دقیق فارسی/انگلیسی + تأیید + اسکرول) برای هر ۴ پلتفرم؛ اکشن استوری فقط برای فیسبوک (تنها پلتفرمی که از وب استوری عکس می‌پذیرد) و از اینستاگرام حذف شد با دلیلِ مستند در راهنما؛ زیر هر فیلد کلید API دکمهٔ «؟» با آموزش گام‌به‌گام + لینک مستقیم اخذ کلید + نکتهٔ ایران
- ParsAgent-v2.10.0.zip از دکمهٔ «دانلود سورس کامل (ZIP)» سایت آماده است (۱۱ فایل کامل — نه پچ)
- هیچ فیچر دیگری حذف نشد؛ فقط post_story اینستاگرام حذف شد چون پلتفرم خودش اجازه نمی‌دهد (طبق تحقیق و درخواست صریح کاربر)
- WORK LOG دائمی طبق قانون کاربر ادامه دارد — این بخش هرگز پاک نشود

═══════════════════════════════════════════════════════════════════════════════
نسخهٔ ۲.۱۱.۰ — ۲۰۲۵ (دو درخواست کاربر: «۲.۱۰ همون ۲.۹ بود» + «واتساپ وب هم اضافه کن»)
═══════════════════════════════════════════════════════════════════════════════

گزارش کاربر ۱: «نسخهٔ 2.10 در واقع همون 2.9 ئه و تغییر خاصی توش مشاهده نکردم»
- ریشه‌یابی: ZIP خروجی بررسی شد — تغییرهای ۲.۱۰ واقعاً داخلش بودند (LIKE_ENGINES،
  keyhint «؟»، حذف استوری اینستاگرام، APP_VERSION=2.10.0)؛ ولی تقریباً همه در دلِ
  کد یا جزئیات ریز بودند و در ظاهر پنل دیده نمی‌شدند
- راه‌حل پایدار: کادر «🎉 چه چیز تازه است؟» — بالای پنل، سبز، بازشونده، پیش‌فرض باز؛
  تغییرهای ۲.۱۱.۰ + یادآوری تغییرهای پنهانِ ۲.۱۰.۰ را فهرست می‌کند؛ از این به بعد
  هر نسخه تغییراتش را همین‌جا نشان می‌دهد (static/index.html: CSS .whatsnew + مارکاپ)

گزارش کاربر ۲: «واتساپ وب هم بهش اضافه کن» — پلتفرم هشتم اضافه شد:

- parsagent/panel_server.py:
  * PLATFORMS += whatsapp (🟢 واتساپ، web.whatsapp.com)؛ PLAT_IDS و همهٔ حلقه‌های
    خودکار (open، login، per-platform stealth، state، زمان‌بندی) خودش را می‌گیرد
  * ورود مخصوص واتساپ — LOGIN_FLOW["whatsapp"]={"qr": True} و شاخهٔ QR در
    _generic_login → _wa_qr_login: تشخیص «از قبل وارد شده» (فهرست چت‌ها)، «صبر
    هوشمند» تا ۱۸۰ ثانیه با نظرسنجی، تشخیص لحظهٔ اسکن، و پیام‌های فارسی روشن برای
    «اسکن نشد» (راهنمای گوشی: واتساپ ← تنظیمات ← دستگاه‌های متصل ← اتصال دستگاه)
    و «QR دیده نشد» (حالت اتصال با شماره تلفن/لودینگ)
  * اکشن send_message (wa_send): چند گیرنده با ویرگول، فاصلهٔ انسانی ۸–۱۵ ثانیه
    بین گیرنده‌ها، پیام چندخطی با Shift+Enter (مثل خود واتساپ)، ارسال با Enter و
    در صورت لغزیدن با دکمهٔ ارسال، و تأییدِ «کادر خالی شد = ارسال شد»
  * _wa_search_open_chat با دو محافظ:
    (۱) پاک کردن جستجوی قبلی با Ctrl+A+Delete — واتساپ متنِ جستجوی بی‌نتیجه را
        نگه می‌دارد و نام جدید به قبلی می‌چسبید (کشف در تست)
    (۲) 🛡 حفاظت «چت اشتباه»: بعد از باز شدن چت، نامِ هدر با هدف تطبیق داده
        می‌شود (شامل/کلمه‌ای — «رضا» با «رضا محمدی» می‌خواند)؛ اگر جستجو نتیجه
        نداشت و چتِ قبلی باز مانده بود، ارسال لغو می‌شود — پیام به چت اشتباه نمی‌رود
  * سلکتورها: WA_READY_SELS (چت-لیست/جستجو در دو نسل DOM)، WA_QR_SELS،
    WA_MSGBOX_SELS (فوتر چتِ باز)، WA_SEND_SELS، WA_HEADER_SELS (نام چت در هدر)
  * SANCTIONED_HOSTS += whatsapp.com/whatsapp.net — واتساپ از IP ایران فیلتر است؛
    خطای شبکه حالا همان راهنمای فارسی پروکسی/VPN را می‌دهد
  * GUIDE و ACTIONS و SAFE_DELAY واتساپ: راهنمای صریح ریسک اسپم (سخت‌گیرترین
    پیام‌رسان؛ فقط به مخاطبینِ دارای شمارهٔ شما؛ گروه‌های خودتان مطمئن‌ترین)
- parsagent/dm_reply.py: DM_PAGES += whatsapp (فهرست چت‌ها + کادر فوتر چت باز؛
  خوانندهٔ عمومی پیام‌ها با message-out/message-in خودکار جهت را تشخیص می‌دهد)
- parsagent/ai_agent.py: PLATFORM_INFO += whatsapp (چت کوتاه شخصی، بدون هشتگ) +
  whatsapp به فهرست پلتفرم‌های پیش‌فرض پاسخ‌گوی دایرکت
- parsagent/static/index.html: کادر «چه چیز تازه است؟» (بالا)؛ کارت QR در «ورود
  خودکار» (واتساپ اسم و رمز ندارد — ۳ مرحلهٔ اسکن)؛ بخش راهنمای «🟢 واتساپ وب
  چطور کار می‌کند؟»؛ ردیف واتساپ در جدول استوری (فقط اپ موبایل)؛ ۷→۸ پلتفرم؛
  عنوان راهنمای پروکسی شامل واتساپ؛ فوتر ۲.۱۱.۰
- parsagent/launcher.py: APP_VERSION=2.11.0 + docstring ۲.۱۱.۰ + هدر GUI
- parsagent/README.md: بولت‌های واتساپ + کادر چه‌چیز-تازه + بخش «🟢 واتساپ وب» +
  ۴ ردیف عیب‌یابی (باز نشدن/QR/گیرنده/تغییرات نامرئی)
- سایت Next.js → v2.11.0: data.ts (AGENT_VERSION + پلتفرم واتساپ در دموی تعاملی)،
  platform-icons (MessageCircle سبز)، features.tsx کارت «پلتفرم هشتم: واتساپ وب +
  کادر چه چیز تازه است؟ (۲.۱۱.۰)»، header/footer/چیپ دانلود، route → ParsAgent-v2.11.0.zip؛
  public/panel.html بازسازی شد با snapshot واقعی API (۸ پلتفرم در options)
- اعتبارسنجی در سندباکس:
  * py_compile همهٔ فایل‌ها OK · bun run lint صفر خطا
  * تست Playwright واقعی (tests/tmp/test_whatsapp_v211.py) با ماکِ شبیه DOM
    واتساپ وب (جستجوی زندهٔ contenteditable، role=listitem، هدر چت، Enter=ارسال،
    Shift+Enter=سطر، QR با اسکنِ بعد از ۲.۵ ثانیه) — ۱۶/۱۶ پاس:
    - ورود: از قبل وارد ✓ · QR بعد از تأخیر تشخیص شد ✓ · اسکن نشد → راهنمای گوشی ✓ · QR دیده نشد ✓
    - ارسال: بدون ورود → پیام راهنمای QR ✓ · بدون پارامتر ✓ · تک‌گیرنده + چندخطی ✓ ·
      چندگیرنده (۱ رفت، ۱ «نام ناموجود» اعلام شد) ✓ · اسم کوتاه تطبیق خورد ✓
    - حفاظت «چت اشتباه»: جستجوی بی‌نتیجه → هیچ پیامی به چت قبلی نرفت ✓
    - دو باگ واقعی حین تست کشف و همان لحظه رفع شد: متنِ جستجوی قبلی مانده بود
      (→ Ctrl+A+Delete قبل از تایپ) و ماکِ تست r-string لازم داشت (درس: '\n' داخل
      ماکِ غیر-raw کل <script> را می‌کُشد)
  * سرور پنل واقعی بوت شد: /api/ready OK؛ /api/options: ۸ پلتفرم، واتساپ با
    open/login/send_message، راهنمای واتساپ در guide
  * agent-browser: سایت — v2.11.0 (هدر/فوتر/چیپ) و کارت جدید؛ دموی تعاملی:
    انتخاب واتساپ → «ارسال پیام به مخاطب/گروه» → اجرای تسک → لاگ whatsapp.send_message؛
    پنل — کادر چه‌چیز-تازه ✓، دراپ‌داون ۸ پلتفرم با 🟢 واتساپ ✓، کارت QR در ورود
    خودکار (بدون فیلد یوزر/رمز) ✓، فوتر ۲.۱۱.۰ ✓؛ موبایل 390px بدون سرریز (390=390)
  * GET /api/download → 200 با filename=ParsAgent-v2.11.0.zip؛ محتوای ZIP تأیید شد:
    APP_VERSION=2.11.0، WA_READY_SELS/_wa_qr_login/whatsapp×14، whatsnew×11،
    whatsapp در dm_reply/ai_agent؛ بدون __pycache__ و پوشه‌های ران‌تایم
  * VLM روی اسکرین‌شات پنل: «کادر سبز چه‌چیز-تازه بالای صفحه با فهرست تغییرات ✓،
    چیدمان تمیز بدون هم‌پوشانی ✓، فوتر نسخهٔ پنل ۲.۱۱.۰ ✓»

Stage Summary:
- هر دو درخواست کاربر انجام شد: (۱) پاسخ به «تغییری ندیدم» با کادر دائمی «چه چیز
  تازه است؟» که از این پس تغییرات هر نسخه را به چشم نشان می‌دهد + یادآوری تغییرهای
  پنهان ۲.۱۰؛ (۲) واتساپ وب به‌عنوان پلتفرم هشتم کامل شد: ورود QR با صبر هوشمند،
  ارسال پیام چندگیرنده با حفاظت چت-اشتباه، پاسخ‌گوی دایرکت، AI، راهنمای ریسک اسپم
- ParsAgent-v2.11.0.zip از دکمهٔ «دانلود سورس کامل (ZIP)» سایت آماده است (فایل‌های کامل — نه پچ)
- هیچ فیچری حذف نشد؛ WORK LOG دائمی طبق قانون کاربر ادامه دارد — این بخش هرگز پاک نشود

════════════════════════════════════════════════════════════════════════════════
نسخهٔ ۲.۱۲.۰ — ۲۰۲۵ (ترمیم کامل «سازنده و چاپ پول»: «نه شد فیلم بسازم نه عکس»)
════════════════════════════════════════════════════════════════════════════════

گزارش کاربر (عیناً): «در بخش سازنده و چاپ پول نه شد فیلم بسازم نه عکس — از api z.ai هم
استفاده کردم» با این خطاها:
- ❌ video: «کتابخانهٔ edge-tts نصب نیست»
- ❌ video: [WinError 10054] اتصال وسط کار به‌اجبار بسته شد
- ❌ image: Z.ai خطای 400 — {"code":"1211","message":"Unknown Model, please check the model code."}
- ❌ image: Z.ai خطای 429 — {"code":"1113","message":"Insufficient balance..."} (JSON خام، بی‌راهنما)
- ❌ image: Pollinations دو بار HTTP 402 Payment Required

### ریشه‌یابی
1. **1211**: کدهای مدلِ کاتالوگ (cogview-4 / cogview-3-flash) مال پلتفرم چینیِ
   open.bigmodel.cn هستند؛ روی api.z.ai بین‌المللی فقط «glm-image» معتبر است
   (تأیید از مستند رسمی docs.z.ai/api-reference/image/generate-image). اندازه‌های
   1024x1792 و 1792x1024 هم در فهرست توصیه‌شده نبودند.
2. **1113**: مدل درست بود ولی موجودی حساب تمام بود — پیام به‌صورت JSON خام نمایش داده می‌شد.
3. **edge-tts نصب نیست**: requirements.txt از ۲.۴.۰ آن را داشت ولی launcher.py فقط
   ۴ ماژول قدیمی (fastapi/uvicorn/multipart/playwright) را چک می‌کرد؛ کاربری که از
   نسخهٔ قبل ارتقا داده بود، «نصب پیش‌نیازها» را لازم نمی‌دید و edge-tts هرگز نصب نمی‌شد.
4. **402**: Pollinations تیر رایگان را محدود کرده (۱ درخواست هم‌زمان + فاصلهٔ ~۱۵
   ثانیه)؛ ساخت چند صحنهٔ پشت‌سرهم بدون صف‌بندی = خطای 402 تضمینی.
5. **10054**: اتصال ناپایدار هیچ تلاش مجددی نداشت — در TTS و فیلم‌نامه و دانلود عکس.

### تغییرها
- **ai_media.py**:
  * کاتالوگ Z.ai → فقط glm-image (حذف CogView) + اعتبارسنجی: مدلِ ذخیره‌شدهٔ کهنه
    (cogview-*) خودکار به glm-image جایگزین می‌شود و در progress اعلام می‌شود
  * سایزها مطابق مستند: مربع 1024x1024، عمودی 768x1344، افقی 1344x768
  * `_http_error_fa`: نقشهٔ خطاها به فارسیِ قابل‌عمل — 1211 (مدل نامعتبر)، 1113
    (موجودی + لینک شارژ z.ai/manage-apikey/apikey-list)، 401، 402 (سهمیهٔ رایگان)، 429
  * `ensure_module`: نصب خودکار یک‌بارهٔ وابستگی‌ها با pip (PyPI، بعد آینهٔ Tsinghua)
    + گارد _DEPS_TRIED؛ generate_video قبل از شروع edge-tts/PIL/imageio_ffmpeg را چک و
    نصب می‌کند؛ _tts_scene هم در ImportError خودش می‌کوشد
  * Pollinations: صف سراسری (_POLL_LOCK) + فاصلهٔ حداقلی ۱۶s (_POLL_MIN_GAP) +
    referrer=parsagent + retry (20/35s) روی 402/429/403/5xx + توکن اختیاری Bearer
    از api_keys.pollinations + پیام فارسی 402
  * retry سه‌مرحله‌ای برای اتصال ناپایدار: TTS (_TTS_RETRY_WAITS)، فیلم‌نامه
    (_LLM_RETRY_WAITS)، دانلود نتیجه (_download_bytes_retry) — همه به‌صورت ثابتِ
    قابل‌تنظیم
  * TTS بازنویسی: کل استریم در بافر جمع می‌شود (فایلِ نیمه‌نوشته حذف شد) + صدای خالی
    → خطای شفاف
- **launcher.py**: REQUIRED += edge_tts / PIL / arabic_reshaper / bidi / imageio_ffmpeg
  (ریشهٔ اصلی باگ نصب) + APP_VERSION=2.12.0
- **panel_server.py**: مستندات سربرگ به‌روز (glm-image)
- **static/index.html**: چیپ و متن کارت عکس؛ راهنمای عیب‌یابی چاپخانه (۵ ردیف:
  1113/1211/402/10054/edge-tts)؛ فیلد «🐢 توکن اختیاری Pollinations» با آموزش «؟»
  و لینک auth.pollinations.ai؛ کادر «چه چیز تازه است؟ ۲.۱۲.۰»؛ فوتر ۲.۱۲.۰
- **README.md**: فهرست عیب‌یابی + متن چاپخانه + تور؛ نسخهٔ ۲.۱۲.۰
- **سایت Next.js**: AGENT_VERSION/chips/route → ParsAgent-v2.12.0.zip؛ کارت ویژگی
  جدید «ترمیم کامل سازنده و چاپ پول (۲.۱۲.۰)»؛ public/panel.html بازسازی شد

### اعتبارسنجی (در سندباکس)
- py_compile همهٔ فایل‌ها OK · bun run lint صفر خطا
- تست واقعی tests/tmp/test_media_v212.py — **۴۴/۴۴ پاس** شامل:
  * کاتالوگ (فقط glm-image؛ بدون حذف openai) · نقشهٔ خطاها (1211/1113/402/401/سایر)
  * سایزها (768x1344/1344x768) · جایگزینی خودکار مدل کهنه + endpoint و payload صحیح
  * 1113 در زنجیره → پیام فارسی به‌جای JSON خام
  * Pollinations: 402→402→موفق؛ توکن Bearer؛ referrer؛ فاصلهٔ صف؛ 402 پایدار → فارسی
  * edge-tts: نبود + شکست نصب → پیام لانچر؛ نصب خودکار موفق → گویندگی OK؛
    دو بار 10054 → سومی موفق؛ سه بار شکست → «بعد از ۳ تلاش ناموفق» فارسی
  * ensure_module: گارد یک‌بار بودن pip (PyPI+Tsinghua فقط در فراخوانی اول)
  * llm_scenes: دو قطعی → سومی موفق · launcher: ۵ ماژول جدید + ۴ قدیمی + 2.12.0
- سرور پنل واقعی بوت شد: /api/ready OK؛ /api/options ۸ پلتفرم؛ /api/ai/image-providers:
  zai=[glm-image]، pollinations=«رایگانِ محدود»، سایزهای جدید
- **تست end-to-end واقعی با شبکه**: POST /api/ai/image (pollinations/flux) → job done →
  GET /media/ai-image-…jpg → JPEG واقعی 768×768 (32KB) دانلود و تأیید شد
- agent-browser: سایت v2.12.0 (هدر/فوتر/چیپ/کارت جدید)؛ پنل: whatsnew ۲.۱۲.۰، فیلد
  توکن Pollinations با «؟» باز‌شونده، راهنمای عیب‌یابی چاپخانه؛ فوتر ۲.۱۲.۰؛
  موبایل 390px بدون سرریز؛ ZIP: filename=ParsAgent-v2.12.0.zip + محتوا تأیید شد

### جمع‌بندی
- همهٔ ۵ خطای گزارش‌شدهٔ «سازنده و چاپ پول» ریشه‌یابی و رفع شد؛ ساخت عکس با تست
  واقعی شبکه اثبات شد و ساخت ویدیو با ۴۴ تست ماک‌محور (مسیر edge-tts/10054/توکن/صف)
- ParsAgent-v2.12.0.zip از دکمهٔ «دانلود سورس کامل (ZIP)» سایت آماده است (فایل‌های کامل — نه پچ)
- هیچ فیچری حذف نشد؛ WORK LOG دائمی طبق قانون کاربر ادامه دارد — این بخش هرگز پاک نشود

---
Task ID: 17 (v2.13.0)
Agent: main-orchestrator (Z.ai Code)
Task: رفع خطای 403 سرویس‌های هوش مصنوعی در ایران — گزارش کاربر: «فیلم‌نامهٔ صحنه‌ها نوشته می‌شود… — خطای 403 از سرویس هوش مصنوعی — Forbidden» برای گروک و «خطای 403 … <!DOCTYPE html>…Error 403» برای جمینای (مرحلهٔ فیلم‌نامهٔ چاپخانهٔ ویدیو)

Work Log:
- ریشه‌یابی: درخواست‌های پایتون (urllib) به‌تنهایی از VPN مرورگر عبور نمی‌کنند؛ Groq و Gemini و OpenAI و Anthropic و xAI درخواست از IP ایران را با 403 رد می‌کنند (Gemini با صفحهٔ HTML گوگل). پیام قبلی («خطای 403 از سرویس هوش مصنوعی — Forbidden») هیچ راهنمایی نمی‌داد؛ ضمناً urllib در ویندوز برای مقصد https آدرس https:// به پروکسیِ HTTP لوکال می‌ساخت (باگ شناخته‌شده) و v2rayN/Nekoray جواب نمی‌داد
- ai_agent.py:
  * resolve_ai_proxy جدید — اولویت: ①فیلد «پروکسی فراخوانی سرویس‌ها» (تنظیمات ← هوش مصنوعی) ②متغیرهای محیط ③رجیستری ویندوز (System Proxy) با رفع باگ scheme؛ پروکسی socks با پیام فارسیِ «پورت HTTP بدهید» رد می‌شود
  * _llm_error_fa جدید — 403 (ساده/HTML گوگل/«User location is not supported»)، 401، 429، «API key not valid» همه فارسیِ راه‌حل‌دار با نام فیلد پروکسی و پیشنهاد Z.ai
  * _http_json: پارامتر proxies + اوپنر پروکسی‌دار؛ URLError حالا می‌گوید «از راه پروکسی وصل نشد» یا «مستقیم»
  * llm_chat: resolve_ai_proxy روی همهٔ سرویس‌ها اعمال می‌شود (چت، فیلم‌نامه، پاسخ دایرکت، تست)
  * سرویس جدید: xAI Grok (گروک) — base=api.x.ai/v1، مدل‌های grok-4/grok-3/grok-3-mini، key_field=grok؛ Z.ai همچنان اولِ لیست
  * پرامپت چت: «۷ پلتفرم» → «۸ پلتفرم» (واتساپ)
- ai_media.py: _proxy_map (از ai_agent) + پارامتر proxies در _http_json/_download_bytes/_download_bytes_retry/_pollinations_image/generate_image (ساخت عکس Z.ai/OpenAI + Pollinations + دانلود عکس‌ها)؛ _http_error_fa پیام 403 فارسی؛ _llm_scenes: خطای دائمی 403/401 دیگر ۳ بار retry نمی‌شود و پیامش «نوشتن فیلم‌نامه ممکن نشد — …» می‌شود (خطای اتصال 10054 همچنان retry می‌شود)
- panel_server.py: DEFAULT_SETTINGS.ai.proxy + کلید grok در api_keys؛ ادغام api_keys زیر-کلیدی شد تا فیلد سرویس تازه در تنظیمات قدیمی گم نشود؛ docstring ۲.۱۳.۰
- static/index.html: فیلد «🛡 پروکسی فراخوانی سرویس‌های AI» با «؟» کامل (نکته‌های v2rayN/Nekoray/Clash و SOCKS) + دکمهٔ «🔌 تست اتصال» (اول ذخیره می‌کند، بعد /api/ai/test سرویس انتخابی را با پیام فارسی وصل/غیروصل می‌گوید) + فیلد کلید xAI Grok با «؟» و لینک console.x.ai + به‌روزرسانی یادداشت‌های Groq/Gemini (خطای 403 → فیلد پروکسی) + راهنمای جدید «خطای 403 و پروکسی سرویس‌ها» + ردیف اول عیب‌یابی چاپخانه + whatsnew ۲.۱۳.۰ + فوتر ۲.۱۳.۰
- launcher.py: APP_VERSION=2.13.0 + docstring (۲.۱۳.۰ و ۲.۱۲.۰ گمشده) + هدر GUI؛ README.md: بولت پروکسی 403 + جدول سرویس‌ها (xAI Grok) + نقل‌قول راهنمای پروکسی AI + ردیف عیب‌یابی 403
- سایت Next.js → v2.13.0: data.ts/header/footer/download-section (چیپ)/download route → ParsAgent-v2.13.0.zip/features.tsx کارت «پروکسی سرویس‌های AI + رفع خطای 403 (۲.۱۳.۰)»؛ public/panel.html بازسازی شد
- منبع مرجع kiwi بررسی شد: پوشهٔ file.kiwi/f59499d6 واقعاً «Empty Folder» است (با مرورگر headless و کلید لینک باز و بررسی شد) — لینک مرجع منقضی شده؛ هیچ فیچری از پروژه حذف نشد (فقط افزودن/رفع باگ)
- اعتبارسنجی در سندباکس:
  * py_compile هر ۵ فایل پایتون OK
  * tests/tmp/test_v213.py — ۳۲/۳۲ پاس: اولویت‌ها و نرمال‌سازی پروکسی (تنظیم/محیط/خالی/socks)، پیام‌های فارسی 403 سه‌گانه (Forbidden ساده/HTML گوگل/Gemini location) و 401/429، کاتالوگ grok (Z.ai اول ماند)، llm_chat از راه پروکسی HTTP محلیِ واقعی (پاسخ OK + URL مطلق به پروکسی رفت + 403 ساده و HTML فارسی بلند شد + لوکال مستقیم بدون پروکسی)، _llm_scenes: 403 فقط ۱ بار صدا زده شد (نه ۳ بار) و 10054 هنوز retry می‌شود، DEFAULT_SETTINGS و ادغام api_keys قدیمی (grok اضافه ماند)
  * سرور پنل واقعی بوت: /api/ready OK؛ /api/ai/catalog با grok؛ agent-browser: whatsnew و فوتر ۲.۱۳.۰، فیلد ai-proxy و دکمهٔ تست و کلید grok حاضر؛ «ذخیره همهٔ تنظیمات» → settings.json با ai.proxy نوشته شد؛ دکمهٔ تست اتصال → «❌ کلید API «Z.ai (GLM)» در تنظیمات وارد نشده…» (جریان کامل ذخیره→تست فارسی)؛ صفر خطای صفحه
  * پنل: دسکتاپ 1440 و موبایل 390 بدون سرریز (390=390)، فیلد پروکسی مرئی (w=208)
  * سایت: v2.13.0 در هدر/فوتر/چیپ، کارت جدید حاضر، موبایل 390 بدون سرریز
  * GET /api/download → 200 با filename=ParsAgent-v2.13.0.zip؛ محتوای ZIP (۱۱ entry) تأیید شد: APP_VERSION=2.13.0، resolve_ai_proxy، grok، ai-proxy، ai-test-conn، data-aikey=grok، whatsnew/فوتر ۲.۱۳.۰، بدون __pycache__ و پوشه‌های ران‌تایم
  * bun run lint: صفر خطا

Stage Summary:
- ParsAgent v2.13.0 آماده: خطای 403 (گروک/Groq، جمینای، OpenAI…) در ایران ریشه‌یابی و رفع شد — فیلد «پروکسی فراخوانی سرویس‌ها» + حالت خودکار (System Proxy ویندوز با رفع باگ https) + دکمهٔ «تست اتصال» + پیام فارسی راه‌حل‌دار + سرویس جدید xAI Grok؛ Z.ai از ایران مستقیم کار می‌کند
- ParsAgent-v2.13.0.zip از دکمهٔ «دانلود سورس کامل (ZIP)» سایت قابل دانلود است (فایل‌های کامل — نه پچ)
- WORK LOG دائمی — این بخش هرگز پاک نشود

---
## نسخهٔ 2.14.0 — 2026-10-13 (گزارش باگ کاربر: 404 مدل + خرابی ضبط/پخش ماکرو)

**گزارش کاربر:** «❌ خطای 404 از سرویس هوش مصنوعی — The model `llama-3.3-70b-versatile` does not exist or you do not have access to it. بقیشون هم خطا میدن» + «ضبط و پخش ماکرو هم درست کار نمیکنه. موقع خاموش کردن ماکرو رو هم ضبط نکنه. کلا ماکرو فقط در پنجره نرم افزار انتخاب شده به عنوان مرورگر برای مرور شبکه های اجتماعی در صفحه تنظیمات فقط کار کنه و دیگه روی پنجره های دیگه چیزی ضبط نکنه»

### ۱) ریشه‌یابی خطای 404 (تحقیق زنده با وب)
- مستند رسمی Groq (console.groq.com/docs/deprecations) خوانده شد: **۱۶ اوت ۲۰۲۶ — Groq مدل‌های `llama-3.3-70b-versatile` و `llama-3.1-8b-instant` را برای کلیدهای معمولی بست (فقط Enterprise)**
- جایگزین‌های رسمی اعلام‌شده: `openai/gpt-oss-20b` (به‌جای 8b-instant) و `qwen/qwen3.6-27b` (به‌جای 70b-versatile)؛ خود qwen3.6-27b هم در ۱۴ سپتامبر ۲۰۲۶ با `qwen/qwen3.8-27b` جایگزین شد
- جدول مدل‌های production فعلی Groq: gpt-oss-120b، gpt-oss-20b (+ Enterprise: llama-3.x، minimax-m2.7)
- نتیجه: کلید کاربر سالم بود؛ مدل از سمت خود سرویس حذف شده بود — «بقیشون هم خطا میدن» چون بقیهٔ مدل‌های کاتالوگ ایستا هم همین‌طور مرده بودند

### ۲) ریشه‌یابی خرابی ماکرو (تست واقعی با Playwright در سندباکس)
- **باگ اصلی:** جعبه‌های چت اینستاگرام/واتساپ/تلگرام `contentEditable` هستند و رویداد `change` ندارند → متنِ تایپ‌شده **هرگز ضبط نمی‌شد** → پخش ماکرو دکمهٔ «ارسال» را با متن خالی می‌زد
- رویدادها از همهٔ صفحاتِ مرورگر ضبط می‌شدند (از جمله پنل ParsAgent اگر داخل همان مرورگر باز بود → کلیک روی دکمهٔ «توقف و ذخیره» هم داخل ماکرو می‌نشست — دقیقاً گزارش کاربر)
- پخش فقط روی صفحهٔ اصلی و فقط قاب اصلی: رخدادهای ضبط‌شده در تب/فریم دیگر بی‌صدا رد می‌شدند («0 از 5 رخداد اجرا شد» بدون هیچ توضیحی)
- رفتار `context.expose_binding` روی صفحات موجود با تست تأیید شد که سالم است (ریشهٔ مشکل نبود)

### ۳) تغییرهای اعمال‌شده

**ai_agent.py:**
- کاتالوگ Groq با مدل‌های زندهٔ رسمی: `openai/gpt-oss-120b` (پیشنهادی)، `openai/gpt-oss-20b` (سریع)، `qwen/qwen3.8-27b` (پیش‌نمایش)
- `DEAD_MODELS` — جدول «مدل مرده ← جایگزین رسمی» برای groq (۱۲ مدل: llama-3.3-70b-versatile، llama-3.1-8b-instant، qwen3-32b، qwen3.6-27b، deepseek-r1-distill-llama-70b، gemma2-9b-it، kimi-k2-*، llama3-*-8192، mixtral) و gemini (نسل 1.5)
- `resolve_model()` در `llm_chat` — مدل حذف‌شده بی‌صدا با جایگزین رسمی عوض می‌شود (هیچ فراخوانی روی مدل مرده گیر نمی‌کند)
- `fetch_models()` + `_http_get_json()` — دریافت فهرست مدل‌های «همین لحظه» از خود سرویس (GET {base}/models با کلید کاربر؛ سازگار با OpenAI/Anthropic/Gemini/سفارشی) + فیلتر مدل‌های غیرگفتگو (whisper/embed/tts/guard/...) + حفظ ترتیب کاتالوگ
- `_llm_error_fa` — پیام فارسی راه‌حل‌دار برای 404 مدل («دکمهٔ 🔄 مدل‌های زنده» + توضیح حذف مدل‌ها) و 404 مسیر (سرویس سفارشی)
- `catalog()` — پرچم `dead_current`/`dead_replacement` برای هشدار پنل

**ai_media.py:** `_llm_scenes` — خطای 404 (مثل 403/401) دیگر ۳ بار تلاش مجددِ بی‌فایده نمی‌کند؛ همان لحظه با پیام فارسی اعلام می‌شود

**panel_server.py:**
- `PLATFORM_DOMAINS` — دامنه‌های مجازِ ضبط برای هر ۸ پلتفرم
- `RECORDER_JS` نسخهٔ ۲: ضبط متن contentEditable (رویداد focusout) + کلید Enter + مقدار نهایی input ها (focusout) + هر رویداد `origin` دارد + خودش روی localhost (پنل) اصلاً لیسنر نمی‌گذارد + **dedupe با WeakMap** (Enter بعد از تایپ و blur بعدش، متن را دوبار ضبط نمی‌کند تا پخش، پیام را دوبار نفرستد)
- `_rec_handler` + `_rec_origin_ok` — فیلتر سمت سرور: رویداد پنل (localhost) و سایت‌های خارج از دامنهٔ پلتفرم نادیده گرفته و شمرده می‌شوند (`rec_dropped_panel`/`rec_dropped_foreign`)
- `_macro_replay` — پخش مقاوم: پیدا کردن تبِ درست از روی `origin` هر رخداد + جستجوی عنصر در همهٔ فریم‌ها (iframe) + شمارش و **اعلام دلیل** رخدادهای ناموفق (قبلاً بی‌صدا رد می‌شد)
- `macro_stop` — دابل‌چک نهایی: رویدادهای خارج از دامنه قبل از ذخیره حذف می‌شوند؛ تعدادش در پیام اعلام می‌شود
- اندپوینت جدید `GET /api/ai/models?provider=...` — فهرست مدل‌های زنده
- مهاجرت startup: مدلِ ذخیره‌شدهٔ مرده خودکار با جایگزین رسمی **عوض و ذخیره** می‌شود (لاگ فارسی)
- `/api/state` — شمارنده‌های رویدادهای نادیده‌گرفته‌شده

**static/index.html:** دکمهٔ «🔄 مدل‌های زنده» کنار فیلد مدل (هر دو فرم: تب هوش مصنوعی + تنظیمات) با ذخیرهٔ خودکار تنظیمات قبل از دریافت؛ جایگزینی خودکار مدل مرده در فرم با toast؛ چیپ «N رویداد خارج از پلتفرم نادیده گرفته شد»؛ متن جدید تب ماکرو و راهنما؛ ردیف عیب‌یابی 404؛ کادر «چه چیز تازه است؟» ۲.۱۴.۰؛ فوتر ۲.۱۴.۰

**launcher.py:** APP_VERSION=2.14.0 + سربند + هدر GUI
**README.md:** بولت‌های ۲.۱۴.۰ + ردیف 404 در عیب‌یابی + ردیف Groq و ماکرو به‌روز

**سایت Next.js:** header/footer/download-section/data.ts → v2.14.0؛ کارت فیچر «مدل‌های زنده + تعمیر ماکرو (۲.۱۴.۰)»؛ مسیر دانلود → ParsAgent-v2.14.0.zip؛ public/panel.html بازسازی (اسکریپت زنده حذف + بنر پیش‌نمایش)

### ۴) اعتبارسنجی
- تست منطق (۲۶/۲۶ پاس): کاتالوگ Groq جدید، resolve_model (مدل مرده/زنده/خالی/زنجیره‌ای)، پیام فارسی 404 (سه حالت)، fetch_models با سرور محلی (۳ مدل گفتگو، فیلتر whisper/tts/embed)، خطای بدون کلید، فیلتر دامنه ۹ حالت، RECORDER_JS، catalog/dead_current
- **تست مرورگر واقعی E2E (Playwright + صفحهٔ شبیه‌چت با contentEditable):** ضبط (متن چت + Enter + کلیک‌ها + input با blur + dedupe تک‌مصدایی) و **پخش کامل روی همان صفحه بعد از پاک‌سازی: 7/7 رخداد، متن «سلام این پیام تست ماکرو است» دقیقاً ارسال شد و input دقیقاً پر شد** ✅؛ رویداد تب غیرمجاز (someother.com) حذف شد
- سرور پنل واقعی بوت: مهاجرت خودکار groq/llama-3.3-70b-versatile → openai/gpt-oss-120b در settings.json اعمال شد؛ /api/ai/catalog با مدل‌های جدید؛ /api/ai/models بدون کلید → پیام فارسی؛ /api/ai/models با کلید جعلی روی api.groq.com واقعی → پیام فارسی 403 ایران (زنجیرهٔ خطا کامل)؛ /api/state با شمارنده‌های جدید؛ ۸ پلتفرم دست‌نخورده
- سایت با agent-browser: v2.14.0 در header/footer/چیپ/کارت، دموی زنده اجرا (لاگ: pars-agent v2.14.0 — task: instagram.post_photo)، صفر خطای کنسول، موبایل 390px بدون سرریز (سایت + پنل)
- ZIP ParsAgent-v2.14.0.zip: ۱۰ فایل کامل + static/index.html؛ ۱۳ چک محتوایی پاس؛ پوشه‌های اجرایی (config/media/macros/profiles/logs/offline_bundle/__pycache__) داخل بسته نیستند
- bun run lint صفر خطا؛ py_compile همهٔ فایل‌ها OK

### نتیجهٔ نسخه
- خطای 404 مدل‌ها سه‌لایه رفع شد (کاتالوگ زنده + جایگزینی خودکار + دکمهٔ مدل‌های زنده)؛ «بقیشون هم خطا میدن» هم حل شد چون کل کاتالوگ Groq مرده بود
- ماکرو هر سه درخواست کاربر را گرفت: ضبط/پخش واقعاً کار می‌کند (تایپ در چت‌ها + پخش مقاوم)، دکمهٔ خاموش کردن ضبط نمی‌شود (فیلتر localhost دو لایه)، ضبط فقط در پنجرهٔ مرورگرِ همان شبکهٔ اجتماعی است (فیلتر دامنه در مرورگر + سرور)
- ParsAgent-v2.14.0.zip از دکمهٔ «دانلود سورس کامل (ZIP)» سایت آماده است (فایل‌های کامل — نه پچ)

---

## نسخهٔ ۲.۱۵.۰ — کنترل کامل پخش ماکرو (۴ درخواست کاربر)
تاریخ: ۲۰۲۶-۱۰-۱۳ (Asia/Tehran)

گزارش کاربر (عیناً):
1) «برای استاپ پخش ماکرو هم دکمه بذار»
2) «فقط اینستاگرام در پخش ماکرو قابل انتخابه؛ بقیه پلتفورمها رو کلیک میکنم دوباره برمیگرده به اولین گزینه دراپ داون. اصلا در این قسمت پخش احتیاجی به دراپ داون نیست؛ از قسمت بالا دراپ داون ضبط داریم، همونها رو انتخاب میکنیم و پایین مینویسه این ضبط مربوط به چه پلتفرمیه»
3) «وقتی ماکرو شروع میشه هر پلتفرمی که انتخاب شده بره به صفحه اصلی اون پلتفرم در مرورگر؛ الان صفحه خالی میاره و سایت باز نمیشه»
4) «وقتی پخش تموم میشه یا دکمه توقف رو میزنم پلتفرم و پنجره مرورگر هم بسته بشه؛ الان اگر دستی هم مرورگر رو ببندم باز در قسمت پلتفرم چون باز خورده ماکرو دوباره پخش نمیشه و خطا میده»

### ۱) ریشه‌یابی
- باگ دراپ‌داون: پُل ۳ ثانیه‌ای state هر بار کل لیست ماکروها را بازمی‌ساخت → `<select>` تازه با گزینهٔ اول (اینستاگرام) جایگزین می‌شد و انتخاب کاربر می‌پرید؛ درخواست صحیح کاربر: پلتفرم باید از خودِ ضبط بیاید نه انتخابِ جدا
- صفحهٔ خالی هنگام پخش: `_macro_replay` فقط `ensure()` می‌زد؛ context ماندگار با about:blank/تب بسته بالا می‌آمد و هیچ رخدادی پیدا نمی‌شد
- خطای بعد از بستن دستی: `BotSession.ensure()` فقط `if self.context:` را چک می‌کرد؛ بعد از بستنِ دستیِ پنجره، context کهنه None نبود → صفحهٔ بسته برگردانده می‌شد → «Target page, context or browser has been closed» تا ری‌استارت
- بدون دکمهٔ توقف پخش: هیچ مکانیزمی برای قطع حلقهٔ پخش وجود نداشت

### ۲) تغییرهای کد
- `panel_server.py`:
  - `MACRO_PLAY` (task/stop/platform/name) + `_wsleep` (مکث چانک ۰.۲ث قابل‌قطع) + `_macro_path`/`_macro_load` (فرمت ۲.۱۵.۰ dict + فرمت قدیمی لیست) + `_pick_replay_page` (اولین تب زنده روی دامنهٔ پلتفرم)
  - `_macro_replay` بازنویسی: رزولوشن پلتفرم از فایل ماکرو (برنده بر پارامتر) + goto صفحهٔ اصلی پلتفرم (domcontentloaded، ۴۵ث، هشدار فارسی اگر ناتمام) + bring_to_front + چک پرچم توقف بین رخدادها و داخل مکث‌ها + `sess.close()` در پایان/توقف (بسته شدن پنجرهٔ مرورگر) + پیام «پخش متوقف شد — N از M» + گارد پخش هم‌زمان
  - `BotSession.ensure()`: تشخیص سلامت واقعی (pages + is_closed)؛ مرورگرِ دستی‌بسته خودکار دوباره باز می‌شود (رفع خطای Target closed تا ری‌استارت)
  - `macro_stop`: ذخیرهٔ `{"platform", "saved_at", "events"}`؛ `macro_names`/`/api/macro/list` با platform برای هر دو فرمت
  - `macro_run`: پلتفرم فقط fallback برای ماکروهای قدیمی؛ endpoint جدید `POST /api/macro/stop-run` (پیام فارسی وقتی پخشی نیست)؛ `/api/state` → `macro.playing`
- `static/index.html`: دکمهٔ «⏹ توقف پخش» (فقط حین پخش) + چیپ «▶ در حال پخش» + حذف دراپ‌داون پخش (چیپ پلتفرم از لحظهٔ ضبط؛ دراپ‌داون فقط برای ماکروهای قدیمی) + renderMacros با امضای تغییر (رفع کامل باگ ریست) + غیرفعال‌شدن «اجرا» حین پخش + `fillMacroSelect/syncSchMacroPlatform` (زمان‌بندی هم پلتفرم را از ماکرو می‌گیرد) + whatsnew/راهنما/FAQ/فوتر ۲.۱۵.۰
- `launcher.py` 2.15.0 + `README.md` (بولت/جدول/عیب‌یابی) + سایت Next.js → v2.15.0 + کارت فیچر Square + `public/panel.html` بازسازی از سورس تازه

### ۳) اعتبارسنجی
- تست منطقی ۱۵/۱۵ پاس (فرمت ذخیره، macro_names هر دو فرمت، _macro_load، stop-run بدون پخش، _wsleep قابل‌قطع، 404، state.playing)
- **E2E مرورگر واقعی Chromium هدلس ۱۴/۱۴ پاس:** پخش کامل (goto ماک + ۵/۵ رخداد روی سرور ماک تأیید شد + بسته شدن خودکار مرورگر)؛ پارامتر غلط (instagram) → روی پلتفرم ذخیره‌شده (telegram) اجرا شد؛ state.playing حین پخش؛ stop-run وسط کار → پیام توقف + بستن مرورگر؛ پخش دوباره بعد از توقف سالم؛ ensure بعد از بستنِ دستیِ context دوباره باز کرد و صفحه سالم بود؛ پخش هم‌زمان دوم → پیام فارسی
- پنل واقعی بوت + agent-browser: ردیف ماکرو با چیپ «📸 اینستاگرام» و ماکروی قدیمی با دراپ‌داون؛ مقدار دراپ‌داون بعد از ۹ ثانیه (۳ پُل) ثابت ماند؛ دکمهٔ توقف/چیپ/غیرفعال‌شدن اجرا حین پخش (شبیه‌سازی state) + کلیک توقف → endpoint؛ زمان‌بندی → پلتفرم خودکار instagram؛ صفر خطای صفحه/کنسول؛ موبایل 390px بدون سرریز؛ VLM: چیدمان تمیز
- سایت: v2.15.0 (هدر/چیپ/کارت)، ZIP ParsAgent-v2.15.0.zip با ۱۵ چک محتوایی پاس (بدون config/macros/profiles/__pycache__)؛ lint صفر؛ py_compile OK

### نتیجهٔ نسخه
- هر ۴ درخواست کاربر انجام و با تست واقعی مرورگر اثبات شد؛ ParsAgent-v2.15.0.zip از دکمهٔ «دانلود سورس کامل (ZIP)» سایت آماده است (فایل‌های کامل — نه پچ)
