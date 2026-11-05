"""
نقطة الدخول الرئيسية لتشغيل محمّل الوسائط الذكي (main.py).
"""

import io
import sys


def _ensure_safe_streams() -> None:
    """ضمان سلامة sys.stdout و sys.stderr عند التشغيل عبر pythonw.exe أو مع الرموز التعبيرية."""
    if sys.stdout is None:
        sys.stdout = io.StringIO()
    elif hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    if sys.stderr is None:
        sys.stderr = io.StringIO()
    elif hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


_ensure_safe_streams()

# تمييز البرنامج لدى شريط مهام ويندوز لعرض أيقونته الخاصة بدلاً من أيقونة بايثون الافتراضية
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "antigravity.smartdownloader.app.1.0"
        )
    except Exception:
        pass

from ui.app import DownloaderApp  # noqa: E402


def main() -> None:
    app = DownloaderApp()
    app.mainloop()


if __name__ == "__main__":
    main()
