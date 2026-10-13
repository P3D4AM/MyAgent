"""Remote control channel — connects ParsAgent to the web control panel.

Protocol (JSON messages over a single WebSocket):

  agent → panel
    {"type": "hello",       "agent": "pars-agent/1.0.0", "platform": "windows"}
    {"type": "telemetry",   "cpu": 12.5, "mouse": [512, 384], "tasks_done": 3}
    {"type": "log",         "level": "info", "line": "..."}
    {"type": "result",      "task": "...", "ok": true, "duration_s": 8.2}

  panel → agent
    {"type": "command", "cmd": "run_task", "task": {...task json...}}
    {"type": "command", "cmd": "status"}
    {"type": "command", "cmd": "stop"}

The gateway address lives in config.json → gateway.url. Point it at your own
instance of the ParsAgent web panel (or any small websocket relay you trust).
"""

import asyncio
import json
import platform
import random
import time
from typing import Any, Callable, Dict, Optional

from core.logger import get_logger

log = get_logger("gateway")


class GatewayClient:
    """Async WebSocket client with auto-reconnect and command dispatch."""

    def __init__(self, config: Dict[str, Any],
                 on_run_task: Optional[Callable[[dict], dict]] = None):
        g = config.get("gateway", {})
        self.url = g.get("url", "ws://127.0.0.1:3030")
        self.token = g.get("token", "")
        self.on_run_task = on_run_task
        self._stop = asyncio.Event()

    # ------------------------------------------------------------------ #
    async def run(self) -> None:
        """Connect forever with exponential backoff (1s → 30s)."""
        backoff = 1.0
        while not self._stop.is_set():
            try:
                import websockets
                async with websockets.connect(self.url, ping_interval=20) as ws:
                    await self._hello(ws)
                    backoff = 1.0
                    log.info("🛰 gateway connected → %s", self.url)
                    await self._serve(ws)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.warning("gateway unreachable (%s) — retry in %.0fs",
                            exc, backoff)
            await asyncio.sleep(backoff + random.uniform(0, 1))
            backoff = min(backoff * 2, 30)

    async def _hello(self, ws) -> None:
        await ws.send(json.dumps({
            "type": "hello",
            "agent": "pars-agent/1.0.0",
            "platform": f"{platform.system()} {platform.release()}",
            "token": self.token,
        }))

    async def _serve(self, ws) -> None:
        """Read loop: dispatch commands, push telemetry every 5s."""
        telemetry_task = asyncio.create_task(self._telemetry_loop(ws))
        try:
            async for raw in ws:
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if msg.get("type") == "command":
                    await self._dispatch(ws, msg)
        finally:
            telemetry_task.cancel()

    async def _telemetry_loop(self, ws) -> None:
        while True:
            try:
                import psutil
                cpu = psutil.cpu_percent(interval=None)
                mem = psutil.virtual_memory().percent
            except Exception:
                cpu, mem = 0.0, 0.0
            mouse = "-"
            try:
                import pyautogui
                pos = pyautogui.position()
                mouse = [pos.x, pos.y]
            except Exception:
                pass
            await ws.send(json.dumps({
                "type": "telemetry", "cpu": cpu, "mem": mem, "mouse": mouse,
                "uptime_s": round(time.time() % 86_400),
            }))
            await asyncio.sleep(5)

    async def _dispatch(self, ws, msg: Dict[str, Any]) -> None:
        cmd = msg.get("cmd")
        if cmd == "run_task" and self.on_run_task:
            def _log(level: str, line: str) -> None:
                # fire-and-forget: forward task logs to the panel
                asyncio.ensure_future(ws.send(json.dumps(
                    {"type": "log", "level": level, "line": line})))
            result = await asyncio.to_thread(self.on_run_task, msg.get("task", {}))
            await ws.send(json.dumps({"type": "result", **result}))
        elif cmd == "status":
            await ws.send(json.dumps({"type": "result", "ok": True,
                                      "status": "idle", "agent": "pars-agent/1.0.0"}))
        elif cmd == "stop":
            self._stop.set()
            await ws.send(json.dumps({"type": "result", "ok": True,
                                      "status": "stopping"}))

    def stop(self) -> None:
        self._stop.set()
