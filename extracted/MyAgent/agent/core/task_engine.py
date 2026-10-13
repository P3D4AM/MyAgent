"""Declarative task engine — JSON workflows that chain every engine together.

A task file describes WHAT to do; the engine decides HOW. Example task:

    {
      "name": "morning_routine",
      "vars": { "caption": "صبح بخیر ☀️", "chat": "ParsAgent Devs" },
      "steps": [
        {"type": "platform", "platform": "instagram", "action": "post_photo",
         "args": {"image": "assets/sunrise.jpg", "caption": "{{caption}}"}},
        {"type": "wait", "seconds": 3},
        {"type": "platform", "platform": "telegram", "action": "send_message",
         "args": {"chat": "{{chat}}", "text": "Posted! ✓"}},
        {"type": "notify", "message": "روتین صبح تمام شد ✅"}
      ],
      "on_error": "continue",          # abort | continue
      "retries": 1                     # per-step retry count
    }

Step types:
    platform  → action of a social platform module (instagram, telegram, …)
    browser   → raw engine op: goto / click / type / press / screenshot
    desktop   → raw SystemController op: click / type_text / hotkey / scroll
    wait      → sleep seconds
    notify    → Windows toast
    shell     → run an OS command (use carefully!)
"""

import json
import re
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from core.logger import get_logger
from core.notify import notify

log = get_logger("tasks")


class StepError(RuntimeError):
    pass


class TaskEngine:
    """Loads task JSON files and executes their steps step-by-step."""

    def __init__(self, config: Dict[str, Any],
                 browser_factory: Callable, desktop: Any, platforms: Dict[str, Any]):
        """
        browser_factory: callable(headless) → started BrowserEngine
        desktop:         SystemController instance
        platforms:        {name: cls} registry
        """
        self.config = config
        self.browser_factory = browser_factory
        self.desktop = desktop
        self.platforms = platforms
        self._browser = None
        self._platform_instances: Dict[str, Any] = {}

    # ------------------------------------------------------------------ #
    def platform(self, name: str):
        """Lazily instantiate & cache a platform module bound to the browser.

        هر پلتفرم پروفایل مرورگر ماندگار مستقل خودش را دارد
        (data/profiles/<name>) — use_profile() قبل از هر استفاده فعالش
        می‌کند تا new_page() دقیقاً در همان کانتکست باز شود.
        """
        if name not in self.platforms:
            raise StepError(f"unknown platform '{name}' "
                            f"(available: {', '.join(sorted(self.platforms))})")
        if self._browser is None:
            self._browser = self.browser_factory()
        self._browser.use_profile(name)
        if name not in self._platform_instances:
            self._platform_instances[name] = self.platforms[name](self._browser, self.config)
        return self._platform_instances[name]

    def finish(self) -> None:
        if self._browser:
            self._browser.close()
            self._browser = None
        self._platform_instances.clear()

    # ------------------------------------------------------------------ #
    # template vars
    # ------------------------------------------------------------------ #
    @staticmethod
    def _resolve(value: Any, vars_: Dict[str, str]) -> Any:
        if isinstance(value, str):
            def sub(m):
                key = m.group(1).strip()
                return str(vars_.get(key, m.group(0)))
            return re.sub(r"\{\{(\w+)\}\}", sub, value)
        if isinstance(value, list):
            return [TaskEngine._resolve(v, vars_) for v in value]
        if isinstance(value, dict):
            return {k: TaskEngine._resolve(v, vars_) for k, v in value.items()}
        return value

    def _prompt_vars(self, task: Dict[str, Any]) -> Dict[str, str]:
        """Ask (console) for vars flagged interactive:true — e.g. 2FA codes."""
        vars_ = dict(task.get("vars", {}))
        for name, spec in task.get("interactive_vars", {}).items():
            if spec.get("interactive"):
                secret = spec.get("secret", False)
                prompt = spec.get("prompt", name)
                val = input(f"{prompt}: ")
                vars_[name] = val
        return vars_

    # ------------------------------------------------------------------ #
    def load(self, path: str) -> Dict[str, Any]:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if "tasks" in data:          # a bundle of tasks → return list carrier
            return data
        if "steps" not in data:
            raise StepError(f"{path}: missing 'steps' array")
        return data

    def run(self, task: Dict[str, Any], dry: bool = False) -> Dict[str, Any]:
        """Execute a task dict → stats {ok, steps, duration_s, failures}."""
        started = time.time()
        vars_ = self._prompt_vars(task)
        steps: List[Dict[str, Any]] = task.get("steps", [])
        on_error = task.get("on_error", "abort")
        default_retries = task.get("retries", 0)
        stats = {"task": task.get("name", "unnamed"), "steps": 0, "failures": [],
                 "ok": True, "duration_s": 0.0}

        log.info("▛▀▀ task: %s — %s step(s) %s", task.get("name", "unnamed"),
                 len(steps), "(DRY-RUN)" if dry else "")

        for idx, step in enumerate(steps, 1):
            step = self._resolve(step, vars_)
            retries = int(step.get("retries", default_retries))
            try:
                log.info("▙ step %s/%s → %s", idx, len(steps), self._describe(step))
                if dry:
                    stats["steps"] += 1
                    continue
                self._execute(step)
                stats["steps"] += 1
            except Exception as exc:
                succeeded = False
                if retries > 0:
                    log.warning("step %s failed (%s) — retrying up to %s×",
                                idx, exc, retries)
                    for attempt in range(1, retries + 1):
                        try:
                            time.sleep(1.5 * attempt)
                            self._execute(step)
                            stats["steps"] += 1
                            succeeded = True
                            break
                        except Exception as exc2:
                            exc = exc2
                if not succeeded:
                    stats["failures"].append({"step": idx, "error": str(exc)})
                    log.error("✖ step %s/%s failed: %s", idx, len(steps), exc)
                    if on_error == "abort":
                        stats["ok"] = False
                        break

        stats["duration_s"] = round(time.time() - started, 1)
        log.info("▜▄▄ task %s — %s (steps %s/%s, %.1fs)",
                 stats["task"],
                 "✔ OK" if stats["ok"] else "✖ FAILED",
                 stats["steps"], len(steps), stats["duration_s"])
        return stats

    # ------------------------------------------------------------------ #
    @staticmethod
    def _describe(step: Dict[str, Any]) -> str:
        t = step.get("type", "?")
        if t == "platform":
            return f"platform:{step.get('platform')}.{step.get('action')}"
        return f"{t}:{step.get('action', '')}".rstrip(':')

    def _execute(self, step: Dict[str, Any]) -> None:
        stype = step.get("type")
        if stype == "platform":
            mod = self.platform(step["platform"])
            method = getattr(mod, step["action"], None)
            if method is None:
                raise StepError(f"platform '{step['platform']}' has no action "
                                f"'{step['action']}'")
            method(**step.get("args", {}))
        elif stype == "browser":
            self._browser_step(step)
        elif stype == "desktop":
            self._desktop_step(step)
        elif stype == "wait":
            time.sleep(float(step.get("seconds", 1)))
        elif stype == "notify":
            notify("ParsAgent", step.get("message", "انجام شد"))
        elif stype == "shell":
            import subprocess
            subprocess.run(step["command"], shell=True, check=True,
                           capture_output=True)
        else:
            raise StepError(f"unknown step type '{stype}'")

    def _browser_step(self, step: Dict[str, Any]) -> None:
        if self._browser is None:
            self._browser = self.browser_factory()
        page = self._browser.pages[0] if self._browser.pages else self._browser.new_page()
        action = step.get("action")
        if action == "goto":
            self._browser.goto(page, step["url"])
        elif action == "click":
            self._browser.click(page, step["selector"])
        elif action == "type":
            self._browser.type(page, step["selector"], step["text"],
                               secret=step.get("secret", False))
        elif action == "press":
            self._browser.press(page, step["key"])
        elif action == "screenshot":
            self._browser.screenshot(page, step.get("tag", "step"))
        else:
            raise StepError(f"unknown browser action '{action}'")

    def _desktop_step(self, step: Dict[str, Any]) -> None:
        action = step.get("action")
        if action == "click":
            self.desktop.click(step.get("x"), step.get("y"), button=step.get("button", "left"))
        elif action == "type_text":
            self.desktop.type_text(step["text"])
        elif action == "hotkey":
            self.desktop.hotkey(*step["keys"])
        elif action == "scroll":
            self.desktop.scroll(int(step.get("clicks", -3)))
        elif action == "click_image":
            ok = self.desktop.click_image(step["image"])
            if not ok:
                raise StepError(f"image not found: {step['image']}")
        else:
            raise StepError(f"unknown desktop action '{action}'")
