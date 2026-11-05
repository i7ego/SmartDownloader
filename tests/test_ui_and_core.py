"""
اختبارات شاملة للتحقق من مطابقة جميع متطلبات تصميم الواجهة وتجربة الاستخدام (UI/UX) والمحرك الخلفي.
"""

import re
from pathlib import Path
import pytest

from core.downloader import DownloadManager, format_duration, format_speed
from core.storage import StorageManager
from ui import theme
from ui.i18n import i18n
from ui.icons import create_app_logo_pil, get_icon
from ui.app import DownloaderApp


def test_theme_constants_exact_match() -> None:
    """التحقق من تطابق جميع الألوان والأحجام والمسافات مع المواصفات في ui/theme.py."""
    # الوضع الداكن
    assert theme.DARK_BG_MAIN == "#0F1117"
    assert theme.DARK_BG_SIDEBAR == "#161923"
    assert theme.DARK_BG_CARD == "#1C2030"
    assert theme.DARK_BORDER == "#2A2F45"
    assert theme.COLOR_PRIMARY == "#6C5CE7"
    assert theme.COLOR_PRIMARY_HOVER == "#5A4BD1"
    assert theme.COLOR_ACCENT == "#00CEC9"
    assert theme.COLOR_SUCCESS == "#2ECC71"
    assert theme.COLOR_WARNING == "#F39C12"
    assert theme.COLOR_ERROR == "#E74C3C"
    assert theme.DARK_TEXT_PRIMARY == "#F5F6FA"
    assert theme.DARK_TEXT_SECONDARY == "#9AA0B5"

    # الوضع الفاتح
    assert theme.LIGHT_BG_MAIN == "#F5F7FB"
    assert theme.LIGHT_BG_SIDEBAR == "#FFFFFF"
    assert theme.LIGHT_BG_CARD == "#FFFFFF"
    assert theme.LIGHT_BORDER == "#E3E7F0"
    assert theme.LIGHT_TEXT_PRIMARY == "#1E2233"

    # أحجام الخطوط الثابتة
    assert theme.FONT_SIZE_TITLE_LARGE == 24
    assert theme.FONT_SIZE_SECTION_TITLE == 18
    assert theme.FONT_SIZE_BODY == 14
    assert theme.FONT_SIZE_SMALL == 12

    # الزوايا المستديرة (بين 10 و 16)
    for r in (
        theme.RADIUS_CHIP,
        theme.RADIUS_BUTTON,
        theme.RADIUS_INPUT,
        theme.RADIUS_CARD,
        theme.RADIUS_THUMBNAIL,
    ):
        assert 10 <= r <= 16

    # أبعاد الشريط الجانبي والنافذة والأزرار
    assert theme.SIDEBAR_WIDTH == 220
    assert theme.WINDOW_MIN_WIDTH == 1000
    assert theme.WINDOW_MIN_HEIGHT == 650
    assert 40 <= theme.BUTTON_HEIGHT <= 44


def test_no_hardcoded_hex_colors_outside_theme() -> None:
    """التحقق من عدم كتابة أي لون Hex مباشرة خارج ملف ui/theme.py."""
    root = Path(__file__).resolve().parent.parent
    hex_pattern = re.compile(r"#[0-9A-Fa-f]{6}\b")

    for folder in ("ui", "core"):
        for py_file in (root / folder).rglob("*.py"):
            if py_file.name == "theme.py":
                continue
            content = py_file.read_text(encoding="utf-8")
            matches = hex_pattern.findall(content)
            assert not matches, f"Found hardcoded color {matches} in {py_file}"


def test_storage_and_downloader_core(tmp_path: Path) -> None:
    """اختبار الإعدادات الافتراضية الذكية وسجل التحميلات وتحليل الروابط."""
    storage = StorageManager(data_dir=tmp_path)
    assert storage.get_setting("theme") == "Dark"
    assert storage.get_setting("language") == "en"
    assert storage.get_setting("default_format") == "MP4"

    entry = storage.add_history_entry(
        title="فيديو تجريبي",
        url="https://example.com/video",
        channel="قناة تجريبية",
        media_type="video",
        quality="1080p",
        fmt="MP4",
        save_path=str(tmp_path),
        duration_str="08:45",
    )
    assert len(storage.history) == 1
    storage.remove_history_entry(entry["id"])
    assert len(storage.history) == 0

    assert format_duration(525) == "08:45"
    assert format_speed(2 * 1024 * 1024) == "2.0 MB/s"

    dm = DownloadManager()
    info = dm.analyze_url("https://example.com/video")
    assert info.title
    assert not info.is_playlist

    pl_info = dm.analyze_url("https://example.com/playlist?list=1")
    assert pl_info.is_playlist
    assert len(pl_info.playlist_entries) == 5


def test_full_gui_workflow(tmp_path: Path) -> None:
    """اختبار بناء النافذة الرئيسية والتبويبات والأزرار والشرائح وتبديل الثيم واللغة."""
    storage = StorageManager(data_dir=tmp_path)
    storage.set_setting("first_run", False)

    app = DownloaderApp(data_dir=tmp_path, enable_tray=False)
    try:
        app.update_idletasks()

        # التحقق من التبويبات الستة
        assert set(app._pages.keys()) == {"new", "active", "cutter", "converter", "history", "settings"}
        assert app._current_tab == "new"

        # التحقق من تبديل مفتاح (فيديو | صوت) وتحديث الشرائح
        app.page_new.media_switch.set_mode("audio", trigger=True)
        app.update()
        assert app.page_new.media_switch.mode == "audio"

        app.page_new.media_switch.set_mode("video", trigger=True)
        app.update()
        assert app.page_new.media_switch.mode == "video"

        # التحقق من تحليل رابط وإظهار بطاقة المعاينة
        app.page_new.url_var.set("https://example.com/video")
        app.update_idletasks()
        info = app.downloader.analyze_url("https://example.com/video")
        app.page_new._apply_analyzed_media(info)
        app.update_idletasks()
        assert app.page_new.current_media is not None

        # التنقل بين التبويبات الستة
        for tab in ("active", "cutter", "converter", "history", "settings", "new"):
            app.switch_tab(tab, animate=False)
            app.update_idletasks()
            assert app._current_tab == tab

        # تبديل الثيم الداكن / الفاتح عبر النقر الفعلي على الزر
        app.theme_toggle_btn._on_enter()
        app.theme_toggle_btn._on_release()
        app.update_idletasks()
        assert app.storage.get_setting("theme") == "Light"

        app.page_settings.theme_btn._on_enter()
        app.page_settings.theme_btn._on_release()
        app.update_idletasks()
        assert app.storage.get_setting("theme") == "Dark"

        # تبديل اللغة (الإنجليزية LTR <-> العربية RTL)
        app.toggle_language()
        app.update_idletasks()
        assert i18n.lang == "ar"
        assert i18n.is_rtl

        app.toggle_language()
        app.update_idletasks()
        assert i18n.lang == "en"
        assert not i18n.is_rtl

        # التحقق من الأيقونات والشعار
        logo = create_app_logo_pil(size=48)
        assert logo.size == (48, 48)
        icon = get_icon("download", size=20)
        assert icon is not None
    finally:
        app.quit_app()
