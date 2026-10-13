"""Bale module — Iranian messenger by Iran's Ministry of ICT.

Web app: https://web.bale.ai — first login via phone + code (typed in the
console by you), afterwards the persistent profile keeps the session.

UI notes (as of writing, verified on the web client):
  * search box        → input with class 'search-input' / placeholder 'Search'
  * conversation list → ul#chatlist-items
  * message input     → div[contenteditable] with class 'input-message-input'
Selectors are defined per-Bale-release; adjust after their UI updates.
"""

from typing import Optional

from platforms.base import BasePlatform


class Bale(BasePlatform):
    name = "bale"
    base_url = "https://web.bale.ai/"

    SEARCH_INPUT = [
        "input.search-input",
        "input[placeholder*='Search']",
        "input[placeholder*='جست']",
    ]
    CHAT_INPUT = [
        "div.input-message-input",
        "div[contenteditable='true'].input-message-input",
        "div[contenteditable='true'][role='textbox']",
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
        """Open the web app; you type the SMS code in this console."""
        page = self.open()
        if self.is_logged_in():
            self.log.info("already logged in (profile session)")
            return

        phone = phone or self.cfg.get("phone")
        if phone:
            sel = self.try_selectors("phone", [
                "input[name='phone_number']",
                "input[placeholder*='Phone']",
                "input[placeholder*='موبایل']",
            ], timeout_each=8_000)
            if sel:
                self.engine.type(page, sel, phone, secret=True)
                self.pause(0.4, 0.9)
                self.engine.press(page, "Enter")

        code = input("🔑 کد ورود بله را وارد کنید: ").strip()
        sel = self.try_selectors("code", [
            "input[autocomplete='one-time-code']",
            "input[name='login_code']",
        ], timeout_each=15_000)
        if not sel:
            self.shot("bale_code")
            raise RuntimeError("Bale: code input not found")
        self.engine.type(page, sel, code, secret=True)
        self.pause(2.0, 3.5)
        self.engine.export_session(self.page, "bale")
        self.log.info("✔ bale login finished")

    # ------------------------------------------------------------------ #
    def _open_chat(self, chat: str) -> None:
        page = self.page
        sel = self.try_selectors("search", self.SEARCH_INPUT, timeout_each=8_000)
        if not sel:
            self.shot("bale_search")
            raise RuntimeError("Bale: search box not found")
        self.engine.click(page, sel)
        self.engine.type(page, sel, chat)
        self.pause(1.2, 2.4)
        self.engine.press(page, "Enter")
        self.pause(0.8, 1.6)
        self.log.info("chat focused → %s", chat)

    def send_message(self, chat: str, text: str) -> None:
        self._open_chat(chat)
        page = self.page
        box = self.try_selectors("chat_input", self.CHAT_INPUT, timeout_each=8_000)
        if not box:
            self.shot("bale_input")
            raise RuntimeError("Bale: message input not found")
        self.engine.type(page, box, text)
        self.pause(0.3, 0.7)
        self.engine.press(page, "Enter")
        self.pause(0.8, 1.4)
        self.log.info("✔ پیام بله ارسال شد → %r", chat)
        self.toast("✅ پیام بله ارسال شد")

    def post_channel(self, channel: str, text: str) -> None:
        """Publish to a Bale channel where this account is an admin."""
        self.send_message(channel, text)

    def broadcast(self, chats: list, text: str) -> int:
        """Send the same message to several chats (simple campaign helper)."""
        sent = 0
        for chat in chats:
            try:
                self.send_message(chat, text)
                sent += 1
                self.pause(2.0, 4.0)        # spacing between messages
            except Exception as exc:
                self.log.warning("broadcast: %s failed → %s", chat, exc)
        self.log.info("✔ broadcast: %s/%s sent", sent, len(chats))
        return sent
