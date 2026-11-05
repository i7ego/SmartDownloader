#!/usr/bin/env bash
# ==============================================================
# SmartDownloader Launcher for Linux & macOS
# Developed by Ahmed Hagag (@i7ego)
# ==============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Detect Python 3
if command -v python3 >/dev/null 2>&1; then
    PY_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PY_BIN="python"
else
    echo "[!] Error: Python 3 is not installed or not found in PATH."
    echo "    Please install Python 3 (https://www.python.org/)."
    exit 1
fi

# 2. Ensure virtual environment exists
if [ ! -d "venv" ]; then
    echo "[*] Creating Python virtual environment (venv)..."
    "$PY_BIN" -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# 3. Verify and install requirements
echo "[*] Checking and installing dependencies..."
pip install -q -r requirements.txt

# 4. Check FFmpeg availability
if ! command -v ffmpeg >/dev/null 2>&1 && [ ! -f "bin/ffmpeg" ]; then
    echo "[!] Warning: ffmpeg is not installed or not in PATH."
    echo "    Please install it using your package manager:"
    echo "      • Ubuntu/Debian : sudo apt install ffmpeg python3-tk"
    echo "      • Fedora        : sudo dnf install ffmpeg python3-tkinter"
    echo "      • Arch Linux    : sudo pacman -S ffmpeg tk"
    echo "      • macOS (Brew)  : brew install ffmpeg python-tk"
fi

# 5. Launch the application
echo "[+] Launching Smart Media Downloader..."
python main.py "$@"
