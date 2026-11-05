"""
إدارة الإعدادات الذكية وسجل التحميلات (core/storage.py).
توفر قيماً افتراضية ذكية (أفضل جودة، MP4، مجلد Downloads) بحيث لا يحتاج المبتدئ لتغيير أي إعداد.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_default_downloads_dir() -> str:
    """إرجاع مجلد التحميلات الافتراضي للمستخدم."""
    downloads = Path.home() / "Downloads"
    if downloads.exists():
        return str(downloads)
    return str(Path.home())


DEFAULT_SETTINGS: Dict[str, Any] = {
    "theme": "Dark",                    # الوضع الداكن هو الافتراضي
    "language": "en",                   # English default with LTR, switchable to Arabic RTL
    "download_dir": get_default_downloads_dir(),
    "default_quality": "1080p",
    "default_format": "MP4",
    "concurrent_downloads": 3,
    "auto_analyze_on_paste": True,
    "minimize_to_tray": True,
    "first_run": True,
}


class StorageManager:
    """إدارة قراءة وحفظ الإعدادات وسجل التحميلات في ملفات JSON محلية."""

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        if data_dir is None:
            data_dir = Path(__file__).resolve().parent.parent / "data"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.settings_file = self.data_dir / "settings.json"
        self.history_file = self.data_dir / "history.json"

        self.settings: Dict[str, Any] = self._load_settings()
        self.history: List[Dict[str, Any]] = self._load_history()

    def _load_settings(self) -> Dict[str, Any]:
        merged = dict(DEFAULT_SETTINGS)
        if self.settings_file.exists():
            try:
                raw = json.loads(self.settings_file.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    merged.update(raw)
            except Exception:
                pass
        return merged

    def save_settings(self) -> None:
        try:
            self.settings_file.write_text(
                json.dumps(self.settings, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, DEFAULT_SETTINGS.get(key, default))

    def set_setting(self, key: str, value: Any, save: bool = True) -> None:
        self.settings[key] = value
        if save:
            self.save_settings()

    def _load_history(self) -> List[Dict[str, Any]]:
        if self.history_file.exists():
            try:
                raw = json.loads(self.history_file.read_text(encoding="utf-8"))
                if isinstance(raw, list):
                    return raw
            except Exception:
                pass
        return []

    def save_history(self) -> None:
        try:
            self.history_file.write_text(
                json.dumps(self.history, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    def add_history_entry(
        self,
        title: str,
        url: str,
        channel: str,
        media_type: str,
        quality: str,
        fmt: str,
        save_path: str,
        duration_str: str = "",
    ) -> Dict[str, Any]:
        entry = {
            "id": f"hist_{int(datetime.now().timestamp() * 1000)}",
            "title": title,
            "url": url,
            "channel": channel,
            "media_type": media_type,
            "quality": quality,
            "format": fmt,
            "save_path": save_path,
            "duration_str": duration_str,
            "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.history.insert(0, entry)
        self.save_history()
        return entry

    def remove_history_entry(self, entry_id: str) -> None:
        self.history = [item for item in self.history if item.get("id") != entry_id]
        self.save_history()

    def clear_history(self) -> None:
        self.history.clear()
        self.save_history()
