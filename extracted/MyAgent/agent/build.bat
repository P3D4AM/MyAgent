@echo off
REM ============================================================
REM  ParsAgent — ساخت فایل EXE تک‌فایلی (PyInstaller)
REM  پیش‌نیاز: python -m pip install pyinstaller
REM ============================================================
cd /d "%~dp0"

echo [1/3] Installing PyInstaller ...
python -m pip install --upgrade pyinstaller || goto :error

echo [2/3] Building ParsAgent.exe ...
pyinstaller --onefile --name ParsAgent ^
  --hidden-import=pyautogui ^
  --hidden-import=pynput.keyboard ^
  --hidden-import=pynput.mouse ^
  --hidden-import=playwright ^
  --collect-submodules=platforms ^
  --collect-submodules=core ^
  main.py || goto :error

echo [3/3] Done. Output:
echo     dist\ParsAgent.exe
echo.
echo  نکته: پوشه‌های data\ , macros\ , tasks\ , config.json باید
echo  کنار ParsAgent.exe قرار بگیرند.
pause
exit /b 0

:error
echo  ✖ ساخت با خطا مواجه شد.
pause
exit /b 1
