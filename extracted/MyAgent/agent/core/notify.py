"""Cross-platform desktop notifications (Windows toast via plyer)."""

from core.logger import get_logger

log = get_logger("notify")


def notify(title: str, message: str, timeout: int = 6) -> None:
    """Show a toast. Falls back to a log line when plyer is unavailable."""
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="ParsAgent",
            timeout=timeout,
        )
        log.info("🔔 toast: %s — %s", title, message)
    except Exception as exc:
        log.info("🔔 %s — %s (plyer unavailable: %s)", title, message, exc)
