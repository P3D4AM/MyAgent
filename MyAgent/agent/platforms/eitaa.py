"""Eitaa module — Iranian channel-centric messenger.

Web app: https://web.eitaa.com — QR or phone login; afterwards the
persistent profile keeps the session.
"""

from typing import Optional

from platforms.base import BasePlatform


class Eitaa(BasePlatform):
    name = "eitaa"
    base_url = "https://web.eitaa.com/"

    SEARCH_INPUT = [
        "input[placeholder*='Search']",
        "input[placeholder*='جست']",
        "input[type='search']",
    ]
    CHAT_INPUT = [
        "div[contenteditable='true']",
        "textarea.input-message-input",
    ]

    # ------------------------------------------------------------------ #
    def is_logged_in(self) -> bool:
        try:
            self.page.goto(self.base_url, wait_until="domcontentloaded",
                           timeout=30_000)
        except Exception:
            pass
        self.pause(2.0, 3.0)
        return self.engine.exists("div[contenteditable='true']", timeout=4_000)

    def login(self, phone: Optional[str] = None) -> None:
        page = self.open()
        if self.is_logged_in():
            self.log.info("already logged in (profile session)")
            return

        phone = phone or self.cfg.get("phone")
        if phone:
            sel = self.try_selectors("phone", [
                "input[name='phone_number']",
                "input[type='tel']",
            ], timeout_each=8_000)
            if sel:
                self.engine.type(page, sel, phone, secret=True)
                self.pause(0.4, 0.9)
                self.engine.press(page, "Enter")

        code = input("🔑 کد ورود ایتا را وارد کنید: ").strip()
        sel = self.try_selectors("code", [
            "input[autocomplete='one-time-code']",
            "input[name='login_code']",
        ], timeout_each=15_000)
        if not sel:
            self.shot("eitaa_code")
            raise RuntimeError("Eitaa: code input not found")
        self.engine.type(page, sel, code, secret=True)
        self.pause(2.0, 3.5)
        self.engine.export_session(self.page, "eitaa")
        self.log.info("✔ eitaa login finished")

    # ------------------------------------------------------------------ #
    def send_message(self, chat: str, text: str) -> None:
        page = self.page
        sel = self.try_selectors("search", self.SEARCH_INPUT, timeout_each=8_000)
        if not sel:
            self.shot("eitaa_search")
            raise RuntimeError("Eitaa: search box not found")
        self.engine.click(page, sel)
        self.engine.type(page, sel, chat)
        self.pause(1.2, 2.4)
        self.engine.press(page, "Enter")
        self.pause(0.8, 1.6)
        box = self.try_selectors("chat_input", self.CHAT_INPUT, timeout_each=8_000)
        if not box:
            self.shot("eitaa_input")
            raise RuntimeError("Eitaa: message input not found")
        self.engine.type(page, box, text)
        self.pause(0.3, 0.7)
        self.engine.press(page, "Enter")
        self.pause(0.8, 1.4)
        self.log.info("✔ پیام ایتا ارسال شد → %r", chat)
        self.toast("✅ پیام ایتا ارسال شد")

    def post_channel(self, channel: str, text: str) -> None:
        self.send_message(channel, text)
