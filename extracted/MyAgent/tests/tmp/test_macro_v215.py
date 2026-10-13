# -*- coding: utf-8 -*-
"""تست منطقی v2.15.0 — بدون مرورگر: فرمت ذخیرهٔ ماکرو (platform)،
macro_names با هر دو فرمت، _macro_load، گارد پخش هم‌زمان، پیام فارسی."""
import asyncio, json, sys, os, tempfile, shutil
from pathlib import Path

sys.path.insert(0, "/home/z/my-project/parsagent")
os.environ["PANEL_PORT"] = "8899"
import panel_server as ps

PASS = []
def ok(name, cond, extra=""):
    PASS.append(bool(cond))
    print(("✅" if cond else "❌"), name, extra)

async def main():
    # ---- ۱) فرمت ذخیرهٔ جدید: macro_stop → dict با platform
    # شبیه‌سازی: ضبط فعال با رخداد ساختگی، سپس ذخیره
    sess = ps.SESSIONS["telegram"]
    sess.recording = True
    sess.rec_events = [
        {"t": "click", "sel": "button.send", "origin": "https://web.telegram.org/"},
        {"t": "input", "sel": "div.chat", "v": "سلام", "origin": "https://web.telegram.org/"},
    ]
    r = await ps.macro_stop({"platform": "telegram", "name": "تست-۲۱۵"})
    ok("macro_stop ok", r.get("ok") is True, str(r))
    f = ps.MACROS_DIR / "تست-۲۱۵.json"
    raw = json.loads(f.read_text(encoding="utf-8"))
    ok("فرمت جدید dict", isinstance(raw, dict) and raw.get("platform") == "telegram" and isinstance(raw.get("events"), list), str(raw.keys()))
    ok("saved_at ثبت شده", bool(raw.get("saved_at")))

    # ---- ۲) macro_names با هر دو فرمت
    legacy = ps.MACROS_DIR / "قدیمی-بدون-پلتفرم.json"
    legacy.write_text(json.dumps([{"t": "click", "sel": "a", "origin": "https://x.com/"}], ensure_ascii=False), encoding="utf-8")
    names = {m["name"]: m for m in ps.macro_names()}
    ok("پلتفرم ماکروی جدید", names.get("تست-۲۱۵", {}).get("platform") == "telegram")
    ok("ماکروی قدیمی platform خالی + شمارش درست", names.get("قدیمی-بدون-پلتفرم", {}).get("platform") == "" and names.get("قدیمی-بدون-پلتفرم", {}).get("events") == 1)

    # ---- ۳) _macro_load هر دو فرمت
    ok("_macro_load جدید", ps._macro_load(f)["platform"] == "telegram")
    ok("_macro_load قدیمی", ps._macro_load(legacy)["platform"] == "" and len(ps._macro_load(legacy)["events"]) == 1)
    ok("_macro_load فایل گمشده", ps._macro_load(ps.MACROS_DIR / "نا موجود.json") == {"platform": "", "events": []})

    # ---- ۴) رزولوشن پلتفرم در _macro_replay — بدون اجرای واقعی:
    # فایل با platform=whatsapp ولی pid غلط → باید به whatsapp برود؛ برای تستِ فقط-پارامتر
    wf = ps.MACROS_DIR / "تست-واتساپ.json"
    save = json.dumps({"platform": "whatsapp", "events": [{"t": "click", "sel": "b", "origin": "https://web.whatsapp.com/"}]}, ensure_ascii=False)
    wf.write_text(save, encoding="utf-8")
    # دراگرد: اجرا روی پلتفرم غلط؟ نه — pid از فایل برنده است ولی چون مرورگر واقعی لازم است،
    # فقط چک می‌کنیم پیامِ «هم اکنون پخشی نیست» برای stop-run بدون اجرا درست باشد:

    # ---- ۵) stop-run بدون پخش → پیام فارسی
    r = await ps.macro_stop_run()
    ok("stop-run بدون پخش", r["ok"] is False and "پخشی در حال اجرا نیست" in r["message"], r["message"])

    # ---- ۶) _wsleep: توقف سریع با پرچم
    ps.MACRO_PLAY["stop"] = True
    import time as _t
    t0 = _t.monotonic()
    stopped = await ps._wsleep(5.0)
    ok("_wsleep قابل‌قطع (<1s)", stopped is True and _t.monotonic() - t0 < 1.0, f"{_t.monotonic()-t0:.2f}s")
    ps.MACRO_PLAY["stop"] = False
    t0 = _t.monotonic()
    stopped = await ps._wsleep(0.15)
    ok("_wsleep خواب کامل", stopped is False and _t.monotonic() - t0 >= 0.14)

    # ---- ۷) _pick_replay_page بدون مرورگر → None (نه کرش)
    ok("_pick_replay_page بدون context", ps._pick_replay_page(ps.SESSIONS["bale"], "bale") is None)

    # ---- ۸) macro_run با ماکروی ناموجود → 404
    from fastapi import HTTPException
    try:
        await ps.macro_run({"platform": "instagram", "name": "هیچ"})
        ok("macro_run 404", False)
    except HTTPException as e:
        ok("macro_run 404", e.status_code == 404)

    # ---- ۹) state شامل playing
    st = await ps.state()
    ok("state.macro.playing=None", st["macro"].get("playing") is None)
    ok("state.macro.saved با platform", any(m.get("platform") == "telegram" for m in st["macro"]["saved"]))

    # پاک‌سازی تست
    for p_ in (f, legacy, wf):
        p_.unlink(missing_ok=True)
    print("\n" + ("ALL PASS ✅" if all(PASS) else "SOME FAILED ❌"))
    sys.exit(0 if all(PASS) else 1)

asyncio.run(main())
