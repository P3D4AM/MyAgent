@echo off
chcp 65001 >nul
title ParsAgent
cd /d "%~dp0"

rem ---------------------------------------------------------------
rem  ParsAgent — اجرا با دابل‌کلیک
rem  فقط لانچر گرافیکی را بالا می‌آورد؛ سرور پنل و ضبط ماکرو
rem  هرگز خودکار شروع نمی‌شوند (همه‌چیز با دکمهٔ خودش در پنل).
rem
rem  ۲.۸.۰: اول py launcher امتحان می‌شود چون در انتخاب پیش‌فرضش
rem  هرگز نسخهٔ free-threaded (مثل python3.13t) را برنمی‌گزیند؛
rem  لانچر هم اگر باز با پایتون t باز شود، خودش را با پایتونِ
rem  استانداردِ سیستم بازگشایی می‌کند (یا نصب می‌کند).
rem ---------------------------------------------------------------

set PYSTD=0
where py >nul 2>nul
if not errorlevel 1 (
    py -c "import sys" >nul 2>nul
    if not errorlevel 1 set PYSTD=1
)

if %PYSTD%==1 (
    start "" py launcher.py
    exit /b
)

where python >nul 2>nul
if not errorlevel 1 (
    start "" python launcher.py
    exit /b
)

echo ❌ پایتون استاندارد پیدا نشد — از python.org نسخهٔ استاندارد را نصب کنید
echo    (تیک Add to PATH را بزنید؛ نسخهٔ free-threaded مثل 3.13t مناسب نیست).
pause
