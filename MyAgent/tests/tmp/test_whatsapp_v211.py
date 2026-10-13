# -*- coding: utf-8 -*-
"""اعتبارسنجی v2.11.0 — پلتفرم هشتم: واتساپ وب.

با مرورگر Chromium واقعی (Playwright) و صفحهٔ ماکِ شبیه DOM واتساپ وب:
  - جعبهٔ جستجو: div[data-testid='chat-list-search'] div[contenteditable='true'][data-tab='3']
  - نتایج جستجو: #side div[role='listitem'] (با فیلتر زنده روی متن تایپ‌شده)
  - چت باز: #main header span[title] (نام چت) + footer contenteditable (جعبهٔ پیام)
  - رفتار واقعی Enter (ارسال و خالی شدن جعبه) و Shift+Enter (سطر جدید)
  - صفحهٔ اسکن QR: canvas[aria-label*='Scan this QR code'] + div[data-ref]

سنجه‌ها:
  ۱) ورود: از قبل وارد شده / QR بعد از تأخیر اسکن می‌شود / اسکن نشد / QR دیده نشد
  ۲) ارسال پیام: بدون ورود → پیام راهنما؛ تک‌گیرنده؛ چندخطی؛ چندگیرنده با یک نام ناموجود؛
     بدون پارامتر؛ حفاظت «چت اشتباه» (جستجوی بی‌نتیجه پیام نمی‌فرستد)
"""
import asyncio
import sys

sys.path.insert(0, "/home/z/my-project/parsagent")
import panel_server as ps  # noqa

from playwright.async_api import async_playwright

PASS, FAIL = [], []


def check(name, cond, extra=""):
    (PASS if cond else FAIL).append(name)
    print(("✅" if cond else "❌") + f" {name}" + (f"  [{extra}]" if extra else ""))


class _FastRandom:
    def uniform(self, a, b): return float(a) if a else 0.01
    def randint(self, a, b): return int(a)
    def randrange(self, *a): return int(a[0]) if a else 1
    def random(self): return 0.5


class FakeSess:
    def __init__(self, page, platform="whatsapp"):
        self.page = page
        self.platform = platform

    async def ensure(self):
        return self.page


# --------------------------------------------------------------- ماک واتساپ وب
# سه مخاطب ذخیره‌شده؛ «نام ناموجود» عمداً در هیچ‌کدام هست نیست.
# ⚠️ r-string است چون JS داخلش '\n' دارد — بدون r، پایتون \n را به سطر واقعی
# تبدیل می‌کند و کل <script> با SyntaxError می‌میرد (تست همین باگ را کشف کرد).
WA_MOCK_LOGGED_IN = r"""
<body><style>
#side{width:260px;min-height:400px;border:1px solid #ccc;float:right}
#searchbox{min-height:26px;width:220px;border:1px solid #999;padding:3px}
div[role='listitem']{height:40px;border-bottom:1px solid #eee;padding:4px}
#main{width:420px;min-height:400px;border:1px solid #ccc;float:left;display:none}
#msgbox{min-height:30px;width:360px;border:1px solid #999;padding:5px}
#chatname{min-height:20px;display:inline-block;padding:4px;font-weight:700}
.message-out{background:#d9fdd3;padding:4px 8px;margin:3px 0}
</style>
<div id="side">
  <div data-testid="chat-list-search">
    <div id="searchbox" contenteditable="true" data-tab="3"></div>
  </div>
  <div id="results"></div>
</div>
<div id="main">
  <header><span id="chatname" dir="auto"></span></header>
  <div id="messages"></div>
  <footer><div id="msgbox" contenteditable="true" data-tab="10"></div></footer>
</div>
<script>
const contacts = [
  {title: 'علی رضایی'},
  {title: 'گروه فروش'},
  {title: 'رضا محمدی'},
];
const results = document.getElementById('results');
function render(list) {
  results.innerHTML = '';
  list.forEach(c => {
    const li = document.createElement('div');
    li.setAttribute('role', 'listitem');
    li.dataset.name = c.title;
    li.textContent = c.title;
    li.addEventListener('click', () => openChat(c));
    results.appendChild(li);
  });
}
render(contacts);
const searchbox = document.getElementById('searchbox');
searchbox.addEventListener('input', () => {
  const q = searchbox.textContent.trim();
  render(q ? contacts.filter(c => c.title.includes(q)) : contacts);
});
function openChat(c) {
  document.getElementById('main').style.display = 'block';
  document.getElementById('chatname').textContent = c.title;   // نام چت در هدر
  searchbox.textContent = '';   // واتساپ بعد از باز شدن چت جستجو را پاک می‌کند
  render(contacts);
}
const msgbox = document.getElementById('msgbox');
// شبیه‌سازی سطر جدید: واتساپ واقعی <br> می‌گذارد که در textContent دیده نمی‌شود؛
// اینجا محل هر Shift+Enter یادداشت و هنگام ارسال به سطرِ واقعی تبدیل می‌شود.
let lineBreaks = [];
msgbox.addEventListener('keydown', e => {
  if (e.key === 'Enter' && e.shiftKey) {       // Shift+Enter = سطر جدید
    e.preventDefault();
    lineBreaks.push(msgbox.textContent.length);
  } else if (e.key === 'Enter') {               // Enter = ارسال
    e.preventDefault();
    let t = msgbox.textContent;
    for (let i = lineBreaks.length - 1; i >= 0; i--)
      t = t.slice(0, lineBreaks[i]) + '\n' + t.slice(lineBreaks[i]);
    lineBreaks = [];
    const t2 = t;
    if (t2.trim()) {
      const m = document.createElement('div');
      m.className = 'message-out';
      m.textContent = t;
      m.style.whiteSpace = 'pre-line';
      document.getElementById('messages').appendChild(m);
    }
    msgbox.textContent = '';
  }
});
</script>
"""

# صفحهٔ QR — با اسکن بعد از ~۲.۵ ثانیه (تست صبر هوشمند)
WA_MOCK_QR_SCAN = """
<body><style>canvas{width:200px;height:200px;border:1px solid #ccc}
#side,#main{display:none}</style>
<div data-ref="2@abcd"><canvas aria-label="Scan this QR code to pair"></canvas></div>
<script>
setTimeout(() => {           // شبیه‌سازی اسکن QR با گوشی
  document.body.innerHTML = `<div id="side">
    <div data-testid="chat-list-search">
      <div id="searchbox" contenteditable="true" data-tab="3" style="min-height:26px;width:200px;border:1px solid #999"></div>
    </div>
    <div id="results"><div role="listitem" style="height:40px">علی رضایی</div></div>
  </div>`;
}, 2500);
</script>
"""

# صفحهٔ QR که هرگز اسکن نمی‌شود
WA_MOCK_QR_STUCK = """
<body><style>canvas{width:200px;height:200px;border:1px solid #ccc}</style>
<div data-ref="2@xyz"><canvas aria-label="Scan this QR code to pair"></canvas></div>
"""


async def main():
    orig_goto, orig_hdelay, orig_random = ps.goto, ps.hdelay, ps.random

    async def noop_goto(page, url, attempts=3):
        pass  # محتوا با set_content از قبل ست شده

    async def fast_delay(lo=0.8, hi=2.8):
        await asyncio.sleep(0.01)

    ps.goto, ps.hdelay, ps.random = noop_goto, fast_delay, _FastRandom()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 900, "height": 700})

        # ================= ورود: از قبل وارد شده
        page = await ctx.new_page()
        sess = FakeSess(page)
        await page.set_content(WA_MOCK_LOGGED_IN)
        res = await ps.ACTION_IMPL[("whatsapp", "login")](sess, {})
        check("WA ورود: از قبل وارد → ok=True و پیام «از قبل وارد»",
              res["ok"] is True and "از قبل وارد" in res["message"], str(res))
        await page.close()

        # ================= ورود: QR بعد از ۲.۵ ثانیه اسکن می‌شود (صبر هوشمند)
        page = await ctx.new_page()
        sess = FakeSess(page)
        await page.set_content(WA_MOCK_QR_SCAN)
        res = await ps._wa_qr_login(page, wait_s=12)
        check("WA ورود: اسکن QR تشخیص شد → ok=True و پیام «QR اسکن شد»",
              res["ok"] is True and "QR اسکن شد" in res["message"], str(res))
        await page.close()

        # ================= ورود: QR اسکن نمی‌شود → پیام «اسکن QR انجام نشد»
        page = await ctx.new_page()
        sess = FakeSess(page)
        await page.set_content(WA_MOCK_QR_STUCK)
        res = await ps._wa_qr_login(page, wait_s=3)
        check("WA ورود: اسکن نشد → ok=False و راهنمای گام‌به‌گام گوشی",
              res["ok"] is False and "اسکن QR انجام نشد" in res["message"]
              and "دستگاه‌های متصل" in res["message"], str(res))
        await page.close()

        # ================= ورود: نه فهرست چت نه QR → پیام «کد QR دیده نشد»
        page = await ctx.new_page()
        sess = FakeSess(page)
        await page.set_content("<body><h1>Link with phone number</h1></body>")
        res = await ps._wa_qr_login(page, wait_s=2)
        check("WA ورود: QR دیده نشد → ok=False و اشاره به حالت شماره تلفن",
              res["ok"] is False and "کد QR دیده نشد" in res["message"], str(res))
        await page.close()

        # ================= ارسال: بدون ورود → پیام راهنمای QR
        page = await ctx.new_page()
        sess = FakeSess(page)
        await page.set_content(WA_MOCK_QR_STUCK)
        res = await ps.ACTION_IMPL[("whatsapp", "send_message")](
            sess, {"target": "علی", "text": "سلام"})
        check("WA ارسال: بدون ورود → ok=False و پیام «وارد نشده‌اید» + راهنمای QR",
              res["ok"] is False and "وارد نشده‌اید" in res["message"]
              and "QR" in res["message"], str(res))
        await page.close()

        # ================= ارسال: بدون پارامتر → خطای روشن
        page = await ctx.new_page()
        sess = FakeSess(page)
        await page.set_content(WA_MOCK_LOGGED_IN)
        res = await ps.ACTION_IMPL[("whatsapp", "send_message")](sess, {})
        check("WA ارسال: بدون گیرنده/متن → ok=False «هر دو لازم‌اند»",
              res["ok"] is False and "لازم‌اند" in res["message"], str(res))

        # ================= ارسال: تک‌گیرنده + پیام چندخطی
        res = await ps.ACTION_IMPL[("whatsapp", "send_message")](
            sess, {"target": "علی رضایی", "text": "سلام علی\nقیمت‌ها را بفرست"})
        sent = await page.evaluate(
            "Array.from(document.querySelectorAll('.message-out')).map(m => m.textContent)")
        check("WA ارسال: تک‌گیرنده → ok=True و «۱ گیرنده»",
              res["ok"] is True and "1 گیرنده" in res["message"], str(res))
        check("WA ارسال: هر دو سطر پیام چندخطی درست ارسال شد (Shift+Enter)",
              len(sent) == 1 and sent[0].replace("\n", " ").strip() == "سلام علی قیمت‌ها را بفرست",
              f"sent={sent}")
        check("WA ارسال: جعبهٔ پیام بعد از ارسال خالی شد",
              (await page.evaluate("document.getElementById('msgbox').textContent")).strip() == "")
        check("WA ارسال: پیام به چت درست رفت (هدر=علی رضایی)",
              (await page.evaluate("document.getElementById('chatname').textContent")) == "علی رضایی")

        # ================= حفاظت «چت اشتباه»: جستجوی بی‌نتیجه پیام نمی‌فرستد
        before = await page.evaluate("document.querySelectorAll('.message-out').length")
        res = await ps.ACTION_IMPL[("whatsapp", "send_message")](
            sess, {"target": "نام ناموجود", "text": "نباید برسد"})
        after = await page.evaluate("document.querySelectorAll('.message-out').length")
        check("WA حفاظت: جستجوی بی‌نتیجه → ok=False با «هیچ‌کدام»",
              res["ok"] is False and "هیچ‌کدام" in res["message"], str(res))
        check("WA حفاظت: هیچ پیامی به چت قبلی (اشتباهی) ارسال نشد",
              after == before, f"before={before} after={after}")

        # ================= ارسال: چندگیرنده — یکی می‌رسد، یکی پیدا نمی‌شود
        res = await ps.ACTION_IMPL[("whatsapp", "send_message")](
            sess, {"target": "گروه فروش، نام ناموجود", "text": "سلام به همه"})
        sent_names = await page.evaluate(
            "Array.from(document.querySelectorAll('.message-out')).map(m => m.textContent)")
        check("WA ارسال: چندگیرنده → ok=True و «۱ گیرنده» (یکی پیدا نشد)",
              res["ok"] is True and "1 گیرنده" in res["message"], str(res))
        check("WA ارسال: نام گیرنده ناموفق در پیام نتیجه اعلام شد",
              "نام ناموجود" in res.get("message", ""), str(res))
        check("WA ارسال: پیام فقط به چت درست (گروه فروش) رفت",
              (await page.evaluate("document.getElementById('chatname').textContent")) == "گروه فروش"
              and any("سلام به همه" in s for s in sent_names), f"sent={sent_names}")

        # ================= ارسال: نصف‌نام (فقط اسم کوچکِ ذخیره) هم تطبیق می‌خورد
        res = await ps.ACTION_IMPL[("whatsapp", "send_message")](
            sess, {"target": "رضا", "text": "سلام رضا"})
        check("WA ارسال: اسم کوتاه (رضا) با چت «رضا محمدی» تطبیق خورد و ارسال شد",
              res["ok"] is True and "1 گیرنده" in res["message"], str(res))
        await page.close()

        await ctx.close()
        await browser.close()

    ps.goto, ps.hdelay, ps.random = orig_goto, orig_hdelay, orig_random
    print("\n" + "=" * 60)
    print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("FAILED:", *FAIL, sep="\n  - ")
        sys.exit(1)
    print("ALL TESTS PASSED")


asyncio.run(main())
