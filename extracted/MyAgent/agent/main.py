#!/usr/bin/env python3
"""ParsAgent — Windows automation agent
=====================================

یک ایجنت اتوماسیون برای ویندوز که:
  • موس و کیبورد واقعی را کنترل می‌کند (PyAutoGUI)
  • ورودی‌ها را ضبط و بازپخش می‌کند (pynput ماکرو)
  • وب‌سایت‌ها را در سطح کد و بدون دخالت موس/کیبورد اتومیت می‌کند (Playwright)
  • برای شبکه‌های اجتماعی (اینستاگرام، توییتر، تلگرام، فیسبوک، لینکدین،
    بله، روبیکا، ایتا) ماژول آماده دارد

Usage:
    python main.py platforms                     # فهرست پلتفرم‌ها
    python main.py install                       # نصب کرومیوم از آینه (رفع 403)
    python main.py login <platform>              # ورود اول + ذخیره سشن
    python main.py run tasks/examples.json -t post_instagram_photo
    python main.py record -o macros/my.json      # ضبط ماکرو (F9 پایان)
    python main.py play macros/my.json -s 1.5    # بازپخش با سرعت ×۱.۵
    python main.py schedule tasks/examples.json -t morning_routine --every 30m
    python main.py demo                          # دموی سریع موتور مرورگر
    python main.py gateway                       # اتصال به پنل کنترل وب

مرورگر: لانچر مقاوم اول Edge ویندوز (msedge) را امتحان می‌کند، بعد Chrome،
و در نهایت کرومیوم باندل Playwright — پس روی ویندوز ۱۰/۱۱ حتی بدون
`playwright install` هم کار می‌کند.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from core.browser_engine import BrowserEngine          # noqa: E402
from core.gateway_client import GatewayClient          # noqa: E402
from core.input_recorder import InputRecorder, MacroPlayer  # noqa: E402
from core.logger import get_logger                     # noqa: E402
from core.scheduler import Scheduler                   # noqa: E402
from core.system_controller import SystemController    # noqa: E402
from core.task_engine import TaskEngine                # noqa: E402
from platforms import PLATFORMS                        # noqa: E402

log = get_logger("main")
console = Console()
CONFIG_PATH = ROOT / "config.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        example = {
            "browser": {"headless": False, "user_data_dir": "data/profiles/main",
                        "user_agent": None, "proxy": None, "slow_mo_ms": 0,
                        "channel": None,
                        "channel_fallbacks": ["msedge", "chrome", "chromium"]},
            "human": {"enabled": True, "min_delay_s": 0.35, "max_delay_s": 1.4,
                      "typing_delay_ms": [35, 95]},
            "platforms": {},
            "gateway": {"enabled": False, "url": "ws://127.0.0.1:3030",
                       "token": "change-me"},
        }
        CONFIG_PATH.write_text(json.dumps(example, ensure_ascii=False, indent=2),
                               encoding="utf-8")
        log.warning("config.json created from defaults — edit it now")
        return example
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def build_engines(config: dict, headless=None):
    """Wire the object graph: engines + platforms + task engine."""
    def browser_factory():
        # lazy: کانتکست مرورگر دقیقاً وقتی باز می‌شود که اولین گام پلتفرمی اجرا شود؛
        # هر پلتفرم پروفایل ماندگار خودش را می‌گیرد (data/profiles/<platform>)
        return BrowserEngine(config).start(headless=headless, lazy=True)
    desktop = SystemController(
        human=config.get("human", {}).get("enabled", True),
    )
    engine = TaskEngine(config, browser_factory, desktop, PLATFORMS)
    return engine


# ---------------------------------------------------------------------- #
# commands
# ---------------------------------------------------------------------- #
def cmd_platforms(args) -> None:
    table = Table(title="🌐 پلتفرم‌های پشتیبانی‌شده")
    table.add_column("پلتفرم", style="green")
    table.add_column("کلاس ماژول", style="cyan")
    table.add_column("نشانی وب")
    for name, cls in PLATFORMS.items():
        table.add_row(name, cls.__name__, cls.base_url)
    console.print(table)


def cmd_login(args) -> None:
    config = load_config()
    if args.platform not in PLATFORMS:
        console.print(f"[red]پلتفرم ناشناخته: {args.platform}[/red]")
        sys.exit(1)
    # هر پلتفرم پروفایل ماندگار خودش را دارد → data/profiles/<platform>
    engine = BrowserEngine(config).start(headless=False, profile=args.platform)
    try:
        mod = PLATFORMS[args.platform](engine, config)
        mod.login()
        console.print(
            f"[green]✔ ورود {args.platform} انجام و سشن ذخیره شد[/green] "
            f"[dim](کانال: {engine.channel} | پروفایل: data/profiles/{args.platform})[/dim]")
    finally:
        engine.close()


def cmd_install(args) -> None:
    """نصب کرومیوم Playwright از آینه — بدون فیلترشکن (رفع خطای 403 تحریمی)."""
    import os
    import subprocess

    mirror = args.mirror or "https://cdn.npmmirror.com/binaries/playwright"
    console.print(Panel.fit(
        f"[bold green]نصب {args.browser} از آینه[/] [dim]\n{mirror}[/dim]",
        border_style="green",
    ))
    env = dict(os.environ)
    env["PLAYWRIGHT_DOWNLOAD_HOST"] = mirror
    proc = subprocess.run(
        [sys.executable, "-m", "playwright", "install", args.browser],
        env=env,
    )
    if proc.returncode == 0:
        console.print("[green]✔ نصب کامل شد — پارس‌ایجنت آماده است[/green]")
        console.print("[dim]نکته: اگر Edge یا Chrome نصب دارید، اصلاً به این دانلود "
                      "نیازی نیست؛ لانچر خودکار اول از همان‌ها استفاده می‌کند.[/dim]")
    else:
        console.print("[yellow]✖ نصب از آینه ناموفق بود — اگر Edge یا Chrome "
                      "نصب دارید، این مرحله را رد کنید و مستقیم اجرا کنید.[/yellow]")
        sys.exit(proc.returncode)


def cmd_run(args) -> None:
    config = load_config()
    data = json.loads(Path(args.task).read_text(encoding="utf-8"))
    tasks = data["tasks"] if "tasks" in data else [data]
    if args.task_name:
        tasks = [t for t in tasks if t.get("name") == args.task_name] or tasks[:1]

    engine = build_engines(config, headless=args.headless)
    try:
        for task in tasks:
            engine.run(task, dry=args.dry)
    finally:
        engine.finish()


def cmd_record(args) -> None:
    InputRecorder(out_path=args.out).record()
    console.print(f"[green]✔ ماکرو ذخیره شد → {args.out}[/green]")


def cmd_play(args) -> None:
    MacroPlayer(SystemController(human=False)).play(
        args.macro, speed=args.speed, loop=args.loop)


def cmd_schedule(args) -> None:
    config = load_config()
    engine = build_engines(config)

    def runner(task_path: str):
        data = json.loads(Path(task_path).read_text(encoding="utf-8"))
        tasks = data["tasks"] if "tasks" in data else [data]
        if args.task_name:
            tasks = [t for t in tasks if t.get("name") == args.task_name] or tasks[:1]
        for task in tasks:
            engine.run(task)

    sched = Scheduler(config)
    sched.attach_runner(runner)
    if args.every:
        unit = args.every[-1]
        value = int(args.every[:-1])
        sched.every(args.task, **{{"s": "seconds", "m": "minutes",
                                  "h": "hours"}[unit]: value})
    if args.at:
        sched.daily(args.task, at=args.at)
    console.print("[cyan]⏰ زمان‌بند فعال شد — Ctrl+C برای توقف[/cyan]")
    try:
        sched.run_forever()
    except KeyboardInterrupt:
        sched.stop()
        engine.finish()
        console.print("[yellow]زمان‌بند متوقف شد[/yellow]")


def cmd_demo(args) -> None:
    """Tiny smoke-test of the browser engine (opens example.com)."""
    config = load_config()
    with BrowserEngine(config).start(headless=args.headless) as engine:
        page = engine.new_page()
        engine.goto(page, "https://example.com")
        engine.click_text(page, "More information...")
        shot = engine.screenshot(page, "demo")
        console.print(f"[green]✔ دمو اجرا شد — اسکرین‌شات: {shot}[/green]")


def cmd_gateway(args) -> None:
    config = load_config()
    gcfg = config.get("gateway", {})
    if not gcfg.get("enabled") and not args.force:
        console.print("[yellow]gateway.enabled=false در config.json — "
                      "برای اجرای اجباری --force بزنید[/yellow]")
        return

    engine_holder = {"engine": None}

    def on_run_task(task: dict) -> dict:
        if engine_holder["engine"] is None:
            engine_holder["engine"] = build_engines(load_config())
        stats = engine_holder["engine"].run(task)
        return {"task": stats["task"], "ok": stats["ok"],
                "duration_s": stats["duration_s"]}

    client = GatewayClient(config, on_run_task=on_run_task)
    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        client.stop()
        if engine_holder["engine"]:
            engine_holder["engine"].finish()


# ---------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="parsagent",
        description="پارس‌ایجنت — ایجنت اتوماسیون ویندوز (موس/کیبورد + مرورگر)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("platforms", help="فهرست پلتفرم‌ها").set_defaults(func=cmd_platforms)

    inst = sub.add_parser("install", help="نصب مرورگر Playwright از آینه (بدون فیلترشکن)")
    inst.add_argument("--browser", default="chromium",
                      choices=["chromium", "firefox", "webkit"])
    inst.add_argument("--mirror", default=None, help="آدرس آینه جایگزین")
    inst.set_defaults(func=cmd_install)

    pl = sub.add_parser("login", help="ورود اول به یک پلتفرم و ذخیره سشن")
    pl.add_argument("platform", choices=sorted(PLATFORMS))
    pl.set_defaults(func=cmd_login)

    rn = sub.add_parser("run", help="اجرای یک تسک/فایل تسک")
    rn.add_argument("task", help="مسیر فایل تسک JSON")
    rn.add_argument("-t", "--task-name", help="نام تسک داخل فایل (اختیاری)")
    rn.add_argument("--dry", action="store_true", help="اجرای خشک بدون عملیات واقعی")
    rn.add_argument("--headless", action="store_true", help="مرورگر بدون پنجره")
    rn.set_defaults(func=cmd_run)

    rc = sub.add_parser("record", help="ضبط ورودی‌ها (F9 پایان، F10 لغو)")
    rc.add_argument("-o", "--out", default="macros/macro.json")
    rc.set_defaults(func=cmd_record)

    pl2 = sub.add_parser("play", help="بازپخش ماکرو ضبط‌شده")
    pl2.add_argument("macro")
    pl2.add_argument("-s", "--speed", type=float, default=1.0)
    pl2.add_argument("--loop", type=int, default=1)
    pl2.set_defaults(func=cmd_play)

    sc = sub.add_parser("schedule", help="زمان‌بندی اجرای تسک")
    sc.add_argument("task")
    sc.add_argument("-t", "--task-name")
    sc.add_argument("--every", help="بازه تکرار مثل 30m یا 2h یا 45s")
    sc.add_argument("--at", help="ساعت روزانه مثل 09:30")
    sc.set_defaults(func=cmd_schedule)

    dm = sub.add_parser("demo", help="دموی سریع موتور مرورگر")
    dm.add_argument("--headless", action="store_true")
    dm.set_defaults(func=cmd_demo)

    gw = sub.add_parser("gateway", help="اتصال به پنل کنترل وب (WebSocket)")
    gw.add_argument("--force", action="store_true")
    gw.set_defaults(func=cmd_gateway)

    return p


def main() -> None:
    console.print(Panel.fit(
        "[bold green]ParsAgent[/] [dim]v1.0.0[/] — "
        "ایجنت اتوماسیون ویندوز | موس و کیبورد + مرورگر",
        border_style="green",
    ))
    args = build_parser().parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        console.print("\n[yellow]⛔ متوقف شد (Ctrl+C)[/yellow]")


if __name__ == "__main__":
    main()
