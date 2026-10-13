@echo off
chcp 65001 >nul
title ParsAgent — نصب کرومیوم Playwright از آینه (بدون فیلترشکن)

REM ============================================================
REM  رفع خطای 403 تحریمی CDN رسمی Playwright:
REM  دانلود از آینه چینی npmmirror که در ایران بدون فیلترشکن
REM  در دسترس است. بعد از این نصب، دیگر این فایل لازم نیست.
REM
REM  نکته مهم: اگر Microsoft Edge یا Chrome نصب دارید، اصلاً به این
REM  دانلود نیازی نیست — لانچر پارس‌ایجنت خودکار اول از همان
REM  مرورگرها استفاده می‌کند (msedge → chrome → chromium).
REM ============================================================

set PLAYWRIGHT_DOWNLOAD_HOST=https://cdn.npmmirror.com/binaries/playwright

echo [1/1] در حال دانلود کرومیوم از آینه ...
python -m playwright install chromium

if %errorlevel% neq 0 (
    echo.
    echo  نصب از آینه ناموفق بود — ولی یادتان باشد: اگر Edge یا
    + Chrome نصب دارید، پارس‌ایجنت بدون این مرحله هم کار می‌کند.
    pause
    exit /b 1
)

echo.
echo  نصب کامل شد — پارس‌ایجنت آماده است.
pause
