@echo off
setlocal
cd /d "%~dp0"
title Build SmartDownloader EXE

set "PY_EXE="
if exist "C:\Users\Hagag\AppData\Local\Programs\Python\Python314\python.exe" (
    set "PY_EXE=C:\Users\Hagag\AppData\Local\Programs\Python\Python314\python.exe"
) else if exist "C:\Users\Hagag\AppData\Local\Python\pythoncore-3.14-64\python.exe" (
    set "PY_EXE=C:\Users\Hagag\AppData\Local\Python\pythoncore-3.14-64\python.exe"
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 set "PY_EXE=python"
)

if "%PY_EXE%"=="" (
    echo [ERROR] Python not found.
    pause
    exit /b 1
)

echo Building SmartDownloader standalone executable...
"%PY_EXE%" build_exe.py
pause
