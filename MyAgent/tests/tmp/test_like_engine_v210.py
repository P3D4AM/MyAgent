# -*- coding: utf-8 -*-
"""اعتبارسنجی v2.10.0 — موتور لایک مقاوم (۴ پلتفرم) + استوری فیسبوک + حذف استوری اینستاگرام.

با مرورگر Chromium واقعی (Playwright) و صفحات ماکِ شبیه DOM روز هر پلتفرم:
  - اینستاگرام: article + section نوار اکشن + لیبل فارسی/انگلیسی + فید بی‌نهایت با اسکرول
  - توییتر/X:   article[data-testid='tweet'] + button[data-testid='like'] (مستقل از زبان)
  - فیسبوک:     div[role='article'][aria-posinset] + دکمهٔ دقیق 'Like' (نه «Liked»!)
  - لینکدین:    div[data-id^='urn:li:activity'] + برچسب داینامیک «Like John's post»
هر کلیک واقعی روی صفحه اجرا می‌شود و نتیجه از DOM خوانده می‌شود."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, "/home/z/my-project/parsagent")
import panel_server as ps  # noqa

from playwright.async_api import async_playwright

PASS, FAIL = [], []


def check(name, cond, extra=""):
    (PASS if cond else FAIL).append(name)
    print(("✅" if cond else "❌") + f" {name}" + (f"  [{extra}]" if extra else ""))


class _FastRandom:
    """random سریع برای تست — مقادیر را به حداقل می‌برد."""

    def uniform(self, a, b): return float(a) if a else 0.01
    def randint(self, a, b): return int(a)
    def randrange(self, *a): return int(a[0]) if a else 1
    def random(self): return 0.5


class FakeSess:
    def __init__(self, page):
        self.page = page

    async def ensure(self):
        return self.page


MOCKS = Path("/tmp/like_mocks_v210")
MOCKS.mkdir(exist_ok=True)

# ---------------------------------------------------------------- ماک اینستاگرام
IG_MOCK = """
<body><style>article{height:90px;padding:6px;border:1px solid #ccc}
svg{width:26px;height:26px;display:inline-block}</style><main id="feed"></main>
<script>
const feed = document.getElementById('feed');
function post(label, opts={}) {
  const a = document.createElement('article');
  const sec = document.createElement('section');
  const d = document.createElement('div');
  const svg = document.createElement('svg');
  svg.setAttribute('aria-label', label);
  if (opts.hidden) svg.style.display = 'none';
  d.appendChild(svg); sec.appendChild(d); a.appendChild(sec);
  if (opts.decoy) { // لایکِ کامنت — داخل article ولی بیرون از section و مخفی
    const c = document.createElement('div');
    const ds = document.createElement('svg'); ds.setAttribute('aria-label', 'Like');
    ds.style.display = 'none'; ds.className = 'decoy';
    c.appendChild(ds); a.appendChild(c);
  }
  feed.appendChild(a);
}
post('Unlike');                       // از قبل لایک‌شده + دکوی کامنت مخفی
post('پسندیدن', {decoy: true});
post('Like');
post('پسندیدن');
let added = 0;
window.addEventListener('wheel', () => {   // فید بی‌نهایت: با اسکرول پست تازه می‌آید
  if (added < 3) { added++; post('Like'); }
});
document.addEventListener('click', e => {
  const el = e.target.closest('[aria-label]');
  if (!el) return;
  const a = el.getAttribute('aria-label') || '';
  if (a === 'Like' || a === 'پسندیدن') {
    el.setAttribute('aria-label', a === 'Like' ? 'Unlike' : 'برداشتن پسند');
    window._likedSeq = (window._likedSeq || 0) + 1;
  }
}, true);
</script></body>
"""

# ---------------------------------------------------------------- ماک توییتر
TW_MOCK = """
<body><div id="tl"></div>
<script>
const tl = document.getElementById('tl');
function tweet(liked) {
  const a = document.createElement('article'); a.setAttribute('data-testid', 'tweet');
  const b = document.createElement('button');
  b.setAttribute('data-testid', liked ? 'unlike' : 'like');
  b.setAttribute('aria-label', liked ? 'برداشتن پسند' : 'پسندیدن');
  b.addEventListener('click', () => {
    b.setAttribute('data-testid', 'like' === b.getAttribute('data-testid') ? 'unlike' : 'like');
    b.setAttribute('aria-label', 'like' === b.getAttribute('aria-label') ? 'x' : 'برداشتن پسند');
    if (b.getAttribute('data-testid') === 'unlike') window._twLiked = (window._twLiked||0)+1;
  });
  a.appendChild(b); tl.appendChild(a);
}
tweet(false); tweet(true); tweet(false);
let added = 0;
window.addEventListener('wheel', () => { if (added < 3) { added++; tweet(false); } });
</script></body>
"""

# ---------------------------------------------------------------- ماک فیسبوک
FB_MOCK = """
<body><div id="feed"></div>
<div role="button" aria-label="Like Page" id="pageLike">Like Page</div>
<script>
const feed = document.getElementById('feed');
function post(state, pos) {
  const a = document.createElement('div'); a.setAttribute('role', 'article');
  a.setAttribute('aria-posinset', String(pos));
  const b = document.createElement('div'); b.setAttribute('role', 'button');
  b.setAttribute('aria-label', state); b.textContent = state;
  b.addEventListener('click', () => {
    const cur = b.getAttribute('aria-label');
    if (cur === 'Like') { b.setAttribute('aria-label', 'Liked'); b.textContent = 'Liked'; window._fbLiked = (window._fbLiked||0)+1; }
    else if (cur === 'پسندیدن') { b.setAttribute('aria-label', 'پسندیدم'); b.textContent = 'پسندیدم'; window._fbLiked = (window._fbLiked||0)+1; }
    // «Liked» و «پسندیدم» کلیک نشوند — دکمهٔ دقیق فقط Like است
  });
  a.appendChild(b); feed.appendChild(a);
}
post('Like', 1); post('Liked', 2); post('پسندیدن', 3);
</script></body>
"""

# ---------------------------------------------------------------- ماک لینکدین
LI_MOCK = """
<body><div id="feed"></div>
<script>
const feed = document.getElementById('feed');
function post(label) {
  const a = document.createElement('div');
  a.setAttribute('data-id', 'urn:li:activity:' + Math.floor(Math.random()*1e9));
  const b = document.createElement('button'); b.setAttribute('aria-label', label);
  b.addEventListener('click', () => {
    const cur = b.getAttribute('aria-label');
    if (cur.startsWith('Like')) { b.setAttribute('aria-label', 'Unlike ' + cur.slice(4)); window._liLiked = (window._liLiked||0)+1; }
    else if (cur.startsWith('پسندیدن')) { b.setAttribute('aria-label', 'برداشتن پسند'); window._liLiked = (window._liLiked||0)+1; }
  });
  a.appendChild(b); feed.appendChild(a);
}
post("Like Ali Rezaei's post. Button available");
post("Unlike Sara Ahmadi's post");
post('پسندیدن پستِ محمد');
</script></body>
"""

# ------------------------------------------------- ماک صفحهٔ لاگین (اینستاگرام روی آدرس اصلی)
IG_LOGIN_WALL = """<body><form><input type="text" name="username">
<input type="password" name="password"></form></body>"""

# ------------------------------------------------- ماک فیسبوک استوری
FB_STORY_MOCK = """
<body>
<div id="cs" role="button" aria-label="Create story">Create story</div>
<div id="photo" role="button" style="display:none"><span>Create photo story</span></div>
<input type="file" accept="image/*" style="display:none" id="fin">
<div id="share" role="button" aria-label="Share story" style="display:none">Share story</div>
<script>
document.getElementById('cs').addEventListener('click', () => {
  document.getElementById('photo').style.display = 'block';
});
document.getElementById('photo').addEventListener('click', () => {
  document.getElementById('photo').style.display = 'none';
  const f = document.getElementById('fin'); f.style.display = 'block';
  f.addEventListener('change', () => { document.getElementById('share').style.display = 'block'; });
});
document.getElementById('share').addEventListener('click', () => { window._shared = true; });
</script></body>
"""

(MOCKS / "ig.html").write_text(IG_MOCK, encoding="utf-8")
(MOCKS / "tw.html").write_text(TW_MOCK, encoding="utf-8")
(MOCKS / "fb.html").write_text(FB_MOCK, encoding="utf-8")
(MOCKS / "li.html").write_text(LI_MOCK, encoding="utf-8")
(MOCKS / "ig_home_loginwall.html").write_text(IG_LOGIN_WALL, encoding="utf-8")
(MOCKS / "login_page.html").write_text(IG_LOGIN_WALL, encoding="utf-8")
(MOCKS / "fb_stories.html").write_text(FB_STORY_MOCK, encoding="utf-8")

ROUTE = {
    "https://www.instagram.com/": MOCKS / "ig.html",
    "https://x.com/home": MOCKS / "tw.html",
    "https://www.facebook.com/": MOCKS / "fb.html",
    "https://www.linkedin.com/feed/": MOCKS / "li.html",
    "https://www.facebook.com/stories": MOCKS / "fb_stories.html",
}
LOGIN_WALL_ROUTE = "https://www.instagram.com/__loginwall__"


async def main():
    orig_goto, orig_hdelay, orig_random = ps.goto, ps.hdelay, ps.random
    current = {"url": None}

    async def mock_goto(page, url, attempts=3):
        target = current["url"] or url
        await page.goto((ROUTE.get(target) or MOCKS / "ig.html").as_uri(),
                        wait_until="domcontentloaded")

    async def fast_delay(lo=0.8, hi=2.8):
        await asyncio.sleep(0.01)

    ps.goto, ps.hdelay, ps.random = mock_goto, fast_delay, _FastRandom()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 900, "height": 700})

        # ================= اینستاگرام — ۵ لایک از فید بی‌نهایت (۱ پست از قبل لایک‌شده)
        page = await ctx.new_page()
        sess = FakeSess(page)
        res = await ps.ACTION_IMPL[("instagram", "like")](sess, {"count": 5})
        liked = await page.evaluate("window._likedSeq || 0")
        unlikes = await page.evaluate("document.querySelectorAll(\"article svg[aria-label='Unlike']\").length")
        removed = await page.evaluate("document.querySelectorAll(\"article svg[aria-label='برداشتن پسند']\").length")
        decoy = await page.evaluate("document.querySelector('svg.decoy') === null ? 'gone' : document.querySelector('svg.decoy').getAttribute('aria-label')")
        check("IG: نتیجه ok=True و پیام درست", res["ok"] is True and "لایک انجام شد: 5" in res["message"], str(res))
        check("IG: دقیقاً ۵ کلیکِ لایکِ تازه انجام شد", liked == 5, f"liked={liked}")
        check("IG: تأییدِ بعد از کلیک — برچسب به Unlike/برداشتن پسند تغییر کرد", unlikes >= 1 and removed >= 1, f"unlike={unlikes} برداشتن={removed}")
        check("IG: پستِ از‌قبل‌لایک‌شده دست نخورد (لایک برنداشته شد؟)", unlikes + removed == 6 and unlikes >= 1, f"unlike={unlikes} برداشتن={removed} (مجموع باید ۱ قدیمی+۵ تازه=۶ باشد)")
        check("IG: دکویِ کامنتِ مخفی هرگز کلیک نشد", decoy == "Like", f"decoy={decoy}")
        check("IG: فید بی‌نهایت — با اسکرول پست تازه آمد (بیشتر از ۴ پست اولیه)", await page.evaluate("document.querySelectorAll('article').length") >= 5)
        await page.close()

        # ================= توییتر — data-testid مستقل از زبان + اسکرول
        page = await ctx.new_page()
        sess = FakeSess(page)
        res = await ps.ACTION_IMPL[("twitter", "like")](sess, {"count": 4})
        liked = await page.evaluate("window._twLiked || 0")
        check("TW: نتیجه ok و ۴ لایک", res["ok"] is True and "4" in res["message"], str(res))
        check("TW: کلیک‌ها از راه data-testid (مستقل از زبان) شد", liked == 4, f"liked={liked}")
        check("TW: پستِ از‌قبل‌لایک‌شده (unlike) دست نخورد",
              await page.evaluate("document.querySelectorAll(\"button[data-testid='unlike']\").length") == 5)
        await page.close()

        # ================= فیسبوک — دکمهٔ دقیق، نه «شامل»
        page = await ctx.new_page()
        sess = FakeSess(page)
        res = await ps.ACTION_IMPL[("facebook", "like")](sess, {"count": 5})
        liked = await page.evaluate("window._fbLiked || 0")
        preliked = await page.evaluate("document.querySelectorAll(\"div[role='button'][aria-label='Liked'],div[role='button'][aria-label='پسندیدم']\").length")
        page_like = await page.evaluate("document.getElementById('pageLike').getAttribute('aria-label')")
        check("FB: ۲ لایک انجام شد (از ۲ قابل‌لایک) و ok=True", res["ok"] is True and "لایک انجام شد: 2 از 5" in res["message"], str(res))
        check("FB: دقیقاً ۲ کلیک", liked == 2, f"liked={liked}")
        check("FB: پستِ از‌قبل‌لایک‌شده «Liked» → «Like» برنگشت (لایک برنداشته شد؟ نه!)",
              preliked == 3 and (await page.evaluate("document.querySelectorAll(\"div[role='article'][aria-posinset='2'] div[role='button']\")[0].getAttribute('aria-label')")) == "Liked")
        check("FB: دکمهٔ «Like Page» بیرون از پست‌ها کلیک نشد", page_like == "Like Page", f"pageLike={page_like}")
        await page.close()

        # ================= لینکدین — برچسب داینامیک
        page = await ctx.new_page()
        sess = FakeSess(page)
        res = await ps.ACTION_IMPL[("linkedin", "like")](sess, {"count": 2})
        liked = await page.evaluate("window._liLiked || 0")
        check("LI: ۲ لایک ok", res["ok"] is True and "لایک انجام شد: 2" in res["message"], str(res))
        check("LI: پستِ Unlike رد شد (فقط ۲ کلیک)", liked == 2, f"liked={liked}")
        check("LI: تأیید — دکمه‌ها به Unlike/برداشتن پسند تغییر کردند",
              await page.evaluate("document.querySelectorAll(\"button[aria-label^='Unlike'],button[aria-label^='برداشتن']\").length") == 3)
        await page.close()

        # ================= اینستاگرامِ لاگین‌نشده — چک ورود (آدرس لاگین)
        page = await ctx.new_page()
        sess = FakeSess(page)
        current["url"] = "https://www.instagram.com/accounts/login/"

        async def loginwall_goto(pg, url, attempts=3):
            await pg.goto((MOCKS / "ig_home_loginwall.html").as_uri(), wait_until="domcontentloaded")

        ps.goto = loginwall_goto
        res = await ps.ACTION_IMPL[("instagram", "like")](sess, {"count": 3})
        # آدرس ماک «ig_home_loginwall» شامل /login نیست → تشخیص از راه فرم رمز
        check("IG لاگین‌نشده: پیام «وارد نشده‌اید» با راهنمای دکمهٔ ورود",
              res["ok"] is False and "وارد" in res["message"] and "ورود" in res["message"], str(res))
        ps.goto = mock_goto
        await page.close()

        # ================= تشخیص آدرس لاگین (marker در URL)
        page = await ctx.new_page()
        await page.goto((MOCKS / "login_page.html").as_uri(), wait_until="domcontentloaded")
        out = await ps._looks_logged_out(page, list(ps.LOGIN_URL_MARKERS["instagram"]))
        check("IG: تشخیص لاگین از خودِ URL (/login در آدرس)", out is True)
        await page.close()

        # ================= فید خالی — پیام راهنما (بدون انتظار ۲۵ ثانیه، timeout کوچک مستقیم)
        page = await ctx.new_page()
        await page.goto("about:blank")
        got = await ps._wait_feed(page, ps.LIKE_ENGINES["instagram"]["posts"], timeout=1.2)
        check("موتور: _wait_feed روی صفحهٔ خالی None برمی‌گرداند", got is None)
        await page.close()

        # ================= همهٔ پست‌ها از قبل لایک‌شده — پیام «هیچ پست لایک‌نشدنی»
        page = await ctx.new_page()
        sess = FakeSess(page)
        await page.set_content("""<body><main>
        <article><section><svg aria-label='Unlike'></svg></section></article>
        <article><section><svg aria-label='برداشتن پسند'></svg></section></article>
        </main></body>""")

        async def content_goto(pg, url, attempts=3):
            pass  # صفحه از قبل ست شده

        ps.goto = content_goto
        res = await ps.ACTION_IMPL[("instagram", "like")](sess, {"count": 3})
        check("IG: همه‌لایک‌شده → پیام «هیچ پستِ لایک‌نشدنی پیدا نشد»",
              res["ok"] is False and "لایک‌نشدنی" in res["message"], str(res))
        ps.goto = mock_goto
        await page.close()

        # ================= استوری فیسبوک — فلو کامل با ماک
        page = await ctx.new_page()
        sess = FakeSess(page)
        current["url"] = "https://www.facebook.com/stories"   # مسیر استوری فعال شود
        media = Path(ps.MEDIA_DIR) / "v210_test_story.png"
        if not media.exists():
            media.parent.mkdir(parents=True, exist_ok=True)
            # ۱×۱ پیکسل PNG واقعی
            media.write_bytes(bytes.fromhex(
                "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
                "1f15c4890000000d49444154789c6360000002000100"
                "05ff0a4f4b0000000049454e44ae426082"))
        res = await ps.ACTION_IMPL[("facebook", "post_story")](sess, {"media": media.name})
        shared = await page.evaluate("window._shared === true")
        check("FB استوری: ok=True و پیام «استوری فیسبوک ارسال شد»",
              res["ok"] is True and "استوری فیسبوک ارسال شد" in res["message"], str(res))
        check("FB استوری: فلو کامل Create story → photo story → فایل → Share story", shared is True)
        await page.close()

        # ================= ویدیو → پیام «ویدیو از وب ممکن نیست»
        vid = Path(ps.MEDIA_DIR) / "v210_test_story.mp4"
        vid.write_bytes(b"\x00\x00\x00\x18ftypmp42")
        res = await ps.ACTION_IMPL[("facebook", "post_story")](sess, {"media": vid.name})
        check("FB استوری: ویدیو با پیام روشن رد می‌شود", res["ok"] is False and "ویدیو" in res["message"], str(res))
        try:
            media.unlink(); vid.unlink()
        except Exception:
            pass

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
