"""Facebook module — status/photo posts, page posts, likes and comments.

Facebook's UI is heavily A/B-tested; aria-labels differ per language.
We therefore match on several label variants (English + Persian).
"""

from typing import Optional

from platforms.base import BasePlatform


class Facebook(BasePlatform):
    name = "facebook"
    base_url = "https://www.facebook.com/"

    COMPOSER_TRIGGERS = [
        "div[role='button'][aria-label*='Create a post']",
        "div[role='button'][aria-label*='ایجاد پست']",
        "div[role='button'][aria-label*='Write something']",
    ]
    STATUS_BOX = [
        "div[role='textbox'][contenteditable='true'][aria-label*='post']",
        "div[contenteditable='true'][aria-label*='متن']",
        "div[role='textbox'][contenteditable='true']",
    ]
    POST_BUTTONS = [
        "div[role='button'][aria-label*='Post']",
        "div[aria-label='Post'][role='button']",
        "span:has-text('پست')",
    ]

    # ------------------------------------------------------------------ #
    def is_logged_in(self) -> bool:
        return self.engine.exists("div[aria-label*='Facebook']",
                                  timeout=5_000) and not self.engine.exists(
            "input[name='email']", timeout=3_000)

    def login(self, email: Optional[str] = None, password: Optional[str] = None) -> None:
        email = email or self.cfg.get("email")
        password = password or self.cfg.get("password")
        if not email or not password:
            raise RuntimeError("platforms.facebook.email/password not set")

        page = self.open()
        self.engine.type(page, "input[name='email']", email)
        self.pause(0.4, 0.9)
        self.engine.type(page, "input[name='password']", password, secret=True)
        self.pause(0.4, 0.9)
        self.engine.press(page, "Enter")
        self.pause(3.0, 5.0)
        self.engine.export_session(self.page, "facebook")
        self.log.info("✔ facebook login flow finished")

    # ------------------------------------------------------------------ #
    def post_status(self, text: str, image: Optional[str] = None) -> None:
        page = self.page
        page.goto(self.base_url, wait_until="domcontentloaded")
        self.pause(2.0, 3.5)

        trigger = self.try_selectors("composer", self.COMPOSER_TRIGGERS,
                                     timeout_each=8_000)
        if not trigger:
            self.shot("fb_composer")
            raise RuntimeError("Facebook: composer not found")
        self.engine.click(page, trigger)
        self.pause(1.2, 2.2)

        if image:
            attach = page.locator("input[type='file'][accept*='image']").first
            attach.wait_for(state="attached", timeout=10_000)
            attach.set_input_files(image)
            self.log.info("media attached → %s", image)
            self.pause(2.0, 3.5)

        box = self.try_selectors("status", self.STATUS_BOX, timeout_each=8_000)
        if not box:
            self.shot("fb_status")
            raise RuntimeError("Facebook: status box not found")
        self.engine.type(page, box, text)
        self.pause(0.8, 1.6)

        btn = self.try_selectors("post_btn", self.POST_BUTTONS, timeout_each=8_000)
        if not btn:
            self.shot("fb_post_btn")
            raise RuntimeError("Facebook: post button not found")
        self.engine.click(page, btn)
        self.pause(2.5, 4.0)
        self.log.info("✔ status posted (%s chars%s)",
                      len(text), " +image" if image else "")
        self.toast("📘 پست فیسبوک منتشر شد")

    def like_post(self, post_url: str) -> None:
        page = self.page
        page.goto(post_url, wait_until="domcontentloaded")
        self.pause(2.0, 3.0)
        like = self.try_selectors("like", [
            "div[role='button'][aria-label*='Like']",
            "div[role='button'][aria-label*='پسندیدن']",
        ])
        if not like:
            self.log.warning("like: button not found (already liked?)")
            return
        self.engine.click(page, like)
        self.pause(0.8, 1.6)
        self.log.info("✔ liked %s", post_url)

    def comment(self, post_url: str, text: str) -> None:
        page = self.page
        page.goto(post_url, wait_until="domcontentloaded")
        self.pause(2.0, 3.0)
        box = self.try_selectors("comment", [
            "div[role='textbox'][contenteditable='true'][aria-label*='comment']",
            "div[role='textbox'][contenteditable='true'][aria-label*='نظر']",
        ])
        if not box:
            self.shot("fb_comment")
            raise RuntimeError("Facebook: comment box not found")
        self.engine.type(page, box, text)
        self.pause(0.4, 0.9)
        self.engine.press(page, "Enter")
        self.pause(1.0, 2.0)
        self.log.info("✔ comment posted on %s", post_url)

    def page_post(self, page_name: str, text: str, image: Optional[str] = None) -> None:
        """Publish as one of your managed pages (page_name as in the URL)."""
        page = self.page
        page.goto(f"{self.base_url}{page_name}/", wait_until="domcontentloaded")
        self.pause(2.0, 3.0)
        trigger = self.try_selectors("page_composer", self.COMPOSER_TRIGGERS,
                                     timeout_each=8_000)
        if not trigger:
            self.shot("fb_page_composer")
            raise RuntimeError("Facebook: page composer not found")
        self.engine.click(page, trigger)
        self.pause(1.2, 2.0)
        if image:
            attach = page.locator("input[type='file'][accept*='image']").first
            attach.wait_for(state="attached", timeout=10_000)
            attach.set_input_files(image)
            self.pause(2.0, 3.5)
        box = self.try_selectors("page_status", self.STATUS_BOX, timeout_each=8_000)
        self.engine.type(page, box, text)
        btn = self.try_selectors("page_post_btn", self.POST_BUTTONS, timeout_each=8_000)
        self.engine.click(page, btn)
        self.pause(2.5, 4.0)
        self.log.info("✔ published on page %r", page_name)
