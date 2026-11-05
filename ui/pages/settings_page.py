"""
صفحة "الإعدادات" - ui/pages/settings_page.py
تضم:
- تخصيص المظهر (داكن/فاتح) واللغة (العربية/الإنجليزية).
- تخصيص القيم الافتراضية الذكية (مجلد الحفظ، الجودة الافتراضية، الصيغة الافتراضية).
- خيار التحليل التلقائي عند اللصق، والتصغير إلى System Tray، وعرض شاشة الترحيب.
"""

from tkinter import filedialog
from typing import Callable
import customtkinter as ctk

from core.storage import StorageManager
from ui import theme
from ui.i18n import i18n
from ui.components.buttons import PrimaryButton, SecondaryButton
from ui.components.feedback import ToastManager
from ui.components.widgets import ChipSelector, HoverCard


class SettingsPage(ctk.CTkScrollableFrame):
    """صفحة "الإعدادات"."""

    def __init__(
        self,
        master: object,
        storage: StorageManager,
        toast: ToastManager,
        on_toggle_theme: Callable[[], None],
        on_toggle_language: Callable[[], None],
        on_show_welcome: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color=theme.COLOR_TRANSPARENT, corner_radius=0)
        self.storage = storage
        self.toast = toast
        self.on_toggle_theme = on_toggle_theme
        self.on_toggle_language = on_toggle_language
        self.on_show_welcome = on_show_welcome

        self._build_ui()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color=theme.COLOR_TRANSPARENT)
        header.pack(fill="x", padx=theme.SPACE_LG, pady=(theme.SPACE_SM, theme.SPACE_LG))

        ctk.CTkLabel(
            header,
            text=i18n.t("page_settings_title"),
            font=theme.get_title_large_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        ).pack(fill="x")

        ctk.CTkLabel(
            header,
            text=i18n.t("page_settings_subtitle"),
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(2, 0))

        # ======================================================================
        # البطاقة 1: المظهر واللغة
        # ======================================================================
        appear_card = HoverCard(self)
        appear_card.pack(fill="x", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))

        ap_inner = ctk.CTkFrame(appear_card, fg_color=theme.COLOR_TRANSPARENT)
        ap_inner.pack(fill="x", padx=theme.SPACE_XL, pady=theme.SPACE_XL)

        ctk.CTkLabel(
            ap_inner,
            text=i18n.t("settings_appearance_section"),
            font=theme.get_section_title_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_MD))

        row1 = ctk.CTkFrame(ap_inner, fg_color=theme.COLOR_TRANSPARENT)
        row1.pack(fill="x", pady=theme.SPACE_XS)

        ctk.CTkLabel(
            row1,
            text=i18n.t("settings_theme_label"),
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
        ).pack(side=i18n.side_start)

        is_dark = str(self.storage.get_setting("theme", "Dark")).lower() == "dark"
        self.theme_btn = SecondaryButton(
            row1,
            text=i18n.t("theme_light") if is_dark else i18n.t("theme_dark"),
            icon_name="sun" if is_dark else "moon",
            width=155,
            command=self.on_toggle_theme,
        )
        self.theme_btn.pack(side=i18n.side_end)

        row2 = ctk.CTkFrame(ap_inner, fg_color=theme.COLOR_TRANSPARENT)
        row2.pack(fill="x", pady=(theme.SPACE_MD, 0))

        ctk.CTkLabel(
            row2,
            text=i18n.t("settings_lang_label"),
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
        ).pack(side=i18n.side_start)

        SecondaryButton(
            row2,
            text=i18n.t("lang_label"),
            icon_name="globe",
            width=155,
            command=self.on_toggle_language,
        ).pack(side=i18n.side_end)

        # ======================================================================
        # البطاقة 2: الإعدادات الافتراضية للتحميل
        # ======================================================================
        def_card = HoverCard(self)
        def_card.pack(fill="x", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))

        df_inner = ctk.CTkFrame(def_card, fg_color=theme.COLOR_TRANSPARENT)
        df_inner.pack(fill="x", padx=theme.SPACE_XL, pady=theme.SPACE_XL)

        ctk.CTkLabel(
            df_inner,
            text=i18n.t("settings_defaults_section"),
            font=theme.get_section_title_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_MD))

        # مجلد الحفظ الافتراضي
        ctk.CTkLabel(
            df_inner,
            text=i18n.t("settings_default_path"),
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_XS))

        path_row = ctk.CTkFrame(df_inner, fg_color=theme.COLOR_TRANSPARENT)
        path_row.pack(fill="x", pady=(0, theme.SPACE_LG))

        self.dir_var = ctk.StringVar(value=str(self.storage.get_setting("download_dir")))
        ctk.CTkEntry(
            path_row,
            textvariable=self.dir_var,
            state="readonly",
            height=theme.BUTTON_HEIGHT,
            corner_radius=theme.RADIUS_INPUT,
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_COLOR,
            text_color=theme.TEXT_PRIMARY,
            font=theme.get_body_font(i18n.lang),
        ).pack(
            side=i18n.side_start,
            fill="x",
            expand=True,
            padx=(0, theme.SPACE_SM) if not i18n.is_rtl else (theme.SPACE_SM, 0),
        )

        SecondaryButton(
            path_row,
            text=i18n.t("btn_change_folder"),
            icon_name="folder",
            width=115,
            command=self._pick_default_dir,
        ).pack(side=i18n.side_start)

        # الجودة الافتراضية
        ctk.CTkLabel(
            df_inner,
            text=i18n.t("settings_default_quality"),
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_XS))

        self.q_chips = ChipSelector(
            df_inner,
            primary_options=["4K", "1080p", "720p", "480p"],
            default_value=str(self.storage.get_setting("default_quality", "1080p")),
        )
        self.q_chips.pack(fill="x", pady=(0, theme.SPACE_MD))

        # الصيغة الافتراضية
        ctk.CTkLabel(
            df_inner,
            text=i18n.t("settings_default_format"),
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_XS))

        self.f_chips = ChipSelector(
            df_inner,
            primary_options=["MP4", "MKV", "WEBM"],
            default_value=str(self.storage.get_setting("default_format", "MP4")),
        )
        self.f_chips.pack(fill="x", pady=(0, theme.SPACE_LG))

        # خيارات السلوك
        self.auto_analyze_var = ctk.BooleanVar(
            value=bool(self.storage.get_setting("auto_analyze_on_paste", True))
        )
        ctk.CTkCheckBox(
            df_inner,
            text=i18n.t("settings_auto_analyze"),
            variable=self.auto_analyze_var,
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            fg_color=theme.PRIMARY_COLOR,
            hover_color=theme.PRIMARY_HOVER,
            border_color=theme.BORDER_COLOR,
        ).pack(anchor=i18n.align_start, pady=theme.SPACE_XS)

        self.tray_var = ctk.BooleanVar(
            value=bool(self.storage.get_setting("minimize_to_tray", True))
        )
        ctk.CTkCheckBox(
            df_inner,
            text=i18n.t("settings_minimize_tray"),
            variable=self.tray_var,
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            fg_color=theme.PRIMARY_COLOR,
            hover_color=theme.PRIMARY_HOVER,
            border_color=theme.BORDER_COLOR,
        ).pack(anchor=i18n.align_start, pady=(theme.SPACE_XS, theme.SPACE_XL))

        btn_row = ctk.CTkFrame(df_inner, fg_color=theme.COLOR_TRANSPARENT)
        btn_row.pack(fill="x")

        PrimaryButton(
            btn_row,
            text=i18n.t("btn_save_settings"),
            icon_name="check",
            width=165,
            command=self._save_settings,
        ).pack(side=i18n.side_start)

        SecondaryButton(
            btn_row,
            text=i18n.t("btn_show_welcome"),
            icon_name="info",
            width=165,
            command=self.on_show_welcome,
        ).pack(
            side=i18n.side_start,
            padx=(theme.SPACE_SM, 0) if not i18n.is_rtl else (0, theme.SPACE_SM),
        )

        # ======================================================================
        # البطاقة 3: معلومات المطور وحقوق النشر
        # ======================================================================
        about_card = HoverCard(self)
        about_card.pack(fill="x", padx=theme.SPACE_LG, pady=(0, theme.SPACE_XL))

        about_inner = ctk.CTkFrame(about_card, fg_color=theme.COLOR_TRANSPARENT)
        about_inner.pack(fill="x", padx=theme.SPACE_XL, pady=theme.SPACE_XL)

        ctk.CTkLabel(
            about_inner,
            text=i18n.t("settings_about_section"),
            font=theme.get_section_title_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_MD))

        dev_row = ctk.CTkFrame(about_inner, fg_color=theme.COLOR_TRANSPARENT)
        dev_row.pack(fill="x", pady=(0, theme.SPACE_SM))

        ctk.CTkLabel(
            dev_row,
            text=i18n.t("dev_copyright"),
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.PRIMARY_COLOR,
            anchor=i18n.align_start,
        ).pack(side=i18n.side_start)

        contact_row = ctk.CTkFrame(about_inner, fg_color=theme.COLOR_TRANSPARENT)
        contact_row.pack(fill="x", pady=(theme.SPACE_XS, 0))

        ctk.CTkLabel(
            contact_row,
            text=f"{i18n.t('dev_contact_label')} {i18n.t('dev_contact')}",
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(side=i18n.side_start)

        SecondaryButton(
            contact_row,
            text=i18n.t("btn_copy_email"),
            icon_name="link",
            width=120,
            command=self._copy_email,
        ).pack(
            side=i18n.side_end,
            padx=(theme.SPACE_SM, 0) if not i18n.is_rtl else (0, theme.SPACE_SM),
        )

    def _copy_email(self) -> None:
        """نسخ البريد الإلكتروني للمطور إلى الحافظة."""
        try:
            self.clipboard_clear()
            self.clipboard_append("ahmed.m.hagag22@gmail.com")
            self.toast.show(i18n.t("toast_email_copied"), kind="success")
        except Exception:
            pass

    def refresh_theme_button(self) -> None:
        from ui.icons import get_icon
        is_dark = str(self.storage.get_setting("theme", "Dark")).lower() == "dark"
        new_text = i18n.t("theme_light") if is_dark else i18n.t("theme_dark")
        new_icon = "sun" if is_dark else "moon"
        self.theme_btn._original_text = new_text
        self.theme_btn._icon_img = get_icon(new_icon, size=18, color_pair=theme.TEXT_PRIMARY)
        self.theme_btn.configure(text=new_text, image=self.theme_btn._icon_img)

    def _pick_default_dir(self) -> None:
        chosen = filedialog.askdirectory(
            parent=self.winfo_toplevel(),
            initialdir=self.dir_var.get(),
            mustexist=False,
        )
        if chosen:
            self.dir_var.set(chosen)
            self.storage.set_setting("download_dir", chosen)

    def _save_settings(self) -> None:
        self.storage.set_setting("download_dir", self.dir_var.get(), save=False)
        self.storage.set_setting("default_quality", self.q_chips.value, save=False)
        self.storage.set_setting("default_format", self.f_chips.value, save=False)
        self.storage.set_setting("auto_analyze_on_paste", self.auto_analyze_var.get(), save=False)
        self.storage.set_setting("minimize_to_tray", self.tray_var.get(), save=True)
        self.toast.show(i18n.t("toast_settings_saved"), kind="success")
