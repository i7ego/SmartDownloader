"""
النافذة الرئيسية للتطبيق (ui/app.py)
تضم:
- الشريط الجانبي الثابت (Sidebar بعرض 220px) مع التبويبات الأربعة والخط الجانبي الملوّن للتبويب النشط.
- أسفل الشريط الجانبي: زر تبديل الوضع الداكن/الفاتح، زر اللغة، ورقم الإصدار.
- دعم كامل لـ RTL وانعكاس التخطيط.
- انتقال سلس (Fade) عند التنقل بين التبويبات.
- اختصارات لوحة المفاتيح: Ctrl+V للصق وتحليل تلقائي، و Enter للبدء.
- شاشة ترحيب مختصرة عند أول تشغيل.
- أيقونة System Tray مع قائمة سريعة (فتح، إيقاف الكل، خروج).
"""

import sys
import threading
import tkinter as tk
from pathlib import Path
from typing import Callable, Dict, Optional
from PIL import Image, ImageTk
import customtkinter as ctk

try:
    import pystray
except ImportError:
    pystray = None  # type: ignore[assignment]

try:
    import windnd
except ImportError:
    windnd = None  # type: ignore[assignment]

from core.downloader import DownloadManager, DownloadTask
from core.storage import StorageManager
from ui import theme
from ui.i18n import i18n
from ui.icons import create_app_logo_pil, get_icon
from ui.components.buttons import GhostIconButton
from ui.components.dialogs import WelcomeDialog
from ui.components.feedback import ToastManager, Tooltip
from ui.pages.active_downloads import ActiveDownloadsPage
from ui.pages.converter_page import ConverterPage
from ui.pages.history_page import HistoryPage
from ui.pages.music_cutter import MusicCutterPage
from ui.pages.new_download import NewDownloadPage
from ui.pages.settings_page import SettingsPage


class SidebarTabItem(ctk.CTkFrame):
    """عنصر تبويب في الشريط الجانبي بخلفية Primary شفافة وخط جانبي ملوّن عند النشاط."""

    def __init__(
        self,
        master: object,
        tab_key: str,
        label_text: str,
        icon_name: str,
        on_select: Callable[[str], None],
    ) -> None:
        super().__init__(
            master,
            fg_color=theme.COLOR_TRANSPARENT,
            corner_radius=theme.RADIUS_BUTTON,
            height=46,
        )
        self.tab_key = tab_key
        self.icon_name = icon_name
        self.on_select = on_select
        self._active = False
        self.pack_propagate(False)

        # الخط الجانبي الملوّن للتبويب النشط
        self.indicator = ctk.CTkFrame(
            self,
            width=theme.SIDEBAR_INDICATOR_WIDTH,
            height=26,
            corner_radius=2,
            fg_color=theme.COLOR_TRANSPARENT,
        )
        self.indicator.pack(
            side=i18n.side_start,
            padx=(4, 0) if not i18n.is_rtl else (0, 4),
        )

        compound = "right" if i18n.is_rtl else "left"
        anchor = "e" if i18n.is_rtl else "w"

        self.btn = ctk.CTkButton(
            self,
            text=label_text,
            image=get_icon(icon_name, size=20, color_pair=theme.TEXT_SECONDARY),
            compound=compound,
            anchor=anchor,
            fg_color=theme.COLOR_TRANSPARENT,
            hover_color=theme.GHOST_HOVER,
            text_color=theme.TEXT_SECONDARY,
            font=theme.get_body_font(i18n.lang, bold=False),
            corner_radius=theme.RADIUS_BUTTON,
            height=44,
            command=lambda: self.on_select(self.tab_key),
        )
        self.btn.pack(side=i18n.side_start, fill="both", expand=True, padx=theme.SPACE_XS)

    def set_active(self, active: bool) -> None:
        self._active = active
        if active:
            self.configure(fg_color=theme.PRIMARY_TINT)
            self.indicator.configure(fg_color=theme.PRIMARY_COLOR)
            self.btn.configure(
                text_color=theme.TEXT_PRIMARY,
                font=theme.get_body_font(i18n.lang, bold=True),
                image=get_icon(self.icon_name, size=20, color_pair=theme.PRIMARY_COLOR),
            )
        else:
            self.configure(fg_color=theme.COLOR_TRANSPARENT)
            self.indicator.configure(fg_color=theme.COLOR_TRANSPARENT)
            self.btn.configure(
                text_color=theme.TEXT_SECONDARY,
                font=theme.get_body_font(i18n.lang, bold=False),
                image=get_icon(self.icon_name, size=20, color_pair=theme.TEXT_SECONDARY),
            )


class DownloaderApp(ctk.CTk):
    """النافذة الرئيسية لتطبيق محمّل الوسائط الذكي."""

    def __init__(self, data_dir: Optional[Path] = None, enable_tray: bool = True) -> None:
        self.storage = StorageManager(data_dir=data_dir)
        saved_lang = str(self.storage.get_setting("language", "en"))
        saved_theme = str(self.storage.get_setting("theme", "Dark"))

        i18n.lang = saved_lang
        theme.init_theme(saved_theme)

        super().__init__(fg_color=theme.BG_MAIN)

        self.title(i18n.t("app_title"))
        self.geometry(f"{theme.WINDOW_DEFAULT_WIDTH}x{theme.WINDOW_DEFAULT_HEIGHT}")
        self.minsize(theme.WINDOW_MIN_WIDTH, theme.WINDOW_MIN_HEIGHT)

        # تعيين أيقونة شريط المهام والنافذة
        self._set_window_icon()

        # إعداد مدير الإشعارات المنبثقة والمحرك الخلفي
        self.toast = ToastManager(self)
        self.downloader = DownloadManager(
            on_task_updated=self._on_task_updated_threadsafe,
            on_task_completed=self._on_task_completed_threadsafe,
            on_task_failed=self._on_task_failed_threadsafe,
        )

        self._current_tab = "new"
        self._tab_items: Dict[str, SidebarTabItem] = {}
        self._pages: Dict[str, ctk.CTkFrame] = {}
        self._tray_icon: Optional[object] = None
        self._enable_tray = enable_tray

        self._build_layout()
        self._bind_shortcuts()
        self._setup_drag_and_drop()

        if self._enable_tray:
            self._setup_system_tray()

        self.protocol("WM_DELETE_WINDOW", self._on_close_window)

        # عرض شاشة الترحيب عند أول تشغيل
        if bool(self.storage.get_setting("first_run", True)):
            self.after(350, self._show_first_run_welcome)

    def _build_layout(self) -> None:
        """بناء الشريط الجانبي الثابت (220px) ومنطقة المحتوى مع مراعاة اتجاه RTL/LTR."""
        for child in self.winfo_children():
            # الاحتفاظ بالإشعارات النشطة فقط إن وجدت
            child.destroy()

        self._tab_items.clear()
        self._pages.clear()

        # الشريط الجانبي الثابت بعرض 220px
        self.sidebar = ctk.CTkFrame(
            self,
            width=theme.SIDEBAR_WIDTH,
            corner_radius=0,
            fg_color=theme.BG_SIDEBAR,
            border_color=theme.BORDER_COLOR,
            border_width=theme.BORDER_WIDTH_THIN,
        )
        self.sidebar.pack(side=i18n.side_start, fill="y")
        self.sidebar.pack_propagate(False)

        # شعار واسم البرنامج أعلى الشريط الجانبي
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color=theme.COLOR_TRANSPARENT)
        brand_frame.pack(fill="x", padx=theme.SPACE_LG, pady=theme.SPACE_XXL)

        logo_pil = create_app_logo_pil(size=38)
        self._logo_ctk = ctk.CTkImage(
            light_image=logo_pil, dark_image=logo_pil, size=(38, 38)
        )
        logo_lbl = ctk.CTkLabel(brand_frame, text="", image=self._logo_ctk)
        logo_lbl.pack(
            side=i18n.side_start,
            padx=(0, theme.SPACE_SM) if not i18n.is_rtl else (theme.SPACE_SM, 0),
        )

        app_name_lbl = ctk.CTkLabel(
            brand_frame,
            text=i18n.t("app_title"),
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
            justify="left" if not i18n.is_rtl else "right",
            wraplength=144,
        )
        app_name_lbl.pack(side=i18n.side_start, fill="x", expand=True)

        # قائمة التبويبات الأربعة
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color=theme.COLOR_TRANSPARENT)
        nav_frame.pack(fill="x", padx=theme.SPACE_MD)

        tabs_spec = [
            ("new", i18n.t("tab_new"), "download"),
            ("active", i18n.t("tab_active"), "activity"),
            ("cutter", i18n.t("tab_cutter"), "scissors"),
            ("converter", i18n.t("tab_converter"), "refresh"),
            ("history", i18n.t("tab_history"), "history"),
            ("settings", i18n.t("tab_settings"), "settings"),
        ]

        for key, label, icon_name in tabs_spec:
            item = SidebarTabItem(
                nav_frame,
                tab_key=key,
                label_text=label,
                icon_name=icon_name,
                on_select=self.switch_tab,
            )
            item.pack(fill="x", pady=theme.SPACE_XS)
            self._tab_items[key] = item

        # أسفل الشريط الجانبي: زر تبديل الوضع الداكن/الفاتح، وزر اللغة، ورقم الإصدار
        bottom_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=theme.COLOR_TRANSPARENT,
        )
        bottom_frame.pack(
            side="bottom",
            fill="x",
            padx=theme.SPACE_LG,
            pady=theme.SPACE_LG,
        )

        divider = ctk.CTkFrame(
            bottom_frame,
            height=1,
            fg_color=theme.BORDER_COLOR,
        )
        divider.pack(fill="x", pady=(0, theme.SPACE_MD))

        controls_row = ctk.CTkFrame(bottom_frame, fg_color=theme.COLOR_TRANSPARENT)
        controls_row.pack(fill="x", pady=(0, theme.SPACE_SM))

        is_dark = str(self.storage.get_setting("theme", "Dark")).lower() == "dark"
        self.theme_toggle_btn = GhostIconButton(
            controls_row,
            icon_name="sun" if is_dark else "moon",
            tooltip=i18n.t("toggle_theme_tip"),
            command=self.toggle_theme,
        )
        self.theme_toggle_btn.pack(side=i18n.side_start, padx=2)

        self.lang_toggle_btn = ctk.CTkButton(
            controls_row,
            text=i18n.t("lang_label"),
            image=get_icon("globe", size=16, color_pair=theme.TEXT_SECONDARY),
            compound="right" if i18n.is_rtl else "left",
            height=theme.ICON_BUTTON_SIZE,
            corner_radius=theme.RADIUS_BUTTON,
            fg_color=theme.COLOR_TRANSPARENT,
            hover_color=theme.GHOST_HOVER,
            border_color=theme.BORDER_COLOR,
            border_width=theme.BORDER_WIDTH_THIN,
            text_color=theme.TEXT_PRIMARY,
            font=theme.get_small_font(i18n.lang, bold=True),
            command=self.toggle_language,
        )
        self.lang_toggle_btn.pack(side=i18n.side_end, fill="x", expand=True, padx=4)

        version_lbl = ctk.CTkLabel(
            bottom_frame,
            text=f"{theme.APP_VERSION}\n© Ahmed Hagag",
            font=theme.get_small_font(i18n.lang),
            text_color=theme.TEXT_MUTED,
            justify="center",
            cursor="hand2",
        )
        version_lbl.pack(fill="x", pady=(theme.SPACE_XS, 0))
        Tooltip(version_lbl, "Copyright © by Ahmed Hagag | ahmed.m.hagag22@gmail.com")

        # منطقة المحتوى الرئيسية
        self.content_area = ctk.CTkFrame(
            self,
            fg_color=theme.BG_MAIN,
            corner_radius=0,
        )
        self.content_area.pack(
            side=i18n.side_start,
            fill="both",
            expand=True,
            padx=theme.SPACE_LG,
            pady=theme.SPACE_LG,
        )

        # إنشاء الصفحات الأربع
        self.page_new = NewDownloadPage(
            self.content_area,
            storage=self.storage,
            downloader=self.downloader,
            toast=self.toast,
            on_download_started=lambda: self.switch_tab("active"),
        )
        self.page_active = ActiveDownloadsPage(
            self.content_area,
            downloader=self.downloader,
            toast=self.toast,
        )
        self.page_cutter = MusicCutterPage(
            self.content_area,
            storage=self.storage,
            toast=self.toast,
            on_cut_completed=lambda _p: self.switch_tab("history"),
        )
        self.page_converter = ConverterPage(
            self.content_area,
            storage=self.storage,
            toast=self.toast,
            on_converted=lambda _p: self.switch_tab("history"),
        )
        self.page_history = HistoryPage(
            self.content_area,
            storage=self.storage,
            toast=self.toast,
            on_cut_item=self.open_cutter_with_file,
            on_convert_item=self.open_converter_with_file,
        )
        self.page_settings = SettingsPage(
            self.content_area,
            storage=self.storage,
            toast=self.toast,
            on_toggle_theme=self.toggle_theme,
            on_toggle_language=self.toggle_language,
            on_show_welcome=self.show_welcome_dialog,
        )

        self._pages = {
            "new": self.page_new,
            "active": self.page_active,
            "cutter": self.page_cutter,
            "converter": self.page_converter,
            "history": self.page_history,
            "settings": self.page_settings,
        }

        self.switch_tab(self._current_tab, animate=False)

    # ==========================================================================
    # التنقل بين التبويبات مع تأثير انتقال سلس (Fade)
    # ==========================================================================

    def switch_tab(self, tab_key: str, animate: bool = True) -> None:
        if tab_key not in self._pages:
            return

        self._current_tab = tab_key
        for k, item in self._tab_items.items():
            item.set_active(k == tab_key)

        if tab_key != "cutter" and hasattr(self, "page_cutter"):
            self.page_cutter.stop_preview()

        for k, page in self._pages.items():
            if k != tab_key:
                page.pack_forget()

        if tab_key == "active":
            self.page_active.refresh_list()
        elif tab_key == "history":
            self.page_history.refresh_history()

        target_page = self._pages[tab_key]

        if animate and self.winfo_exists():
            # تأثير انتقال بصري سلس (Fade overlay)
            overlay = ctk.CTkFrame(
                self.content_area,
                fg_color=theme.BG_MAIN,
                corner_radius=0,
            )
            overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            target_page.pack(fill="both", expand=True)
            overlay.lift()
            self.after(theme.FADE_STEP_MS * 2, overlay.destroy)
        else:
            target_page.pack(fill="both", expand=True)

    # ==========================================================================
    # تبديل الثيم (داكن / فاتح) وتبديل اللغة (AR / EN مع انعكاس RTL)
    # ==========================================================================

    def toggle_theme(self) -> None:
        current = str(self.storage.get_setting("theme", "Dark"))
        new_mode = "Light" if current.lower() == "dark" else "Dark"
        self.storage.set_setting("theme", new_mode)
        ctk.set_appearance_mode(new_mode)

        is_dark = new_mode.lower() == "dark"
        new_icon = get_icon(
            "sun" if is_dark else "moon",
            size=18,
            color_pair=theme.TEXT_SECONDARY,
        )
        self.theme_toggle_btn._icon_img = new_icon
        self.theme_toggle_btn.configure(image=new_icon)
        if hasattr(self, "page_new"):
            self.page_new.drop_zone.refresh_theme()
        if hasattr(self, "page_settings"):
            self.page_settings.refresh_theme_button()

    def toggle_language(self) -> None:
        new_lang = "en" if i18n.lang == "ar" else "ar"
        i18n.lang = new_lang
        self.storage.set_setting("language", new_lang)
        self.title(i18n.t("app_title"))
        self._build_layout()

    # ==========================================================================
    # اختصارات لوحة المفاتيح والسحب والإفلات
    # ==========================================================================

    def _bind_shortcuts(self) -> None:
        """ربط Ctrl+V للصق والتحليل التلقائي، و Enter للبدء."""
        self.bind("<Control-v>", self._on_ctrl_v)
        self.bind("<Control-V>", self._on_ctrl_v)
        self.bind("<Return>", self._on_enter_key)

    def _on_ctrl_v(self, event: tk.Event) -> Optional[str]:
        # إذا كان التركيز داخل حقل الرابط نفسه، نحدث الحقل ونشغل التحليل التلقائي بعد اللصق
        focused = self.focus_get()
        if self._current_tab != "new":
            self.switch_tab("new")

        if focused is self.page_new.url_entry._entry:
            self.after(
                60,
                lambda: self.page_new.trigger_analyze()
                if self.storage.get_setting("auto_analyze_on_paste", True)
                and self.page_new.url_var.get().strip()
                else None,
            )
            return None

        self.page_new.paste_from_clipboard()
        return "break"

    def _on_enter_key(self, _event: tk.Event) -> None:
        if self._current_tab == "new":
            self.page_new.start_download_action()

    def _setup_drag_and_drop(self) -> None:
        if windnd is not None:
            try:
                windnd.hook_dropfiles(self, func=self._on_files_dropped)
            except Exception:
                pass

    def _on_files_dropped(self, items: list) -> None:
        if not items:
            return
        raw = items[0]
        text = raw.decode("utf-8", errors="ignore") if isinstance(raw, bytes) else str(raw)
        if self._current_tab != "new":
            self.switch_tab("new")
        self.page_new.handle_dropped_text(text)

    # ==========================================================================
    # تحديثات التحميلات من الخيوط الخلفية (Thread-Safe Callbacks)
    # ==========================================================================

    def _on_task_updated_threadsafe(self, task: DownloadTask) -> None:
        if self.winfo_exists():
            self.after(0, lambda: self.page_active.update_single_task(task))

    def _on_task_completed_threadsafe(self, task: DownloadTask) -> None:
        if not self.winfo_exists():
            return

        def _handle() -> None:
            self.storage.add_history_entry(
                title=task.title,
                url=task.url,
                channel=task.channel,
                media_type=task.media_type,
                quality=task.quality,
                fmt=task.fmt,
                save_path=task.save_dir,
                duration_str=task.duration_str,
            )
            self.page_active.update_single_task(task)
            self.page_history.refresh_history()
            self.toast.show(
                i18n.t("toast_download_completed", title=task.title[:35]),
                kind="success",
            )

        self.after(0, _handle)

    def _on_task_failed_threadsafe(self, task: DownloadTask) -> None:
        if not self.winfo_exists():
            return
        self.after(
            0,
            lambda: self.toast.show(
                i18n.t("toast_download_failed", title=task.title[:35]),
                kind="error",
            ),
        )

    # ==========================================================================
    # شاشة الترحيب وأيقونة System Tray
    # ==========================================================================

    def _show_first_run_welcome(self) -> None:
        def _mark_seen() -> None:
            self.storage.set_setting("first_run", False)

        WelcomeDialog(self, on_close=_mark_seen)

    def show_welcome_dialog(self) -> None:
        WelcomeDialog(self)

    def _setup_system_tray(self) -> None:
        """إنشاء أيقونة System Tray مع قائمة سريعة (فتح، إيقاف الكل، خروج)."""
        if pystray is None:
            return
        try:
            image = create_app_logo_pil(size=64)
            menu = pystray.Menu(
                pystray.MenuItem(
                    i18n.t("tray_open"),
                    lambda _icon, _item: self.after(0, self._restore_from_tray),
                    default=True,
                ),
                pystray.MenuItem(
                    i18n.t("tray_pause_all"),
                    lambda _icon, _item: self.after(0, self.downloader.pause_all),
                ),
                pystray.MenuItem(
                    i18n.t("tray_exit"),
                    lambda _icon, _item: self.after(0, self.quit_app),
                ),
            )
            self._tray_icon = pystray.Icon(
                "smart_downloader",
                image,
                i18n.t("app_title"),
                menu,
            )
            threading.Thread(target=self._tray_icon.run, daemon=True).start()
        except Exception:
            self._tray_icon = None

    def _set_window_icon(self) -> None:
        """تعيين أيقونة النافذة وشريط المهام الخاصة بالتطبيق."""
        if hasattr(sys, "_MEIPASS"):
            assets_dir = Path(sys._MEIPASS) / "assets"
        else:
            assets_dir = Path(__file__).resolve().parent.parent / "assets"

        ico_path = assets_dir / "app_icon.ico"
        png_path = assets_dir / "app_icon.png"

        # 1. تعيين ملف الأيقونة الرئيسي .ico (لشريط مهام ويندوز ونافذة التطبيق)
        if ico_path.exists():
            try:
                self.iconbitmap(default=str(ico_path))
            except Exception:
                try:
                    self.iconbitmap(str(ico_path))
                except Exception:
                    pass

        # 2. دعم إضافي عبر iconphoto للأنظمة والشاشات ذات الكثافة العالية
        if png_path.exists():
            try:
                img = Image.open(png_path)
                photo = ImageTk.PhotoImage(img)
                self._icon_photo_ref = photo  # حفظ المرجع لمنع التخلص التلقائي
                self.iconphoto(False, photo)
            except Exception:
                pass

    def _restore_from_tray(self) -> None:
        self.deiconify()
        self.lift()
        self.focus_force()

    def _on_close_window(self) -> None:
        if (
            self._tray_icon is not None
            and bool(self.storage.get_setting("minimize_to_tray", True))
        ):
            self.withdraw()
        else:
            self.quit_app()

    def open_cutter_with_file(self, file_path: str) -> None:
        """فتح تبويب تقطيع الوسائط وتحميل الملف الممرر مباشرةً."""
        self.switch_tab("cutter")
        if hasattr(self, "page_cutter"):
            self.page_cutter.load_file(file_path)

    def open_converter_with_file(self, file_path: str) -> None:
        """فتح تبويب تحويل الفيديو وتحميل الملف الممرر مباشرةً."""
        self.switch_tab("converter")
        if hasattr(self, "page_converter"):
            self.page_converter.load_file(file_path)

    def quit_app(self) -> None:
        if hasattr(self, "page_cutter"):
            self.page_cutter.stop_preview()
        if self._tray_icon is not None:
            try:
                self._tray_icon.stop()
            except Exception:
                pass
            self._tray_icon = None
        self.destroy()
