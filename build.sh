#!/usr/bin/env bash
# ==============================================================
# SmartDownloader Standalone Build Script for Linux & macOS
# Developed by Ahmed Hagag (@i7ego)
# ==============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if command -v python3 >/dev/null 2>&1; then
    PY_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PY_BIN="python"
else
    echo "[!] Error: Python 3 not found."
    exit 1
fi

echo "[*] Installing build requirements..."
"$PY_BIN" -m pip install -q pyinstaller -r requirements.txt

echo "[*] Building standalone binary with PyInstaller..."
"$PY_BIN" build_exe.py

echo "[+] Build complete! Check dist/SmartDownloader"
