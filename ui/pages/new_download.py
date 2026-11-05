"""
صفحة "تحميل جديد" (الصفحة الرئيسية) - ui/pages/new_download.py
تضم:
- حقل رابط كبير بحدود مستديرة وأيقونة رابط بداخله، وبجانبه زر "لصق" وزر "تحليل" بارز.
- منطقة سحب وإفلات (Drag & Drop) بحدود منقطة تظهر عند عدم وجود رابط، مع أيقونة ورسالة "اسحبي الرابط هنا أو الصقيه".
- بطاقة معاينة بعد التحليل: الصورة المصغرة بزوايا مستديرة على جانب، والعنوان والقناة والمدة على الجانب الآخر.
- مفتاح مقسّم كبير (فيديو | صوت) يغيّر الخيارات أسفله بحركة سلسة.
- شرائح (Chips) قابلة للاختيار للجودة والصيغة مع قائمة "المزيد".
- اختيار مكان الحفظ كحقل للقراءة فقط مع زر "تغيير" وأيقونة مجلد.
- قسم قابل للطي "خيارات متقدمة" مخفي افتراضياً.
- زر "ابدأ التحميل" كبير وبارز بعرض كامل البطاقة.
"""

import tkinter as tk
from tkinter import filedialog
from typing import Callable, Optional
import customtkinter as ctk

from core.downloader import (
    DownloadManager,
    MediaInfo,
    create_rounded_thumbnail,
)
from core.storage import StorageManager
from ui import theme
from ui.i18n import i18n
from ui.icons import get_icon
from ui.components.buttons import GhostIconButton, PrimaryButton, SecondaryButton
from ui.components.dialogs import PlaylistDialog
from ui.components.feedback import ToastManager
from ui.components.widgets import (
    ChipSelector,
    CollapsibleSection,
    HoverCard,
    MediaTypeSegmentedSwitch,
)


class DashedDropZone(tk.Canvas):
    """
    منطقة سحب وإفلات (Drag & Drop) بحدود منقطة حقيقية وأيقونة سحابة ورسالة
    "اسحبي الرابط هنا أو الصقيه".
    تظهر عند عدم وجود رابط وتختفي عند كتابة أو لصق رابط.
    """

    def __init__(
        self,
        master: object,
        on_click_paste: Callable[[], None],
        height: int = 126,
    ) -> None:
        self._bg_hex = theme.resolve_color(theme.BG_CARD)
        super().__init__(
            master,
            height=height,
            bg=self._bg_hex,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.on_click_paste = on_click_paste
        self._hovered = False

        self.bind("<Configure>", self._redraw)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", lambda _e: self.on_click_paste())

    def _on_enter(self, _event: object = None) -> None:
        self._hovered = True
        self._redraw()

    def _on_leave(self, _event: object = None) -> None:
        self._hovered = False
        self._redraw()

    def refresh_theme(self) -> None:
        self._bg_hex = theme.resolve_color(theme.BG_CARD)
        self.configure(bg=self._bg_hex)
        self._redraw()

    def _redraw(self, _event: object = None) -> None:
        self.delete("all")
        w = max(200, self.winfo_width())
        h = max(90, self.winfo_height())

        pad = 6
        border_col = (
            theme.COLOR_PRIMARY
            if self._hovered
            else theme.resolve_color(theme.BORDER_COLOR)
        )
        fill_col = (
            theme.resolve_color(theme.PRIMARY_TINT)
            if self._hovered
            else theme.resolve_color(theme.BG_INPUT)
        )

        # خلفية منطقة السحب والإفلات
        self.create_rectangle(
            pad,
            pad,
            w - pad,
            h - pad,
            fill=fill_col,
            outline=border_col,
            width=2,
            dash=(8, 6),
        )

        cx = w // 2
        # رمز السحب والإفلات والنص التوجيهي
        title_col = (
            theme.COLOR_PRIMARY
            if self._hovered
            else theme.resolve_color(theme.TEXT_PRIMARY)
        )
        sub_col = theme.resolve_color(theme.TEXT_SECONDARY)

        self.create_text(
            cx,
            h // 2 - 14,
            text=f"⬇  {i18n.t('drag_drop_title')}",
            fill=title_col,
            font=(theme.get_font_family(i18n.lang), theme.FONT_SIZE_BODY, "bold"),
        )
        self.create_text(
            cx,
            h // 2 + 16,
            text=i18n.t("drag_drop_subtitle"),
            fill=sub_col,
            font=(theme.get_font_family(i18n.lang), theme.FONT_SIZE_SMALL),
        )


class NewDownloadPage(ctk.CTkScrollableFrame):
    """صفحة "تحميل جديد" (الصفحة الرئيسية)."""

    VIDEO_PRIMARY_QUALITIES = ["4K", "1080p", "720p"]
    VIDEO_MORE_QUALITIES = ["1440p", "480p", "360p", "240p"]
    VIDEO_PRIMARY_FORMATS = ["MP4", "MKV", "WEBM"]
    VIDEO_MORE_FORMATS = ["MOV", "AVI", "FLV"]

    AUDIO_PRIMARY_QUALITIES = ["320kbps", "256kbps", "192kbps"]
    AUDIO_MORE_QUALITIES = ["128kbps", "96kbps", "64kbps"]
    AUDIO_PRIMARY_FORMATS = ["MP3", "M4A", "WAV"]
    AUDIO_MORE_FORMATS = ["FLAC", "OPUS", "AAC"]

    def __init__(
        self,
        master: object,
        storage: StorageManager,
        downloader: DownloadManager,
        toast: ToastManager,
        on_download_started: Callable[[], None],
    ) -> None:
        super().__init__(
            master,
            fg_color=theme.COLOR_TRANSPARENT,
            corner_radius=0,
        )
        self.storage = storage
        self.downloader = downloader
        self.toast = toast
        self.on_download_started = on_download_started

        self.current_media: Optional[MediaInfo] = None
        self._thumb_ctk_img: Optional[ctk.CTkImage] = None
        self._is_analyzing: bool = False
        self._start_after_analyze: bool = False

        self._build_ui()

    def _build_ui(self) -> None:
        # رأس الصفحة
        header = ctk.CTkFrame(self, fg_color=theme.COLOR_TRANSPARENT)
        header.pack(fill="x", padx=theme.SPACE_LG, pady=(theme.SPACE_SM, theme.SPACE_LG))

        ctk.CTkLabel(
            header,
            text=i18n.t("page_new_title"),
            font=theme.get_title_large_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        ).pack(fill="x")

        ctk.CTkLabel(
            header,
            text=i18n.t("page_new_subtitle"),
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(2, 0))

        # ======================================================================
        # البطاقة 1: حقل الرابط + أزرار لصق وتحليل + منطقة السحب والإفلات
        # ======================================================================
        self.url_card = HoverCard(self)
        self.url_card.pack(fill="x", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))

        url_inner = ctk.CTkFrame(self.url_card, fg_color=theme.COLOR_TRANSPARENT)
        url_inner.pack(fill="x", padx=theme.SPACE_XL, pady=theme.SPACE_XL)

        bar_row = ctk.CTkFrame(url_inner, fg_color=theme.COLOR_TRANSPARENT)
        bar_row.pack(fill="x")

        # حاوية حقل الرابط الكبير بحدود مستديرة وأيقونة رابط بداخله
        self.input_container = ctk.CTkFrame(
            bar_row,
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_COLOR,
            border_width=theme.BORDER_WIDTH_THIN,
            corner_radius=theme.RADIUS_INPUT,
            height=theme.INPUT_HEIGHT,
        )
        self.input_container.pack(
            side=i18n.side_start,
            fill="x",
            expand=True,
            padx=(0, theme.SPACE_SM) if not i18n.is_rtl else (theme.SPACE_SM, 0),
        )

        link_icon_lbl = ctk.CTkLabel(
            self.input_container,
            text="",
            image=get_icon("link", size=20, color_pair=theme.PRIMARY_COLOR),
        )
        link_icon_lbl.pack(
            side=i18n.side_start,
            padx=(theme.SPACE_MD, theme.SPACE_XS)
            if not i18n.is_rtl
            else (theme.SPACE_XS, theme.SPACE_MD),
        )

        self.url_var = ctk.StringVar()
        self.url_var.trace_add("write", self._on_url_changed)

        self.url_entry = ctk.CTkEntry(
            self.input_container,
            textvariable=self.url_var,
            placeholder_text=i18n.t("url_placeholder"),
            height=theme.BUTTON_HEIGHT,
            border_width=0,
            fg_color=theme.COLOR_TRANSPARENT,
            text_color=theme.TEXT_PRIMARY,
            placeholder_text_color=theme.TEXT_MUTED,
            font=theme.get_body_font(i18n.lang),
            justify=i18n.justify,
        )
        self.url_entry.pack(side=i18n.side_start, fill="x", expand=True, padx=theme.SPACE_XS)

        self.clear_btn = GhostIconButton(
            self.input_container,
            icon_name="x",
            tooltip=i18n.t("btn_clear_tip"),
            size=32,
            command=self.clear_url,
        )

        # زر لصق (Secondary)
        self.paste_btn = SecondaryButton(
            bar_row,
            text=i18n.t("btn_paste"),
            icon_name="paste",
            tooltip=i18n.t("btn_paste_tip"),
            width=105,
            height=theme.INPUT_HEIGHT,
            command=self.paste_from_clipboard,
        )
        self.paste_btn.pack(
            side=i18n.side_start,
            padx=(0, theme.SPACE_SM) if not i18n.is_rtl else (theme.SPACE_SM, 0),
        )

        # زر تحليل بارز (Primary)
        self.analyze_btn = PrimaryButton(
            bar_row,
            text=i18n.t("btn_analyze"),
            icon_name="sparkles",
            tooltip=i18n.t("btn_analyze_tip"),
            width=125,
            height=theme.INPUT_HEIGHT,
            command=self.trigger_analyze,
        )
        self.analyze_btn.pack(side=i18n.side_start)

        # منطقة السحب والإفلات بحدود منقطة (تظهر عند عدم وجود رابط)
        self.drop_zone = DashedDropZone(
            url_inner,
            on_click_paste=self.paste_from_clipboard,
            height=115,
        )
        self.drop_zone.pack(fill="x", pady=(theme.SPACE_LG, 0))

        # ======================================================================
        # البطاقة 2: بطاقة المعاينة (تظهر بعد التحليل)
        # ======================================================================
        self.preview_card = HoverCard(self)
        self._build_preview_card()

        # ======================================================================
        # البطاقة 3: إعدادات الجودة والصيغة ومكان الحفظ وزر البدء
        # ======================================================================
        self.options_card = HoverCard(self)
        self.options_card.pack(fill="x", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))

        opt_inner = ctk.CTkFrame(self.options_card, fg_color=theme.COLOR_TRANSPARENT)
        opt_inner.pack(fill="x", padx=theme.SPACE_XL, pady=theme.SPACE_XL)

        # مفتاح مقسّم كبير (فيديو | صوت)
        ctk.CTkLabel(
            opt_inner,
            text=i18n.t("media_type_label"),
            font=theme.get_section_title_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_SM))

        self.media_switch = MediaTypeSegmentedSwitch(
            opt_inner,
            default_mode="video",
            on_change=self._on_media_mode_changed,
        )
        self.media_switch.pack(fill="x", pady=(0, theme.SPACE_LG))

        # حاوية الشرائح (تتغير بحركة سلسة عند التبديل بين فيديو وصوت)
        self.chips_container = ctk.CTkFrame(opt_inner, fg_color=theme.COLOR_TRANSPARENT)
        self.chips_container.pack(fill="x", pady=(0, theme.SPACE_LG))

        # شرائح الجودة
        ctk.CTkLabel(
            self.chips_container,
            text=i18n.t("quality_label"),
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_XS))

        default_q = str(self.storage.get_setting("default_quality", "1080p"))
        self.quality_chips = ChipSelector(
            self.chips_container,
            primary_options=self.VIDEO_PRIMARY_QUALITIES,
            more_options=self.VIDEO_MORE_QUALITIES,
            default_value=default_q,
        )
        self.quality_chips.pack(fill="x", pady=(0, theme.SPACE_MD))

        # شرائح الصيغة
        ctk.CTkLabel(
            self.chips_container,
            text=i18n.t("format_label"),
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_XS))

        default_f = str(self.storage.get_setting("default_format", "MP4"))
        self.format_chips = ChipSelector(
            self.chips_container,
            primary_options=self.VIDEO_PRIMARY_FORMATS,
            more_options=self.VIDEO_MORE_FORMATS,
            default_value=default_f,
        )
        self.format_chips.pack(fill="x")

        # اختيار مكان الحفظ كحقل للقراءة فقط مع زر "تغيير" وأيقونة مجلد
        ctk.CTkLabel(
            opt_inner,
            text=i18n.t("save_path_label"),
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_XS))

        path_row = ctk.CTkFrame(opt_inner, fg_color=theme.COLOR_TRANSPARENT)
        path_row.pack(fill="x", pady=(0, theme.SPACE_LG))

        path_box = ctk.CTkFrame(
            path_row,
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_COLOR,
            border_width=theme.BORDER_WIDTH_THIN,
            corner_radius=theme.RADIUS_INPUT,
            height=theme.BUTTON_HEIGHT,
        )
        path_box.pack(
            side=i18n.side_start,
            fill="x",
            expand=True,
            padx=(0, theme.SPACE_SM) if not i18n.is_rtl else (theme.SPACE_SM, 0),
        )

        folder_ic = ctk.CTkLabel(
            path_box,
            text="",
            image=get_icon("folder", size=18, color_pair=theme.ACCENT_COLOR),
        )
        folder_ic.pack(
            side=i18n.side_start,
            padx=(theme.SPACE_MD, theme.SPACE_XS)
            if not i18n.is_rtl
            else (theme.SPACE_XS, theme.SPACE_MD),
        )

        self.save_path_var = ctk.StringVar(
            value=str(self.storage.get_setting("download_dir"))
        )
        self.save_path_entry = ctk.CTkEntry(
            path_box,
            textvariable=self.save_path_var,
            state="readonly",
            border_width=0,
            fg_color=theme.COLOR_TRANSPARENT,
            text_color=theme.TEXT_PRIMARY,
            font=theme.get_body_font(i18n.lang),
        )
        self.save_path_entry.pack(side=i18n.side_start, fill="x", expand=True, padx=theme.SPACE_XS)

        # السماح بالنقر على حقل المسار أو أيقونة المجلد لاختيار المجلد أيضاً
        path_box.bind("<Button-1>", lambda _e: self._choose_directory(), add="+")
        folder_ic.bind("<Button-1>", lambda _e: self._choose_directory(), add="+")
        self.save_path_entry.bind("<Button-1>", lambda _e: self._choose_directory(), add="+")

        self.change_dir_btn = SecondaryButton(
            path_row,
            text=i18n.t("btn_change_folder"),
            icon_name="folder",
            tooltip=i18n.t("btn_change_folder_tip"),
            width=115,
            command=self._choose_directory,
        )
        self.change_dir_btn.pack(side=i18n.side_start)

        # الخيارات المتقدمة مخفية داخل قسم قابل للطي "خيارات متقدمة"
        self.advanced_section = CollapsibleSection(
            opt_inner,
            title=i18n.t("advanced_options"),
        )
        self.advanced_section.pack(fill="x", pady=(0, theme.SPACE_XL))
        self._build_advanced_options(self.advanced_section.content_frame)

        # زر "ابدأ التحميل" كبير وبارز بعرض كامل البطاقة
        self.start_btn = PrimaryButton(
            opt_inner,
            text=i18n.t("btn_start_download"),
            icon_name="download",
            height=theme.INPUT_HEIGHT,
            command=self.start_download_action,
        )
        self.start_btn.pack(fill="x")

    def _build_preview_card(self) -> None:
        """بناء عناصر بطاقة المعاينة (الصورة المصغرة على جانب والبيانات على الجانب الآخر)."""
        inner = ctk.CTkFrame(self.preview_card, fg_color=theme.COLOR_TRANSPARENT)
        inner.pack(fill="x", padx=theme.SPACE_XL, pady=theme.SPACE_LG)

        # الصورة المصغرة بزوايا مستديرة
        thumb_pil = create_rounded_thumbnail(None, size=(168, 96))
        self._thumb_ctk_img = ctk.CTkImage(
            light_image=thumb_pil, dark_image=thumb_pil, size=(168, 96)
        )
        self.thumb_label = ctk.CTkLabel(inner, text="", image=self._thumb_ctk_img)
        self.thumb_label.pack(
            side=i18n.side_start,
            padx=(0, theme.SPACE_LG) if not i18n.is_rtl else (theme.SPACE_LG, 0),
        )

        # تفاصيل العنوان والقناة والمدة على الجانب الآخر
        meta_frame = ctk.CTkFrame(inner, fg_color=theme.COLOR_TRANSPARENT)
        meta_frame.pack(side=i18n.side_start, fill="both", expand=True)

        self.preview_title_lbl = ctk.CTkLabel(
            meta_frame,
            text="",
            font=theme.get_section_title_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
            justify=i18n.justify,
            wraplength=540,
        )
        self.preview_title_lbl.pack(fill="x", pady=(0, theme.SPACE_XS))

        info_row = ctk.CTkFrame(meta_frame, fg_color=theme.COLOR_TRANSPARENT)
        info_row.pack(fill="x", pady=(0, theme.SPACE_SM))

        self.preview_channel_lbl = ctk.CTkLabel(
            info_row,
            text="",
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
        )
        self.preview_channel_lbl.pack(
            side=i18n.side_start,
            padx=(0, theme.SPACE_LG) if not i18n.is_rtl else (theme.SPACE_LG, 0),
        )

        self.preview_duration_lbl = ctk.CTkLabel(
            info_row,
            text="",
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.ACCENT_COLOR,
        )
        self.preview_duration_lbl.pack(side=i18n.side_start)

        # زر اختيار فيديوهات قائمة التشغيل (يظهر فقط إذا كان الرابط قائمة تشغيل)
        self.playlist_btn = SecondaryButton(
            meta_frame,
            text=i18n.t("preview_choose_videos"),
            icon_name="list_video",
            height=theme.BUTTON_SMALL_HEIGHT,
            width=170,
            command=self._open_playlist_dialog,
        )

    def _build_advanced_options(self, parent: ctk.CTkFrame) -> None:
        self.subtitles_var = ctk.BooleanVar(value=False)
        self.embed_thumb_var = ctk.BooleanVar(value=False)
        self.speed_limit_var = ctk.StringVar(value="0")
        self.filename_tpl_var = ctk.StringVar(value="%(title)s.%(ext)s")

        cb_row = ctk.CTkFrame(parent, fg_color=theme.COLOR_TRANSPARENT)
        cb_row.pack(fill="x", pady=theme.SPACE_XS)

        ctk.CTkCheckBox(
            cb_row,
            text=i18n.t("opt_subtitles"),
            variable=self.subtitles_var,
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            fg_color=theme.PRIMARY_COLOR,
            hover_color=theme.PRIMARY_HOVER,
            border_color=theme.BORDER_COLOR,
        ).pack(
            side=i18n.side_start,
            padx=(0, theme.SPACE_XL) if not i18n.is_rtl else (theme.SPACE_XL, 0),
        )

        ctk.CTkCheckBox(
            cb_row,
            text=i18n.t("opt_embed_thumbnail"),
            variable=self.embed_thumb_var,
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            fg_color=theme.PRIMARY_COLOR,
            hover_color=theme.PRIMARY_HOVER,
            border_color=theme.BORDER_COLOR,
        ).pack(side=i18n.side_start)

        extra_row = ctk.CTkFrame(parent, fg_color=theme.COLOR_TRANSPARENT)
        extra_row.pack(fill="x", pady=(theme.SPACE_SM, 0))

        ctk.CTkLabel(
            extra_row,
            text=i18n.t("opt_speed_limit"),
            font=theme.get_small_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
        ).pack(
            side=i18n.side_start,
            padx=(0, theme.SPACE_SM) if not i18n.is_rtl else (theme.SPACE_SM, 0),
        )

        ctk.CTkEntry(
            extra_row,
            textvariable=self.speed_limit_var,
            width=90,
            height=32,
            corner_radius=theme.RADIUS_CHIP,
            fg_color=theme.BG_CARD,
            border_color=theme.BORDER_COLOR,
            text_color=theme.TEXT_PRIMARY,
            font=theme.get_small_font(i18n.lang),
        ).pack(
            side=i18n.side_start,
            padx=(0, theme.SPACE_LG) if not i18n.is_rtl else (theme.SPACE_LG, 0),
        )

        ctk.CTkLabel(
            extra_row,
            text=i18n.t("opt_custom_filename"),
            font=theme.get_small_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
        ).pack(
            side=i18n.side_start,
            padx=(0, theme.SPACE_SM) if not i18n.is_rtl else (theme.SPACE_SM, 0),
        )

        ctk.CTkEntry(
            extra_row,
            textvariable=self.filename_tpl_var,
            width=180,
            height=32,
            corner_radius=theme.RADIUS_CHIP,
            fg_color=theme.BG_CARD,
            border_color=theme.BORDER_COLOR,
            text_color=theme.TEXT_PRIMARY,
            font=theme.get_small_font(i18n.lang),
        ).pack(side=i18n.side_start, fill="x", expand=True)

    # ==========================================================================
    # التفاعلات والأحداث
    # ==========================================================================

    def _on_url_changed(self, *_args: object) -> None:
        val = self.url_var.get().strip()
        if val:
            self.drop_zone.pack_forget()
            self.clear_btn.pack(side=i18n.side_end, padx=theme.SPACE_XS)
        else:
            self.clear_btn.pack_forget()
            self.preview_card.pack_forget()
            self.current_media = None
            self.drop_zone.pack(fill="x", pady=(theme.SPACE_LG, 0))

    def clear_url(self) -> None:
        self.url_var.set("")

    def handle_dropped_text(self, text: str) -> None:
        cleaned = text.strip().splitlines()[0].strip() if text else ""
        if cleaned:
            self.url_var.set(cleaned)
            if self.storage.get_setting("auto_analyze_on_paste", True):
                self.trigger_analyze()

    def paste_from_clipboard(self) -> None:
        try:
            clip = self.winfo_toplevel().clipboard_get().strip()
        except Exception:
            clip = ""

        if not clip:
            self.toast.show(i18n.t("toast_empty_clipboard"), kind="warning")
            return

        self.url_var.set(clip)
        self.toast.show(i18n.t("toast_pasted"), kind="info")
        if self.storage.get_setting("auto_analyze_on_paste", True):
            self.trigger_analyze()

    def trigger_analyze(self) -> None:
        url = self.url_var.get().strip()
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            self.toast.show(i18n.t("toast_invalid_url"), kind="error")
            return

        if self._is_analyzing:
            return

        self._is_analyzing = True
        self.analyze_btn.set_loading(True, i18n.t("btn_analyze_loading"))

        def _on_ok(info: MediaInfo) -> None:
            if self.winfo_exists():
                self.after(0, lambda: self._apply_analyzed_media(info))

        def _on_err(_msg: str) -> None:
            if self.winfo_exists():
                self.after(0, self._handle_analyze_error)

        self.downloader.analyze_url_async(url, _on_ok, _on_err)

    def _apply_analyzed_media(
        self,
        info: MediaInfo,
        open_playlist_modal: bool = True,
    ) -> None:
        self._is_analyzing = False
        self.analyze_btn.set_loading(False)
        self.start_btn.set_loading(False)
        self.current_media = info

        if info.thumbnail_image:
            self._thumb_ctk_img = ctk.CTkImage(
                light_image=info.thumbnail_image,
                dark_image=info.thumbnail_image,
                size=(168, 96),
            )
            self.thumb_label.configure(image=self._thumb_ctk_img)

        self.preview_title_lbl.configure(text=info.title)
        self.preview_channel_lbl.configure(
            text=f"{i18n.t('preview_channel')} {info.channel}"
        )
        self.preview_duration_lbl.configure(
            text=f"{i18n.t('preview_duration')} {info.duration_str}"
        )

        if info.is_playlist and info.playlist_entries:
            count = len(info.selected_indices)
            total = len(info.playlist_entries)
            self.playlist_btn.configure(
                text=f"{i18n.t('preview_choose_videos')} ({count}/{total})"
            )
            self.playlist_btn.pack(anchor=i18n.align_start, pady=(theme.SPACE_XS, 0))
            if open_playlist_modal and not self._start_after_analyze:
                self._open_playlist_dialog()
        else:
            self.playlist_btn.pack_forget()

        # إظهار بطاقة المعاينة بين بطاقة الرابط وبطاقة الخيارات
        self.preview_card.pack(
            fill="x",
            padx=theme.SPACE_LG,
            pady=(0, theme.SPACE_LG),
            before=self.options_card,
        )
        self.toast.show(i18n.t("toast_analyze_success"), kind="success")

        if self._start_after_analyze:
            self._start_after_analyze = False
            self._dispatch_download(info)

    def _handle_analyze_error(self) -> None:
        self._is_analyzing = False
        self._start_after_analyze = False
        self.analyze_btn.set_loading(False)
        self.start_btn.set_loading(False)
        self.toast.show(i18n.t("toast_analyze_error"), kind="error")

    def _open_playlist_dialog(self) -> None:
        if not self.current_media or not self.current_media.playlist_entries:
            return

        def _on_selected(indices: list[int]) -> None:
            if self.current_media:
                self.current_media.selected_indices = indices
                total = len(self.current_media.playlist_entries)
                self.playlist_btn.configure(
                    text=f"{i18n.t('preview_choose_videos')} ({len(indices)}/{total})"
                )

        PlaylistDialog(
            self.winfo_toplevel(),  # type: ignore[arg-type]
            entries=self.current_media.playlist_entries,
            selected_indices=self.current_media.selected_indices,
            on_confirm=_on_selected,
        )

    def _on_media_mode_changed(self, mode: str) -> None:
        """التبديل السلس لشرائح الجودة والصيغة عند تغيير المفتاح المقسّم (فيديو | صوت)."""
        # حركة انتقال بصرية سريعة
        self.chips_container.pack_forget()

        def _swap() -> None:
            if mode == "video":
                self.quality_chips.set_options(
                    self.VIDEO_PRIMARY_QUALITIES,
                    self.VIDEO_MORE_QUALITIES,
                    selected=str(self.storage.get_setting("default_quality", "1080p")),
                )
                self.format_chips.set_options(
                    self.VIDEO_PRIMARY_FORMATS,
                    self.VIDEO_MORE_FORMATS,
                    selected=str(self.storage.get_setting("default_format", "MP4")),
                )
            else:
                self.quality_chips.set_options(
                    self.AUDIO_PRIMARY_QUALITIES,
                    self.AUDIO_MORE_QUALITIES,
                    selected="320kbps",
                )
                self.format_chips.set_options(
                    self.AUDIO_PRIMARY_FORMATS,
                    self.AUDIO_MORE_FORMATS,
                    selected="MP3",
                )
            self.chips_container.pack(
                fill="x",
                pady=(0, theme.SPACE_LG),
                after=self.media_switch,
            )

        self.after(theme.FADE_STEP_MS * 2, _swap)

    def _choose_directory(self) -> None:
        chosen = filedialog.askdirectory(
            parent=self.winfo_toplevel(),
            initialdir=self.save_path_var.get(),
            mustexist=False,
        )
        if chosen:
            self.save_path_entry.configure(state="normal")
            self.save_path_var.set(chosen)
            self.save_path_entry.configure(state="readonly")
            self.storage.set_setting("download_dir", chosen)

    def start_download_action(self) -> None:
        """بدء التحميل في 3 خطوات (الصق الرابط ← اختر الجودة ← اضغط تحميل)."""
        url = self.url_var.get().strip()
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            self.toast.show(i18n.t("toast_invalid_url"), kind="error")
            return

        if self.current_media and self.current_media.url == url:
            self._dispatch_download(self.current_media)
        elif self._is_analyzing:
            # إذا كان التحليل التلقائي جارياً بالفعل، ننتظر انتهاءه ثم نبدأ التحميل تلقائياً
            self._start_after_analyze = True
            self.start_btn.set_loading(True, i18n.t("btn_start_loading"))
        else:
            # إذا لم يضغط المستخدم على "تحليل" مسبقاً، نحلل تلقائياً ونبدأ فوراً
            self._start_after_analyze = True
            self.start_btn.set_loading(True, i18n.t("btn_start_loading"))
            self.trigger_analyze()

    def _dispatch_download(self, media: MediaInfo) -> None:
        try:
            speed_lim = int(self.speed_limit_var.get().strip() or "0")
        except ValueError:
            speed_lim = 0

        self.downloader.start_download(
            media=media,
            media_type=self.media_switch.mode,
            quality=self.quality_chips.value,
            fmt=self.format_chips.value,
            save_dir=self.save_path_var.get(),
            subtitles=self.subtitles_var.get(),
            embed_thumbnail=self.embed_thumb_var.get(),
            speed_limit_kbps=speed_lim,
            filename_template=self.filename_tpl_var.get().strip() or "%(title)s.%(ext)s",
        )
        self.toast.show(i18n.t("toast_download_started"), kind="success")
        self.on_download_started()
