"""Rubika module — Iranian super-app (messenger + channels + payments).

Web app: https://web.rubika.ir — login via phone + code (you type the code
in this console; it is never stored). The persistent profile then keeps
you signed in.

Rubika's web client is a SPA that loads its bundle from rubika.ir; its
composer is a contenteditable div inside the chat pane.
"""

from typing import Optional

from platforms.base import BasePlatform


class Rubika(BasePlatform):
    name = "rubika"
    base_url = "https://web.rubika.ir/"

    SEARCH_INPUT = [
        "input[placeholder*='Search']",
        "input[placeholder*='جست']",
        "input[type='search']",
    ]
    CHAT_INPUT = [
        "div[contenteditable='true'][role='textbox']",
        "div[contenteditable='true']",
        "textarea[placeholder*='Message']",
    ]
    SEND_BUTTON = [
        "button[aria-label*='Send']",
        "button[aria-label*='ارسال']",
        "svg[class*='send']",
    ]

    # ------------------------------------------------------------------ #
    def is_logged_in(self) -> bool:
        try:
            self.page.goto(self.base_url, wait_until="domcontentloaded",
                           timeout=30_000)
        except Exception:
            pass
        self.pause(2.5, 3.5)
        return self.engine.exists("input[placeholder*='Search']",
                                  timeout=4_000)

    def login(self, phone: Optional[str] = None) -> None:
        page = self.open()
        if self.is_logged_in():
            self.log.info("already logged in (profile session)")
            return

        phone = phone or self.cfg.get("phone")
        if phone:
            sel = self.try_selectors("phone", [
                "input[name='phone']",
                "input[type='tel']",
                "input[placeholder*='Phone']",
                "input[placeholder*='موبایل']",
            ], timeout_each=8_000)
            if sel:
                self.engine.type(page, sel, phone, secret=True)
                self.pause(0.4, 0.9)
                self.engine.press(page, "Enter")

        code = input("🔑 کد ورود روبیکا را وارد کنید: ").strip()
        sel = self.try_selectors("code", [
            "input[autocomplete='one-time-code']",
            "input[name='code']",
        ], timeout_each=15_000)
        if not sel:
            self.shot("rubika_code")
            raise RuntimeError("Rubika: code input not found")
        self.engine.type(page, sel, code, secret=True)
        self.pause(2.5, 4.0)
        self.engine.export_session(self.page, "rubika")
        self.log.info("✔ rubika login finished")

    # ------------------------------------------------------------------ #
    def _open_chat(self, chat: str) -> None:
        page = self.page
        sel = self.try_selectors("search", self.SEARCH_INPUT, timeout_each=8_000)
        if not sel:
            self.shot("rubika_search")
            raise RuntimeError("Rubika: search box not found")
        self.engine.click(page, sel)
        self.engine.type(page, sel, chat)
        self.pause(1.5, 2.5)
        self.engine.press(page, "ArrowDown")
        self.pause(0.2, 0.5)
        self.engine.press(page, "Enter")
        self.pause(1.0, 1.8)
        self.log.info("chat focused → %s", chat)

    def send_message(self, chat: str, text: str) -> None:
        self._open_chat(chat)
        page = self.page
        box = self.try_selectors("chat_input", self.CHAT_INPUT, timeout_each=8_000)
        if not box:
            self.shot("rubika_input")
            raise RuntimeError("Rubika: message input not found")
        self.engine.type(page, box, text)
        self.pause(0.3, 0.7)
        send = self.try_selectors("send", self.SEND_BUTTON, timeout_each=4_000)
        if send:
            self.engine.click(page, send)
        else:
            self.engine.press(page, "Enter")
        self.pause(0.8, 1.4)
        self.log.info("✔ پیام روبیکا ارسال شد → %r", chat)
        self.toast("✅ پیام روبیکا ارسال شد")

    def post_channel(self, channel: str, text: str) -> None:
        """Publish to one of your Rubika channels."""
        self.send_message(channel, text)
