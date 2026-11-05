@echo off
cd /d "%~dp0"

if exist "%~dp0dist\SmartDownloader\SmartDownloader.exe" (
    start "" "%~dp0dist\SmartDownloader\SmartDownloader.exe"
    exit /b 0
)

set "PYW_EXE=C:\Users\Hagag\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"
if not exist "%PYW_EXE%" set "PYW_EXE=C:\Users\Hagag\AppData\Local\Programs\Python\Python314\pythonw.exe"
if not exist "%PYW_EXE%" set "PYW_EXE=pythonw"

start "" "%PYW_EXE%" "%~dp0main.py"
exit /b 0
