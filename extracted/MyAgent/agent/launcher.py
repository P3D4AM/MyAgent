#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ParsAgent Launcher — لانچر گرافیکی نصب و اجرا
====================================================

این همان «دکمهٔ روشن/خاموش» پارس‌ایجنت است:

  ۱) بازش کن (دابل‌کلیک روی ParsAgent.bat یا اجرای python launcher.py)
  ۲) دکمهٔ «نصب پیش‌نیازها» فقط بار اول لازم است
  ۳) دکمهٔ «اجرای سرور» را بزن → سرور مح بالا می‌آید و پنل کنترل
     به‌صورت خودکار در مرورگر باز می‌شود (http://127.0.0.1:8765)

سرور فقط روی همین سیستم در دسترس است؛ هیچ داده‌ای جایی ارسال نمی‌شود.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path
from tkinter import BOTH, BOTTOM, END, LEFT, RIGHT, X, messagebox, scrolledtext
import tkinter as tk

BASE = Path(__file__).resolve().parent
HOST, PORT = "127.0.0.1", 8765
PANEL_URL = f"http://{HOST}:{PORT}"
HEALTH_URL = f"{PANEL_URL}/api/health"

# ماژول‌هایی که سرور پنل و ایجنت لازم دارند (نامِ پکیج pip ≠ نامِ ماژول)
REQUIRED = {
    "fastapi": "سرور وب پنل",
    "uvicorn": "اجرای سرور",
    "playwright": "اتوماسیون مرورگر",
    "pyautogui": "کنترل موس و کیبورد",
    "pynput": "ضبط موس و کیبورد",
    "rich": "لاگ رنگی",
    "plyer": "اعلان ویندوز",
    "PIL": "اسکرین‌شات و تصویر",
    "psutil": "اطلاعات سیستم",
    "pyperclip": "تایپ متن فارسی",
}

NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

COLORS = {
    "bg": "#0b1220", "panel": "#111a2c", "card": "#16213a",
    "line": "#243356", "fg": "#dbe4f0", "muted": "#8fa3c0",
    "acc": "#10b981", "acc2": "#34d399", "warn": "#f59e0b", "err": "#f43f5e",
    "sky": "#38bdf8", "log_bg": "#060b16",
}
TAG_COLORS = {
    "ts": "#475569", "srv": "#7dd3fc", "pip": "#c4b5fd", "ok": "#34d399",
    "warn": "#fbbf24", "err": "#fb7185", "info": "#cbd5e1",
}


def _findable(name: str) -> bool:
    """آیا ماژول قابل ایمپورت است؟ (مقاوم به ماژول‌های بی-spec)"""
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return name in sys.modules


def check_missing() -> list:
    return [m for m in REQUIRED if not _findable(m)]


def server_up(timeout: float = 1.0) -> bool:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ParsAgent — لانچر")
        self.geometry("800x620")
        self.minsize(700, 540)
        self.configure(bg=COLORS["bg"])

        self.proc: subprocess.Popen | None = None
        self.installing = False
        self.stop_flag = False

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(200, self.on_start)

    # ------------------------------------------------------------------ #
    # UI
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        # --- هدر
        header = tk.Frame(self, bg="#080e1a")
        header.pack(fill=X)
        tk.Label(header, text="🤖 ParsAgent", font=("Segoe UI", 21, "bold"),
                 bg="#080e1a", fg=COLORS["acc"]).pack(anchor="e", padx=18,
                                                      pady=(14, 0))
        tk.Label(header, text="لانچر نصب و اجرای پنل کنترل — نسخه ۱.۱",
                 font=("Segoe UI", 10), bg="#080e1a",
                 fg=COLORS["muted"]).pack(anchor="e", padx=18, pady=(0, 14))

        # --- نوار وضعیت
        status_bar = tk.Frame(self, bg=COLORS["panel"])
        status_bar.pack(fill=X, padx=14, pady=(12, 6))
        self.status_dot = tk.Label(status_bar, text="●", font=("Segoe UI", 12),
                                    bg=COLORS["panel"], fg=COLORS["muted"])
        self.status_dot.pack(side=RIGHT, padx=10, pady=8)
        self.status_lbl = tk.Label(status_bar, text="در حال بررسی وضعیت…",
                                   font=("Segoe UI", 11, "bold"),
                                   bg=COLORS["panel"], fg=COLORS["fg"])
        self.status_lbl.pack(side=RIGHT)
        self.link_lbl = tk.Label(status_bar, text=PANEL_URL,
                                 font=("Segoe UI", 10, "underline"),
                                 bg=COLORS["panel"], fg=COLORS["sky"],
                                 cursor="hand2")
        self.link_lbl.pack(side=LEFT, padx=10, pady=8)
        self.link_lbl.bind("<Button-1>", lambda e: self.open_panel())

        # --- دکمه‌های اصلی
        btns = tk.Frame(self, bg=COLORS["bg"])
        btns.pack(fill=X, padx=14, pady=6)
        self.btn_run = self._big_button(btns, "🚀  اجرای سرور", self.start_server,
                                        bg=COLORS["acc"], fg="#04120c",
                                        font=("Segoe UI", 13, "bold"))
        self.btn_run.pack(side=RIGHT, fill=X, expand=True, padx=(0, 8), ipady=10)
        self.btn_panel = self._big_button(btns, "🌐  باز کردن پنل", self.open_panel,
                                          bg=COLORS["card"], fg=COLORS["fg"])
        self.btn_panel.pack(side=RIGHT, fill=X, expand=True, padx=8, ipady=10)
        self.btn_stop = self._big_button(btns, "⛔  توقف سرور", self.stop_server,
                                         bg=COLORS["card"], fg=COLORS["fg"])
        self.btn_stop.pack(side=RIGHT, fill=X, expand=True, padx=8, ipady=10)

        # --- دکمه‌های ابزار
        tools = tk.Frame(self, bg=COLORS["bg"])
        tools.pack(fill=X, padx=14, pady=(2, 8))
        self.btn_install = self._tool_button(tools, "📦  نصب پیش‌نیازها",
                                              self.install_deps,
                                              bg="#1d2c1f", fg=COLORS["acc2"])
        self.btn_install.pack(side=RIGHT, padx=(0, 8))
        self.btn_pw = self._tool_button(tools, "🧭  نصب کرومیوم (آینه)",
                                        self.install_browser,
                                        bg=COLORS["card"], fg=COLORS["fg"])
        self.btn_pw.pack(side=RIGHT, padx=8)
        self.btn_clear = self._tool_button(tools, "🧹  پاک‌سازی لاگ",
                                           self.clear_log,
                                           bg=COLORS["card"], fg=COLORS["muted"])
        self.btn_clear.pack(side=RIGHT, padx=8)

        # --- جعبه لاگ
        self.txt = scrolledtext.ScrolledText(
            self, bg=COLORS["log_bg"], fg=COLORS["fg"], relief="flat",
            font=("Consolas", 9), state="disabled", wrap="word", borderwidth=0)
        self.txt.pack(fill=BOTH, expand=True, padx=14, pady=(2, 8))
        for tag, color in TAG_COLORS.items():
            self.txt.tag_configure(tag, foreground=color)

        # --- فوتر
        footer = tk.Frame(self, bg="#080e1a")
        footer.pack(fill=X, side=BOTTOM)
        tk.Label(footer,
                 text="سرور فقط روی همین سیستم (127.0.0.1) در دسترس است — "
                      "نیازی به اینترنت ندارد",
                 font=("Segoe UI", 9), bg="#080e1a",
                 fg=COLORS["muted"]).pack(side=RIGHT, padx=14, pady=8)
        self.ws_dot = tk.Label(footer, text="○ پنل: بسته", font=("Segoe UI", 9),
                               bg="#080e1a", fg=COLORS["muted"])
        self.ws_dot.pack(side=LEFT, padx=14, pady=8)

        self.set_running(False, unknown=True)

    def _big_button(self, parent, text, cmd, bg, fg, font=("Segoe UI", 11)):
        b = tk.Label(parent, text=text, bg=bg, fg=fg, font=font,
                     cursor="hand2", padx=14, pady=6)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.config(
            bg=COLORS["acc2"] if bg == COLORS["acc"] else "#1c2a4a"))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def _tool_button(self, parent, text, cmd, bg, fg):
        b = tk.Label(parent, text=text, bg=bg, fg=fg, font=("Segoe UI", 10),
                     cursor="hand2", padx=12, pady=6)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.config(bg="#1c2a4a"))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    # ------------------------------------------------------------------ #
    # لاگ
    # ------------------------------------------------------------------ #
    def log(self, kind: str, msg: str):
        ts = time.strftime("%H:%M:%S")
        self.txt.configure(state="normal")
        self.txt.insert(END, f"[{ts}] ", "ts")
        self.txt.insert(END, (msg or "") + "\n", kind if kind in TAG_COLORS else "info")
        self.txt.see(END)
        self.txt.configure(state="disabled")

    def clear_log(self):
        self.txt.configure(state="normal")
        self.txt.delete("1.0", END)
        self.txt.configure(state="disabled")

    def set_status(self, text: str, color: str):
        self.status_lbl.config(text=text, fg=color)
        self.status_dot.config(fg=color)

    def set_running(self, running: bool, unknown: bool = False):
        if unknown:
            self.set_status("در حال بررسی…", COLORS["muted"])
            return
        if running:
            self.btn_run.config(fg="#3f7c66")
            self.btn_stop.config(fg=COLORS["err"])
            self.btn_panel.config(fg=COLORS["sky"])
            self.ws_dot.config(text="● پنل: روشن", fg=COLORS["acc"])
            self.set_status("سرور در حال اجرا — پنل آماده است", COLORS["acc"])
        else:
            self.btn_run.config(fg=COLORS["fg"])
            self.btn_stop.config(fg=COLORS["muted"])
            self.btn_panel.config(fg=COLORS["muted"])
            self.ws_dot.config(text="○ پنل: بسته", fg=COLORS["muted"])
            self.set_status("سرور خاموش است", COLORS["muted"])

    # ------------------------------------------------------------------ #
    # شروع
    # ------------------------------------------------------------------ #
    def on_start(self):
        self.log("info", "به لانچر پارس‌ایجنت خوش آمدی 👋")
        self.log("info", f"پوشه پروژه: {BASE}")
        missing = check_missing()
        if missing:
            names = "، ".join(
                f"{m} ({REQUIRED[m]})" for m in missing)
            self.log("warn", f"ماژول‌های نصب‌نشده: {names}")
            self.set_status(f"نیاز به نصب: {len(missing)} ماژول", COLORS["warn"])
            self.after(400, lambda: self._ask_install(missing))
        else:
            self.log("ok", "همه پیش‌نیازها نصب هستند ✓")
            self.set_running(False)
            if server_up(0.6):
                self.log("ok", "سرور از قبل روشن است — پنل در دسترس است")
                self.set_running(True)

    def _ask_install(self, missing):
        if messagebox.askyesno(
                "نصب پیش‌نیازها",
                "برای اجرای پنل چند پکیج لازم است:\n\n"
                + "\n".join(f"• {m} — {REQUIRED[m]}" for m in missing)
                + "\n\nهم‌اکنون نصب شوند؟ (به اینترنت نیاز دارد)"):
            self.install_deps()
        else:
            self.log("warn", "بدون این ماژول‌ها سرور اجرا نمی‌شود")

    # ------------------------------------------------------------------ #
    # نصب
    # ------------------------------------------------------------------ #
    def _run_async(self, cmd, env=None, on_done=None, cwd=None):
        def work():
            try:
                p = subprocess.Popen(
                    cmd, cwd=str(cwd or BASE),
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace",
                    env=env or os.environ, creationflags=NO_WINDOW)
                for line in p.stdout:
                    self.after(0, lambda l=line: self.log("pip", l.rstrip()))
                code = p.wait()
                self.after(0, lambda: on_done(code == 0) if on_done else None)
            except Exception as exc:
                self.after(0, lambda: self.log("err", f"خطا: {exc}"))
                self.after(0, lambda: on_done(False) if on_done else None)
        threading.Thread(target=work, daemon=True).start()

    def install_deps(self):
        if self.installing:
            return
        if self.proc and self.proc.poll() is None:
            messagebox.showwarning("در حال اجرا",
                                   "اول سرور را متوقف کن، بعد نصب را بزن")
            return
        self.installing = True
        self.set_status("در حال نصب پیش‌نیازها…", COLORS["sky"])
        self.log("info", "شروع نصب پیش‌نیازها (ممکن است چند دقیقه طول بکشد)…")
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        self._run_async(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            env=env, on_done=self._after_install)

    def _after_install(self, ok: bool):
        self.installing = False
        missing = check_missing()
        if not missing:
            self.log("ok", "نصب کامل شد ✓ — حالا «اجرای سرور» را بزن")
            self.set_running(False)
            if messagebox.askyesno("نصب کامل",
                                   "همه پیش‌نیازها نصب شد ✓\n\nسرور الان اجرا شود؟"):
                self.start_server()
        else:
            self.log("err", "بعضی ماژول‌ها هنوز نصب نشده‌اند: "
                     + "، ".join(missing))
            self.set_status("نصب ناقص", COLORS["err"])

    def install_browser(self):
        """نصب کرومیوم Playwright از آینهٔ چینی (بدون فیلترشکن).

        فقط وقتی لازم است که نه Edge داشته باشی نه Chrome —
        لانچر مقاوم خودکار اول از مرورگرهای نصب‌شده استفاده می‌کند.
        """
        if messagebox.askyesno(
                "نصب کرومیوم",
                "کرومیوم باندل Playwright از آینهٔ npmmirror دانلود شود؟\n\n"
                "نکته: اگر روی ویندوزت Edge یا Chrome نصب است،\n"
                "این مرحله اصلاً لازم نیست — ایجنت خودش از همان‌ها استفاده می‌کند."):
            mirror = "https://cdn.npmmirror.com/binaries/playwright"
            env = {**os.environ, "PLAYWRIGHT_DOWNLOAD_HOST": mirror,
                   "PYTHONIOENCODING": "utf-8"}
            self.log("info", f"نصب کرومیوم از آینه: {mirror}")
            self._run_async(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                env=env, on_done=lambda ok: self.log(
                    "ok" if ok else "err",
                    "نصب کرومیوم تمام شد ✓" if ok
                    else "نصب کرومیوم ناموفق بود — لاگ بالا را ببین"))

    # ------------------------------------------------------------------ #
    # اجرای سرور
    # ------------------------------------------------------------------ #
    def start_server(self):
        if self.proc and self.proc.poll() is None:
            self.log("info", "سرور از قبل در حال اجراست — پنل باز می‌شود")
            webbrowser.open(PANEL_URL)
            return
        if server_up(0.8):
            self.log("info", "یک نسخه از سرور روی پورت در حال اجراست — پنل باز می‌شود")
            self.set_running(True)
            webbrowser.open(PANEL_URL)
            return
        if check_missing():
            if messagebox.askyesno(
                    "نصب نشده",
                    "بعضی پیش‌نیازها نصب نیستند.\nهم‌اکنون نصب شوند؟"):
                self.install_deps()
            return

        self.log("info", f"راه‌اندازی سرور پنل روی {PANEL_URL} …")
        self.set_status("در حال راه‌اندازی سرور…", COLORS["sky"])
        env = {**os.environ, "PYTHONIOENCODING": "utf-8",
               "NO_COLOR": "1", "PYTHONPATH": str(BASE)}
        try:
            self.proc = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "server:app",
                 "--host", HOST, "--port", str(PORT), "--log-level", "info"],
                cwd=str(BASE), stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                errors="replace", env=env, creationflags=NO_WINDOW)
        except Exception as exc:
            self.log("err", f"اجرای سرور ناموفق: {exc}")
            self.set_running(False)
            return

        threading.Thread(target=self._pipe_logs, daemon=True).start()
        threading.Thread(target=self._wait_until_up, daemon=True).start()

    def _pipe_logs(self):
        proc = self.proc
        if not proc or not proc.stdout:
            return
        for line in proc.stdout:
            if self.stop_flag:
                break
            self.after(0, lambda l=line: self.log("srv", l.rstrip()))
        code = proc.wait()
        self.after(0, lambda: (
            self.set_running(False),
            self.log("warn", f"پروسهٔ سرور تمام شد (کد {code})")))

    def _wait_until_up(self):
        for _ in range(120):                        # حداکثر ~۶۰ ثانیه
            if self.proc and self.proc.poll() is not None:
                return
            if server_up(0.8):
                self.after(0, self._on_server_up)
                return
            time.sleep(0.5)
        self.after(0, lambda: self.log(
            "err", "سرور در ۶۰ ثانیه پاسخ نداد — خطاهای بالا را ببین"))

    def _on_server_up(self):
        self.log("ok", f"سرور آماده است ✓ — باز کردن پنل: {PANEL_URL}")
        self.set_running(True)
        self.after(500, lambda: webbrowser.open(PANEL_URL))

    def stop_server(self):
        if not (self.proc and self.proc.poll() is None):
            self.log("info", "سرور در حال اجرا نیست")
            return
        self.log("warn", "در حال توقف سرور (مرورگرهای باز هم بسته می‌شوند)…")
        try:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(self.proc.pid)],
                    capture_output=True, creationflags=NO_WINDOW)
            else:
                self.proc.terminate()
        except Exception as exc:
            self.log("err", f"توقف ناموفق: {exc}")

    def open_panel(self):
        if server_up(0.8):
            webbrowser.open(PANEL_URL)
        else:
            messagebox.showinfo("سرور خاموش است",
                                "اول دکمهٔ «اجرای سرور» را بزن")

    # ------------------------------------------------------------------ #
    def on_close(self):
        if self.proc and self.proc.poll() is None:
            if messagebox.askyesno(
                    "سرور در حال اجراست",
                    "با بستن لانچر، سرور و پنل هم خاموش شوند؟",
                    icon="question"):
                self.stop_flag = True
                self.stop_server()
        self.destroy()


def main() -> None:
    Launcher().mainloop()


if __name__ == "__main__":
    main()
