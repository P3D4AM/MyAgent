"""Twitter / X module — tweet, quote, DM, follow, like, retweet."""

from typing import Optional

from platforms.base import BasePlatform


class Twitter(BasePlatform):
    name = "twitter"
    base_url = "https://twitter.com/"

    COMPOSE_URL = "https://twitter.com/compose/post"
    TWEET_BOX = [
        "div[data-testid='tweetTextarea_0']",
        "div[data-testid='tweetTextarea_0RichTextInputContainer'] div[role='textbox']",
    ]
    TWEET_BUTTON = ["button[data-testid='tweetButton']", "button[data-testid='tweetButtonInline']"]
    FILE_INPUT = ["input[data-testid='fileInput']"]
    USER_URL = "https://twitter.com/{username}"
    DM_URL = "https://twitter.com/messages/compose"

    # ------------------------------------------------------------------ #
    def is_logged_in(self) -> bool:
        return self.engine.exists("a[data-testid='AppTabBar_Home_Link']", timeout=5_000)

    def login(self, username: Optional[str] = None,
              password: Optional[str] = None) -> None:
        username = username or self.cfg.get("username")
        password = password or self.cfg.get("password")
        if not username or not password:
            raise RuntimeError("platforms.twitter.username/password not set")

        page = self.open()
        self.engine.type(page, "input[autocomplete='username']", username)
        self.pause(0.4, 0.9)
        self.engine.press(page, "Enter")
        self.pause(1.0, 2.0)
        self.engine.type(page, "input[type='password']", password, secret=True)
        self.pause(0.4, 0.9)
        self.engine.press(page, "Enter")
        self.pause(2.5, 4.0)
        self.engine.export_session(self.page, "twitter")
        self.log.info("✔ twitter login flow finished")

    # ------------------------------------------------------------------ #
    def post_tweet(self, text: str, image: Optional[str] = None) -> None:
        page = self.page
        page.goto(self.COMPOSE_URL, wait_until="domcontentloaded")
        box = self.try_selectors("tweet_box", self.TWEET_BOX, timeout_each=8_000)
        if not box:
            self.shot("tw_no_box")
            raise RuntimeError("Twitter: composer box not found")
        self.engine.type(page, box, text)
        self.pause(0.6, 1.2)

        if image:
            file_input = page.locator(self.FILE_INPUT[0]).first
            file_input.wait_for(state="attached", timeout=10_000)
            file_input.set_input_files(image)
            self.log.info("media attached → %s", image)
            self.pause(1.5, 3.0)          # wait for the preview thumbnail

        btn = self.try_selectors("tweet_button", self.TWEET_BUTTON,
                                 timeout_each=8_000)
        if not btn:
            self.shot("tw_no_button")
            raise RuntimeError("Twitter: tweet button not found")
        self.engine.click(page, btn)
        self.pause(2.0, 3.5)
        self.log.info("✔ tweet posted (%s chars%s)",
                      len(text), " +image" if image else "")
        self.toast("🐦 توییت منتشر شد")

    def send_dm(self, username: str, message: str) -> None:
        page = self.page
        page.goto(self.DM_URL, wait_until="domcontentloaded")
        self.pause(1.5, 2.5)
        # type the recipient in the "To" search of the compose dialog
        search = self.try_selectors("dm_to", [
            "input[data-testid='searchInput']",
            "input[placeholder*='People']",
            "input[aria-label*='To']",
        ])
        if not search:
            self.shot("tw_dm_to")
            raise RuntimeError("Twitter: DM recipient box not found")
        self.engine.type(page, search, username)
        self.pause(1.0, 2.0)
        self.engine.press(page, "Enter")
        self.pause(0.8, 1.4)
        chat = self.try_selectors("dm_box", [
            "div[data-testid='dmComposerTextInput'] div[role='textbox']",
            "textarea[placeholder*='Start a new message']",
        ])
        if not chat:
            self.shot("tw_dm_box")
            raise RuntimeError("Twitter: DM textbox not found")
        self.engine.type(page, chat, message)
        self.pause(0.4, 0.8)
        send = self.try_selectors("dm_send", [
            "button[data-testid='dmComposerSendButton']",
            "div[data-testid='dmComposerSendButton']",
        ])
        if send:
            self.engine.click(page, send)
        else:
            self.engine.press(page, "Enter")
        self.pause(1.0, 1.8)
        self.log.info("✔ DM sent to @%s", username)

    def follow(self, username: str) -> None:
        page = self.page
        page.goto(self.USER_URL.format(username=username),
                  wait_until="domcontentloaded")
        self.pause(1.2, 2.2)
        follow_btn = self.try_selectors("follow", [
            "div[data-testid='placementTracking'] div[role='button']:has-text('Follow')",
            "button:has-text('Follow')",
            "div[role='button']:has-text('دنبال کردن')",
        ])
        if not follow_btn:
            self.log.warning("follow: no Follow button for @%s (already following?)",
                             username)
            return
        self.engine.click(page, follow_btn)
        self.pause(0.8, 1.6)
        self.log.info("✔ followed @%s", username)

    def like(self, post_url: str) -> None:
        page = self.page
        page.goto(post_url, wait_until="domcontentloaded")
        self.pause(1.5, 2.5)
        like = self.try_selectors("like", [
            "div[data-testid='like']",
            "button[data-testid='like']",
        ])
        if not like:
            self.log.warning("like: heart not found (already liked?)")
            return
        self.engine.click(page, like)
        self.pause(0.8, 1.6)
        self.log.info("✔ liked %s", post_url)

    def retweet(self, post_url: str) -> None:
        page = self.page
        page.goto(post_url, wait_until="domcontentloaded")
        self.pause(1.5, 2.5)
        rt = self.try_selectors("rt", [
            "button[data-testid='retweet']",
            "div[data-testid='retweet']",
        ])
        if not rt:
            self.shot("tw_rt")
            raise RuntimeError("Twitter: retweet button not found")
        self.engine.click(page, rt)
        self.pause(0.5, 1.0)
        confirm = self.try_selectors("rt_confirm", [
            "a[data-testid='retweetConfirm']",
            "div[data-testid='retweetConfirm']",
        ])
        if confirm:
            self.engine.click(page, confirm)
        self.pause(1.0, 1.8)
        self.log.info("✔ retweeted %s", post_url)
