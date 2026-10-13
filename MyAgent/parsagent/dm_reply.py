# -*- coding: utf-8 -*-
"""
ParsAgent — پاسخ‌گوی خودکار دایرکت و پیام‌ها (هر پلتفرم، به‌صورت طبیعی)
=====================================================================

اینجنتِ پاسخ‌گویی دایرکت:

  • هر پلتفرمی که «پاسخ‌گویی» آن روشن باشد، باز می‌شود و گفتگوهای خوانده‌نشده
    را پیدا می‌کند (اینستاگرام، توییتر، تلگرام، فیسبوک، لینکدین، بله، روبیکا)
  • چند پیام آخر هر گفتگو را می‌خواند و با «شخصیت و لحن کسب‌وکار شما» جواب
    کاملاً طبیعی می‌نویسد — با همان سرویس AI که انتخاب کرده‌اید (Z.ai و …)
  • مثل انسان تایپ می‌کند (حرف‌به‌حرف با مکث) و ارسال می‌کند
  • سقف روزانه، حداقل فاصله بین دو جواب، ساعت‌های فعال و «حالت پیش‌نمایش»
    (بدون ارسال — اول جواب‌ها را ببینید) دارد؛ آمار همیشه در پنل دیده می‌شود

سلکتورها بهترین‌تلاشِ امروزِ پلتفرم‌هاست و از تنظیمات
(تنظیمات ← هوش مصنوعی ← پاسخ‌گوی دایرکت) قابل بازنویسی است؛ چون رابط
پیام‌رسان‌ها گاهی عوض می‌شود، پیش‌نمایش را اول اجرا کنید تا مطمئن شوید.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import random
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

DEFAULT_DM_CFG: Dict[str, Any] = {
    "enabled": False,          # کلاینت باید صریح روشن کند
    "dry_run": True,           # پیش‌فرض: فقط پیش‌نمایش، بدون ارسال
    "daily_cap": 40,           # سقف جواب در شبانه‌روز (همهٔ پلتفرم‌ها)
    "max_per_round": 4,        # حداکثر گفتگویی که در هر دور جواب می‌گیرد
    "round_minutes": 20,       # هر چند دقیقه یک‌بار دورِ بازرسی
    "min_reply_gap_min": 12,   # حداقل فاصلهٔ بین دو جواب (طبیعی‌بودن)
    "active_hours": [9, 23],  # فقط بین این ساعت‌ها جواب می‌دهد
    "persona": "",             # معرفی کسب‌وکار/شخصیت شما
    "tone": "صمیمی و محترمانه — فارسی روان مثل چت واقعی",
    "faq": [],                 # [{"q": "...", "a": "..."}]
    "platforms": {},           # {instagram: true, telegram: true, ...}
    "selectors": {},           # بازنویسی دستی سلکتورها
}

# بهترین‌تلاشِ امروز — همه از تنظیمات قابل بازنویسی‌اند
DM_PAGES: Dict[str, Dict[str, Any]] = {
    "instagram": {
        "url": "https://www.instagram.com/direct/inbox/",
        "threads": "div[role='listitem'] a[href*='/direct/t/'], a[href^='/direct/t/'], div[aria-label='Chats'] a",
        "input": "textarea[placeholder], div[role='textbox'][contenteditable='true']",
    },
    "twitter": {
        "url": "https://x.com/messages",
        "threads": "a[data-testid='DmActivityItem'], div[data-testid='DmActivityItem'] a, a[href^='/messages/']",
        "input": "div[data-testid='dmComposerTextInput'] div[contenteditable='true'], div[role='textbox'][contenteditable='true'], textarea",
    },
    "telegram": {
        "url": "https://web.telegram.org",
        "threads": "a.chatlist-chat, .chatlist-chat, ul[class*='chat'] a, div[class*='ListItem'] a",
        "input": ".input-message-input, div[contenteditable='true'], textarea",
    },
    "facebook": {
        "url": "https://www.facebook.com/messages/t/",
        "threads": "div[role='navigation'] a[href*='/messages/t/'], a[href^='/messages/t/'], div[aria-label='Chats'] a",
        "input": "div[role='textbox'][contenteditable='true'], textarea",
    },
    "linkedin": {
        "url": "https://www.linkedin.com/messaging/",
        "threads": "div[class*='msg-entity'] a, a[href^='/messaging/'], li a[class*='message']",
        "input": "div[role='textbox'][contenteditable='true'], textarea",
    },
    "bale": {
        "url": "https://web.bale.ir/",
        "threads": "div[class*='chat'] a, a[class*='chat'], li[class*='chat'], div[class*='dialog']",
        "input": "div[contenteditable='true'], textarea, .input-message-input",
    },
    "rubika": {
        "url": "https://web.rubika.ir/",
        "threads": "div[class*='chat'] a, a[class*='chat'], li[class*='chat'], div[class*='dialog']",
        "input": "div[contenteditable='true'], textarea, .input-message-input",
    },
    # ۲.۱۱.۰ — واتساپ وب: فهرست چت‌ها + کادر پیام چتِ باز (footer)
    "whatsapp": {
        "url": "https://web.whatsapp.com/",
        "threads": "#side div[role='listitem'], div[data-testid='cell-frame-container']",
        "input": "#main footer div[contenteditable='true'], footer div[data-testid='conversation-compose-box-input'], footer div[contenteditable='true']",
    },
}

# خواندن پیام‌های گفتگوی بازشده — اکسترکتور عمومی با تشخیص جهت (من/مقابل)
READ_JS = r"""() => {
  const sels = ['div[role="gridcell"]', '[data-testid="message"]',
                '[class*="message"]', '[class*="Message"]', '[class*="bubble"]',
                '.message', '.Message', 'div[role="row"]'];
  let nodes = [];
  for (const s of sels) {
    try { nodes = Array.from(document.querySelectorAll(s)); if (nodes.length >= 2) break; } catch (e) {}
  }
  const OWN = /(own|out|sent|from-me|is-out|outgoing|me-|self|right)/i;
  const out = [];
  for (const n of nodes.slice(-40)) {
    const txt = (n.innerText || '').trim();
    if (!txt || txt.length > 1200) continue;
    let el = n, mine = null;
    for (let i = 0; i < 6 && el; i++) {
      const cls = (el.className && el.className.baseVal !== undefined ? '' : String(el.className || ''));
      if (cls && OWN.test(cls)) { mine = true; break; }
      el = el.parentElement;
    }
    if (mine === null) mine = false;
    out.push({ text: txt.split('\n')[0].slice(0, 400), mine });
  }
  // حذف تکراری‌های تودرتو (چند سلکتور هم‌زمان خورده باشند)
  const seen = new Set(), dedup = [];
  for (const m of out) {
    const k = m.text + '|' + m.mine;
    if (!seen.has(k)) { seen.add(k); dedup.push(m); }
  }
  return dedup.slice(-12);
}"""


class DMAuto:
    """پاسخ‌گوی دایرکت — وابستگی‌ها از پنل تزریق می‌شود (بدون import چرخه‌ای)."""

    def __init__(self):
        self.ctx: Dict[str, Any] = {}
        self._task: Optional[asyncio.Task] = None
        self._replied_hashes: set = set()
        self._last_reply_at: Optional[datetime] = None

    # -------------------------------------------------- اتصال به پنل
    def configure(self, *, get_settings: Callable, save_settings: Callable,
                  get_session: Callable, llm_chat: Callable, llm_provider_model: Callable,
                  log: Callable, hdelay: Callable, htype: Callable, press_enter: Callable) -> None:
        self.ctx = {
            "get_settings": get_settings, "save_settings": save_settings,
            "get_session": get_session, "llm_chat": llm_chat,
            "llm_provider_model": llm_provider_model, "log": log,
            "hdelay": hdelay, "htype": htype, "press_enter": press_enter,
        }

    # -------------------------------------------------- تنظیمات
    def cfg(self) -> Dict[str, Any]:
        ai = self.ctx["get_settings"]().get("ai", {})
        out = json.loads(json.dumps(DEFAULT_DM_CFG))
        out.update(ai.get("dm_reply") or {})
        out["platforms"] = {**DEFAULT_DM_CFG["platforms"], **(out.get("platforms") or {})}
        out["faq"] = out.get("faq") or []
        return out

    def save_cfg(self, cfg: Dict[str, Any]) -> None:
        st = self.ctx["get_settings"]()
        st.setdefault("ai", {})["dm_reply"] = cfg
        self.ctx["save_settings"](st)

    def stats(self) -> Dict[str, Any]:
        return (self.ctx["get_settings"]().get("ai", {}).get("dm_stats")
                if self.ctx else None) or {"date": datetime.now().strftime("%Y-%m-%d"), "replies": {}}

    def _bump(self, platform: str) -> None:
        st = self.ctx["get_settings"]()
        s = st.setdefault("ai", {}).setdefault(
            "dm_stats", {"date": datetime.now().strftime("%Y-%m-%d"), "replies": {}})
        if s.get("date") != datetime.now().strftime("%Y-%m-%d"):
            s.update(date=datetime.now().strftime("%Y-%m-%d"), replies={})
        s["replies"][platform] = int(s["replies"].get(platform, 0)) + 1
        self.ctx["save_settings"](st)

    def running(self) -> bool:
        return bool(self._task and not self._task.done())

    # -------------------------------------------------- چرخهٔ پس‌زمینه
    def start(self) -> Dict[str, Any]:
        if self.running():
            return {"ok": True, "message": "پاسخ‌گوی دایرکت از قبل فعال است"}
        cfg = self.cfg()
        cfg["enabled"] = True
        self.save_cfg(cfg)
        self._task = asyncio.create_task(self._loop())
        return {"ok": True, "message": "✅ پاسخ‌گوی دایرکت روشن شد"}

    def stop(self) -> Dict[str, Any]:
        cfg = self.cfg()
        cfg["enabled"] = False
        self.save_cfg(cfg)
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = None
        return {"ok": True, "message": "⏹ پاسخ‌گوی دایرکت خاموش شد"}

    def _enabled_platforms(self) -> List[str]:
        cfg = self.cfg()
        return [p for p, on in (cfg.get("platforms") or {}).items() if on]

    async def _loop(self) -> None:
        log = self.ctx["log"]
        log("💬 پاسخ‌گوی دایرکت شروع به کار کرد", "ok")
        try:
            while True:
                cfg = self.cfg()
                if not cfg.get("enabled"):
                    break
                hour = datetime.now().hour
                lo, hi = (cfg.get("active_hours") or [9, 23])[:2]
                if not (lo <= hour < hi):
                    await asyncio.sleep(120)
                    continue
                for pid in self._enabled_platforms():
                    try:
                        await self.round(pid, dry_run=False)
                    except Exception as e:  # noqa
                        log(f"⚠ دور پاسخ‌گویی {pid}: {e}", "warn")
                    await asyncio.sleep(random.uniform(4, 9))
                await asyncio.sleep(max(5, int(cfg.get("round_minutes", 20))) * 60)
        except asyncio.CancelledError:
            pass
        finally:
            log("💬 چرخهٔ پاسخ‌گوی دایرکت بسته شد")

    # -------------------------------------------------- یک دور بازرسی
    async def round(self, platform: str, *, dry_run: bool = False) -> Dict[str, Any]:
        """گفتگوهای نیازمند جواب را پیدا و (در حالت واقعی) جواب می‌دهد."""
        cfg = self.cfg()
        get_session, log = self.ctx["get_session"], self.ctx["log"]
        page_cfg = dict(DM_PAGES.get(platform) or {})
        page_cfg.update((cfg.get("selectors") or {}).get(platform) or {})
        if not page_cfg.get("url"):
            raise Exception("برای این پلتفرم پشتیبانی تعریف نشده")
        dry = dry_run or bool(cfg.get("dry_run"))

        st = self.stats()
        today = datetime.now().strftime("%Y-%m-%d")
        used_today = sum(int(v) for v in (st.get("replies") or {}).values()) if st.get("date") == today else 0
        cap = int(cfg.get("daily_cap", 40))
        if not dry and used_today >= cap:
            return {"ok": False, "message": f"سقف روزانهٔ {cap} جواب پر است — فردا ادامه می‌دهم"}

        sess = await get_session(platform)
        page = sess.page
        await page.goto(page_cfg["url"], wait_until="domcontentloaded", timeout=60000)
        await self.ctx["hdelay"](3.5, 6.5)

        # فهرست گفتگوها
        threads = page.locator(page_cfg["threads"])
        try:
            n = await threads.count()
        except Exception:
            n = 0
        if not n:
            return {"ok": False, "message": "هیچ گفتگویی پیدا نشد — سلکتورها را در پیش‌نمایش چک کنید"}
        proposals: List[Dict[str, Any]] = []
        max_round = int(cfg.get("max_per_round", 4)) if not dry else 5
        for i in range(min(n, max_round + 2)):
            if len(proposals) >= max_round:
                break
            try:
                item = threads.nth(i)
                if not await item.is_visible():
                    continue
                await item.click(timeout=8000)
                await self.ctx["hdelay"](2.2, 4.4)
                msgs = (await page.evaluate(READ_JS)) or []
                msgs = [m for m in msgs if m.get("text")]
                if not msgs:
                    continue
                # فقط وقتی جواب بده که آخرین پیام از طرف مقابل است
                if msgs[-1].get("mine"):
                    continue
                last_in = [m["text"] for m in msgs if not m.get("mine")][-4:]
                convo = " | ".join((("من: " if m.get("mine") else "او: ") + m["text"]) for m in msgs[-8:])
                h = hashlib.sha256(f"{platform}:{convo[-300:]}".encode()).hexdigest()[:16]
                if h in self._replied_hashes:
                    continue
                reply = await self._compose(platform, convo, last_in)
                if not reply:
                    continue
                self._replied_hashes.add(h)
                entry = {"platform": platform, "conversation": msgs[-6:], "reply": reply}
                if dry:
                    proposals.append(entry)
                else:
                    gap = int(cfg.get("min_reply_gap_min", 12))
                    if self._last_reply_at and (datetime.now() - self._last_reply_at).total_seconds() < gap * 60:
                        break  # فاصلهٔ طبیعی — دور بعد ادامه می‌دهیم
                    sent = await self._send(page, page_cfg.get("input", ""), reply)
                    if sent:
                        self._last_reply_at = datetime.now()
                        self._bump(platform)
                        log(f"💬 پاسخ دایرکت {platform} ارسال شد: «{reply[:60]}…»", "ok")
                        entry["sent"] = True
                        proposals.append(entry)
                    await self.ctx["hdelay"](3, 7)
            except Exception:
                continue
        if dry:
            return {"ok": True, "dry_run": True, "proposals": proposals,
                    "message": f"{len(proposals)} گفتگو نیازمند جواب پیدا شد (پیش‌نمایش — چیزی ارسال نشد)"}
        return {"ok": True, "replied": len(proposals),
                "message": f"{len(proposals)} گفتگو جواب گرفت" if proposals else "فعلاً گفتگوی بی‌جوابی نبود"}

    # -------------------------------------------------- نوشتن و ارسال جواب
    async def _compose(self, platform: str, convo: str, last_in: List[str]) -> Optional[str]:
        cfg = self.cfg()
        provider, model = self.ctx["llm_provider_model"]()
        persona = (cfg.get("persona") or "").strip()
        faq = "\n".join(f"- پرسش: {f.get('q')} → پاسخ: {f.get('a')}" for f in (cfg.get("faq") or []) if f.get("q"))
        system = (
            "تو صاحب این اکانت هستی و دایرکت‌ها را جواب می‌دهی — نه یک چت‌بات. "
            + (f"معرفی: {persona}. " if persona else "")
            + f"لحن: {cfg.get('tone', '')}. "
            "قوانین: ۱) جواب کوتاه و طبیعی مثل چت واقعی (۱ تا ۳ جمله، ایموجی کم و بجا) ۲) فارسی روان "
            "۳) فقط سراغ چیزی نرو که در معرفی/پرسش‌های متداول نیست؛ در آن صورت بگو بعداً بررسی می‌کنی "
            "۴) از دادن قیمت/قول دقیق بدون منبع خودداری کن ۵) اگر پیام مزاحم یا نامرتبط بود، محترمانه و کوتاه رد کن. "
            "فقط متن جواب را بنویس — بدون هیچ توضیحی."
            + (f"\nپرسش‌های متداول:\n{faq}" if faq else "")
        )
        try:
            reply = await self.ctx["llm_chat"](
                self.ctx["get_settings"]().get("ai", {}), provider, model,
                [{"role": "system", "content": system},
                 {"role": "user", "content": f"پلتفرم: {platform}\nآخرین پیام‌های گفتگو:\n{convo[-1500:]}"}],
                temperature=0.8, max_tokens=220)
            reply = (reply or "").strip().strip('"“”').replace("\n", " ")
            return reply[:600] if 2 <= len(reply) <= 600 else (reply[:600] or None)
        except Exception as e:  # noqa
            self.ctx["log"](f"⚠ تولید جواب دایرکت ناموفق: {e}", "warn")
            return None

    async def _send(self, page, input_sel: str, reply: str) -> bool:
        try:
            box = page.locator(input_sel).first if input_sel else None
            if box is not None:
                try:
                    await box.click(timeout=8000)
                except Exception:
                    pass
            await self.ctx["htype"](page, None, reply)  # تایپ انسانی روی کادر فعال
            await asyncio.sleep(random.uniform(0.5, 1.4))
            await self.ctx["press_enter"](page)
            await asyncio.sleep(1.6)
            return True
        except Exception:
            return False
