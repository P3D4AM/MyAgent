"""Instagram module — post, story, DM, follow, like, comment.

Login strategy
    1. Persistent profile keeps you logged-in across restarts (recommended).
    2. First run: config.json → platforms.instagram.username/password,
       the agent types them and waits for you to type the 2FA code in the
       SAME console (never stored anywhere).

Selector maintenance
    Instagram changes its DOM often — every action below tries multiple
    candidates in order and logs which one hit. Update the lists when needed.
"""

import time
from typing import Optional

from platforms.base import BasePlatform


class Instagram(BasePlatform):
    name = "instagram"
    base_url = "https://www.instagram.com/"

    LOGIN_USER_SEL = ["input[name='username']"]
    LOGIN_PASS_SEL = ["input[name='password']"]
    TWO_FACTOR_SEL = ["input[name='verificationCode']"]
    NEW_POST_BUTTON = [
        "svg[aria-label='New post']",
        "svg[aria-label='پست جدید']",
        "a[role='button'][href*='/create']",
        "div[role='button']:has(svg[aria-label='New post'])",
    ]
    FILE_INPUT = ["input[type='file'][accept*='image']"]
    CAPTION_SEL = [
        "div[role='textbox'][contenteditable='true']",
        "textarea[aria-label*='caption']",
        "textarea[placeholder*='افزودن']",
    ]
    SHARE_BUTTON = [
        "button:has-text('Share')",
        "button:has-text('اشتراک')",
        "div[role='button']:has-text('Share')",
    ]
    SEARCH_INPUT = ["input[placeholder*='Search']", "input[placeholder*='جست']"]

    # ------------------------------------------------------------------ #
    def is_logged_in(self) -> bool:
        try:
            self.page.goto(self.base_url, wait_until="domcontentloaded",
                           timeout=30_000)
        except Exception:
            pass
        self.pause(1.5, 2.5)
        logged_out = self.engine.exists("input[name='username']", timeout=4_000)
        return not logged_out

    def login(self, username: Optional[str] = None,
              password: Optional[str] = None) -> None:
        username = username or self.cfg.get("username")
        password = password or self.cfg.get("password")
        if not username or not password:
            raise RuntimeError("platforms.instagram.username/password not set "
                               "in config.json")

        page = self.open()
        self.engine.type(page, self.LOGIN_USER_SEL[0], username)
        self.pause(0.4, 0.9)
        self.engine.type(page, self.LOGIN_PASS_SEL[0], password, secret=True)
        self.pause(0.4, 0.9)
        self.engine.press(page, "Enter")
        self.log.info("credentials submitted — watching for 2FA / checks")

        # 2FA code (if enabled on the account)
        if self.engine.exists(self.TWO_FACTOR_SEL[0], timeout=8_000):
            code = input("🔑 Instagram 2FA code: ").strip()
            self.engine.type(page, self.TWO_FACTOR_SEL[0], code, secret=True)
            self.engine.press(page, "Enter")

        # "Save your login info?" → Not now
        for text in ("Not now", "الان نه", "Save"):
            try:
                btn = page.get_by_role("button", name=text).first
                btn.wait_for(state="visible", timeout=4_000)
                btn.click()
                self.pause()
            except Exception:
                continue
        self.pause(1.5, 2.5)
        self.engine.export_session(self.page, "instagram")
        self.log.info("✔ instagram login flow finished")

    # ------------------------------------------------------------------ #
    def post_photo(self, image: str, caption: str = "") -> None:
        """Upload a photo with a caption. `image` = absolute/relative file path."""
        page = self.page
        sel = self.try_selectors("new_post", self.NEW_POST_BUTTON)
        if not sel:
            self.shot("ig_no_composer")
            raise RuntimeError("Instagram: create-post button not found")
        self.engine.click(page, sel)

        # Playwright sets files directly — no OS file dialog, no mouse needed
        file_input = page.locator(self.FILE_INPUT[0]).first
        file_input.wait_for(state="attached", timeout=15_000)
        file_input.set_input_files(image)
        self.log.info("media attached → %s", image)
        self.pause(0.8, 1.6)

        # filter screen → Next
        for text in ("Next", "بعدی"):
            try:
                nxt = page.get_by_role("button", name=text).first
                nxt.wait_for(state="visible", timeout=6_000)
                nxt.click()
                self.pause()
                break
            except Exception:
                continue

        # caption
        cap = self.try_selectors("caption", self.CAPTION_SEL)
        if cap and caption:
            self.engine.type(page, cap, caption)
            self.pause(0.5, 1.2)

        share = self.try_selectors("share", self.SHARE_BUTTON, timeout_each=8_000)
        if not share:
            self.shot("ig_no_share")
            raise RuntimeError("Instagram: share button not found")
        self.engine.click(page, share)
        self.pause(2.0, 3.5)
        self.log.info("✔ photo posted (caption %s chars)", len(caption))
        self.toast("📸 عکس اینستاگرام منتشر شد")

    def upload_story(self, image: str) -> None:
        page = self.page
        story_btns = [
            "svg[aria-label='New story']",
            "svg[aria-label='استوری جدید']",
            "a[role='button'][href*='/stories/new']",
        ]
        sel = self.try_selectors("story", story_btns)
        if not sel:
            self.shot("ig_no_story")
            raise RuntimeError("Instagram: story button not found")
        self.engine.click(page, sel)
        file_input = page.locator(self.FILE_INPUT[0]).first
        file_input.wait_for(state="attached", timeout=15_000)
        file_input.set_input_files(image)
        self.pause(1.0, 2.0)
        for text in ("Share", "اشتراک‌گذاری", "Add to story"):
            try:
                btn = page.get_by_role("button", name=text).first
                btn.wait_for(state="visible", timeout=6_000)
                btn.click()
                break
            except Exception:
                continue
        self.pause(2.0, 3.0)
        self.log.info("✔ story uploaded")

    def send_dm(self, username: str, message: str) -> None:
        page = self.page
        page.goto(f"{self.base_url}direct/new/", wait_until="domcontentloaded")
        self.pause(1.0, 2.0)
        search = self.try_selectors("dm_search", self.SEARCH_INPUT)
        if not search:
            self.shot("ig_dm_search")
            raise RuntimeError("Instagram: DM search box not found")
        self.engine.type(page, search, username)
        self.pause(1.2, 2.4)
        self.engine.press(page, "Enter")          # pick first suggestion
        self.pause(0.6, 1.2)
        self.engine.press(page, "Enter")          # confirm chat
        self.pause(0.8, 1.6)
        chat_box = self.try_selectors("dm_box", [
            "textarea[placeholder*='Message']",
            "textarea[placeholder*='پیام']",
            "div[role='textbox'][contenteditable='true']",
        ])
        if not chat_box:
            self.shot("ig_dm_box")
            raise RuntimeError("Instagram: DM textbox not found")
        self.engine.type(page, chat_box, message)
        self.engine.press(page, "Enter")
        self.pause(1.0, 1.8)
        self.log.info("✔ DM sent to @%s", username)

    def follow(self, username: str) -> None:
        page = self.page
        page.goto(f"{self.base_url}{username}/", wait_until="domcontentloaded")
        self.pause(1.2, 2.2)
        for text in ("Follow", "دنبال کردن", "دنبال‌کردن"):
            try:
                btn = page.get_by_role("button", name=text).first
                btn.wait_for(state="visible", timeout=5_000)
                btn.click()
                self.log.info("✔ followed @%s", username)
                self.pause()
                return
            except Exception:
                continue
        self.log.warning("follow: maybe already following @%s", username)

    def like_latest(self, count: int = 3, scroll_times: int = 5) -> int:
        """Open the home feed and like the newest `count` posts."""
        page = self.page
        page.goto(self.base_url, wait_until="domcontentloaded")
        liked = 0
        for _ in range(scroll_times):
            if liked >= count:
                break
            for like_sel in ("svg[aria-label='Like']", "svg[aria-label='پسندیدن']"):
                hearts = page.locator(like_sel)
                for i in range(min(hearts.count(), count - liked)):
                    try:
                        hearts.nth(i).hover()
                        self.pause(0.3, 0.8)
                        hearts.nth(i).click()
                        liked += 1
                        self.pause(0.8, 1.6)
                    except Exception:
                        continue
                if liked:
                    break
            self.engine.scroll(page, 900)
        self.log.info("✔ liked %s/%s posts", liked, count)
        return liked

    def comment(self, post_url: str, text: str) -> None:
        page = self.page
        page.goto(post_url, wait_until="domcontentloaded")
        self.pause(1.5, 2.5)
        box = self.try_selectors("comment", [
            "textarea[placeholder*='Add a comment']",
            "textarea[placeholder*='افزودن']",
            "textarea[aria-label*='comment']",
        ])
        if not box:
            self.shot("ig_comment")
            raise RuntimeError("Instagram: comment box not found")
        self.engine.type(page, box, text)
        self.engine.press(page, "Enter")
        self.pause(1.0, 2.0)
        self.log.info("✔ comment posted on %s", post_url)
