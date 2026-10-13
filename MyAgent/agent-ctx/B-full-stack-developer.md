# Task B — full-stack-developer

**Task:** اتصال سایت ParsAgent به بستهٔ نهایی `parsagent/` (نسخهٔ ۲.۰.۰) — به‌روزرسانی API دانلود/مرور سورس، ارتقای نسخه در UI و بازنویتی راهنمای نصب.

> کاربران بعدی: تاریخچهٔ کامل پروژه در `/home/z/my-project/worklog.md` است (Task 0–8 + آخرین رکورد). نسخهٔ نهایی پایتونی پروژه در `/home/z/my-project/parsagent/` است.

## فایل‌های تغییریافته (۷ فایل — هیچ چیز دیگری تغییر نکرد)

| فایل | تغییر |
|---|---|
| `src/app/api/download/route.ts` | AGENT_ROOT → `parsagent`؛ فیلتر ZIP: حذف `__pycache__` + پوشه‌های ران‌تایم `config/ media/ macros/ profiles/ logs/`؛ نام فایل → `ParsAgent-v2.0.zip`؛ ریشهٔ ZIP همان `pars-agent` |
| `src/app/api/agent/files/route.ts` | AGENT_ROOT → `parsagent`؛ SKIP_DIRS += `media, macros, profiles, config`؛ `.html` → `markup`؛ ORDER جدید: panel_server.py → README.md → requirements.txt → launcher.py → ParsAgent.bat → static/ |
| `src/components/agent/code-viewer.tsx` | فایل پیش‌فرض: `panel_server.py` (قبلاً main.py) |
| `src/components/agent/download-section.tsx` | چیپ «نسخهٔ ۲.۰.۰»؛ متن کارت: «پکیج کامل و آمادهٔ اجرا: سرور پنل محلی + رابط فارسی + لانچر گرافیکی + راهنمای کامل — استخراج کن، اجرا کن.» |
| `src/components/agent/header.tsx` + `footer.tsx` | `PARSAGENT · v2.0.0` |
| `src/components/agent/data.ts` | `AGENT_VERSION = "v2.0.0"` |
| `src/components/agent/install-guide.tsx` | گام ۴ بدون جملهٔ CLI؛ آکاردئون‌های جدید: `run-direct` (Terminal)، `mirror` (Package)، `data` (Keyboard)؛ حذف import ChevronDown |

## نکتهٔ فنی مهم (برای ایجنت‌های بعدی)
فیلتر `zip.addLocalFolder(root, "pars-agent", filter)` در **adm-zip 0.6.1** مسیر «کامل داخل ZIP» را با پیشوند `pars-agent/` می‌گیرد (پوشه‌ها با اسلش انتهایی: `pars-agent/config/`). پس چک `startsWith("config/")` مستقیم جواب نمی‌دهد — باید پیشوند ریشه حذف و سگمنت اول بررسی شود:
```ts
const p = entryPath.split("\\").join("/");
const rel = p.startsWith(`${ZIP_ROOT}/`) ? p.slice(ZIP_ROOT.length + 1) : p;
const root = rel.replace(/\/+$/, "").split("/")[0];
if (root && RUNTIME_DIRS.has(root)) return false;
```

## اعتبارسنجی (همه موفق)
- `bun run lint` → exit 0، صفر خطا/هشدار
- `GET /api/download` → 200، `filename="ParsAgent-v2.0.zip"`، ۴۴,۵۱۸ بایت، ۷ entry: `pars-agent/{panel_server.py, README.md, requirements.txt, launcher.py, ParsAgent.bat, static/, static/index.html}` — **صفر** entry از config/media/macros/profiles/__pycache__
- `GET /api/agent/files` → ۶ فایل / ۳۰۸۶ خط / ۱۵۸KB — ترتیب طبق ORDER جدید؛ `static/index.html` با language=markup
- agent-browser: `/` بدون خطای کنسول/هیدریشن؛ v2.0.0 در هدر/فوتر (صفر v1.0.0)؛ code-viewer پیش‌فرض `panel_server.py`؛ `/panel.html` بنر «پیش‌نمایش استاتیک» + ۸ تب + ۵ لاگ تدریجی؛ موبایل 390px بدون سرریز (هر دو صفحه)؛ فوتر چسبان (footerBottom=viewportH)؛ هر سه آکاردئون جدید محتوای درست دارند
- dev.log → بدون خطای جدید

## محدودهٔ ممنوعه (دست‌نخورده)
`parsagent/` ، `public/panel.html` ، `demo.tsx`/`terminal.tsx`/`hero.tsx`/`panel/*` ، پالت emerald (بدون آبی/نیلی) ، RTL + Vazirmatn.
