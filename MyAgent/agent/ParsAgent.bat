@echo off
rem ─────────────────────────────────────────────────────────────
rem  ParsAgent — راه‌اندازی لانچر گرافیکی (دابل‌کلیک کن!)
rem  اگر پنجره‌ای باز نشد یعنی پایتون در PATH نیست — python.org
rem ─────────────────────────────────────────────────────────────
chcp 65001 >nul
title ParsAgent Launcher
cd /d "%~dp0"

where pythonw >nul 2>nul && (start "" pythonw launcher.py & exit /b)
where python  >nul 2>nul && (start "" python  launcher.py & exit /b)
where py      >nul 2>nul && (start "" py -3   launcher.py & exit /b)

echo [!] Python not found in PATH.
echo     Install it from https://www.python.org/downloads/
echo     (tick "Add python.exe to PATH" during setup)
pause
