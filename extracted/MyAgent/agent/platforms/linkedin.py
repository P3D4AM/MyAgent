"""LinkedIn module — feed posts, articles, connections and DMs."""

from typing import Optional

from platforms.base import BasePlatform


class LinkedIn(BasePlatform):
    name = "linkedin"
    base_url = "https://www.linkedin.com/"

    START_POST = [
        "button[aria-label*='Start a post']",
        "button[aria-label*='شروع یک پست']",
        "button:has-text('Start a post')",
    ]
    SHARE_BOX = [
        "div[role='textbox'][contenteditable='true'][aria-label*='What do you want to talk about']",
        "div[role='textbox'][contenteditable='true']",
    ]
    POST_BUTTON = [
        "button:has-text('Post')",
        "button:has-text('انتشار')",
        "button.share-actions__primary-action",
    ]
    MESSAGE_BOX = [
        "div[role='textbox'][contenteditable='true'][aria-label*='Write a message']",
        "div.msg-form__contenteditable[contenteditable='true']",
    ]

    # ------------------------------------------------------------------ #
    def is_logged_in(self) -> bool:
        return self.engine.exists("button[aria-label*='Me']", timeout=5_000)

    def login(self, email: Optional[str] = None, password: Optional[str] = None) -> None:
        email = email or self.cfg.get("email")
        password = password or self.cfg.get("password")
        if not email or not password:
            raise RuntimeError("platforms.linkedin.email/password not set")

        page = self.open()
        self.engine.type(page, "#session_key", email)
        self.pause(0.4, 0.9)
        self.engine.type(page, "#session_password", password, secret=True)
        self.pause(0.4, 0.9)
        self.engine.press(page, "Enter")
        self.pause(3.0, 5.0)
        # 2FA (if enabled)
        if self.engine.exists("input[name='pin']", timeout=6_000):
            pin = input("🔑 LinkedIn verification code: ").strip()
            self.engine.type(page, "input[name='pin']", pin, secret=True)
            self.pause(0.4, 0.8)
            self.engine.press(page, "Enter")
            self.pause(2.5, 4.0)
        self.engine.export_session(self.page, "linkedin")
        self.log.info("✔ linkedin login flow finished")

    # ------------------------------------------------------------------ #
    def post(self, text: str, image: Optional[str] = None) -> None:
        page = self.page
        page.goto(self.base_url + "feed/", wait_until="domcontentloaded")
        self.pause(2.0, 3.5)

        start = self.try_selectors("start_post", self.START_POST, timeout_each=8_000)
        if not start:
            self.shot("li_start")
            raise RuntimeError("LinkedIn: 'Start a post' not found")
        self.engine.click(page, start)
        self.pause(1.5, 2.5)

        if image:
            attach = page.locator("input[type='file'][accept*='image']").first
            attach.wait_for(state="attached", timeout=10_000)
            attach.set_input_files(image)
            self.log.info("media attached → %s", image)
            self.pause(2.0, 3.5)

        box = self.try_selectors("share_box", self.SHARE_BOX, timeout_each=8_000)
        if not box:
            self.shot("li_box")
            raise RuntimeError("LinkedIn: share box not found")
        self.engine.type(page, box, text)
        self.pause(0.8, 1.6)

        btn = self.try_selectors("post_btn", self.POST_BUTTON, timeout_each=8_000)
        if not btn:
            self.shot("li_btn")
            raise RuntimeError("LinkedIn: post button not found")
        self.engine.click(page, btn)
        self.pause(3.0, 5.0)
        self.log.info("✔ linkedin post published (%s chars)", len(text))
        self.toast("💼 پست لینکدین منتشر شد")

    def connect(self, profile_url: str, note: str = "") -> None:
        page = self.page
        page.goto(profile_url, wait_until="domcontentloaded")
        self.pause(2.0, 3.0)
        connect = self.try_selectors("connect", [
            "button[aria-label*='Connect']",
            "button:has-text('اتصال')",
        ])
        if not connect:
            self.log.warning("connect: no Connect button (already connected?)")
            return
        self.engine.click(page, connect)
        self.pause(1.0, 2.0)
        if note:
            box = self.try_selectors("connect_note", [
                "textarea[id*='connect-cta-textarea']",
                "textarea[placeholder*='Add a note']",
                "textarea[placeholder*='یادداشت']",
            ])
            if box:
                self.engine.type(page, box, note)
                self.pause(0.5, 1.0)
        send = self.try_selectors("connect_send", [
            "button[aria-label*='Send now']",
            "button:has-text('ارسال')",
        ])
        if send:
            self.engine.click(page, send)
        self.pause(1.5, 2.5)
        self.log.info("✔ connection request → %s", profile_url)

    def send_dm(self, profile_url: str, message: str) -> None:
        page = self.page
        page.goto(profile_url, wait_until="domcontentloaded")
        self.pause(2.0, 3.0)
        msg_btn = self.try_selectors("message", [
            "button[aria-label*='Message']",
            "button:has-text('پیام')",
        ])
        if not msg_btn:
            self.shot("li_dm")
            raise RuntimeError("LinkedIn: message button not found")
        self.engine.click(page, msg_btn)
        self.pause(1.5, 2.5)
        box = self.try_selectors("dm_box", self.MESSAGE_BOX, timeout_each=8_000)
        if not box:
            self.shot("li_dm_box")
            raise RuntimeError("LinkedIn: DM box not found")
        self.engine.type(page, box, message)
        self.pause(0.4, 0.9)
        self.engine.press(page, "Enter")
        self.pause(1.0, 1.8)
        self.log.info("✔ DM sent → %s", profile_url)
