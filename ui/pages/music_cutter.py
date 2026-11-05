"""
صفحة "تقطيع الأغاني والموسيقى" (Music Cutter) - ui/pages/music_cutter.py
تتيح:
- مشغّل صوتي متكامل مع شريط تمرير حي (Live Seek Bar) وعرض الوقت بالثواني والدقائق.
- أزرار تعيين نقطة البداية والنهاية أثناء الاستماع بضغطة زر واحدة.
- التحكم بدقة في نقطة البداية ونقطة النهاية مع حساب مدة المقطع تلقائياً.
- زر معاينة فورية للجزء المقتطع قبل تنفيذه.
- إضافة تأثيرات التلاشي الصوتي عند البداية والنهاية (Fade In / Fade Out).
- اختيار صيغة التصدير (MP3, M4A, WAV, FLAC) وجودة الصوت (320kbps إلى 128kbps).
- حفظ الملف المقتطع في مجلد التحميلات مع إشعار Toast بنجاح العملية وإمكانية فتح المجلد.
"""

import os
import threading
from pathlib import Path
from tkinter import filedialog
from typing import Callable, Optional
import customtkinter as ctk

from core.cutter import (
    AudioPreviewPlayer,
    MediaPreviewPlayer,
    cut_audio,
    cut_video,
    is_video_file,
    is_audio_file,
    get_media_duration,
)
from core.downloader import format_duration, open_folder_in_explorer
from core.storage import StorageManager
from ui import theme
from ui.i18n import i18n
from ui.icons import get_icon
from ui.components.buttons import (
    GhostIconButton,
    PrimaryButton,
    SecondaryButton,
)
from ui.components.feedback import ToastManager
from ui.components.widgets import (
    ChipSelector,
    HoverCard,
    StatusBadge,
)


def _sec_to_time_str(seconds: float) -> str:
    """تحويل الثواني إلى صيغة MM:SS.s."""
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins:02d}:{secs:04.1f}"


def _time_str_to_sec(time_str: str) -> Optional[float]:
    """تحويل صيغة MM:SS أو SS إلى ثوانٍ عشرية."""
    text = time_str.strip()
    if not text:
        return None
    try:
        if ":" in text:
            parts = text.split(":")
            if len(parts) == 2:
                return float(parts[0]) * 60.0 + float(parts[1])
            elif len(parts) == 3:
                return float(parts[0]) * 3600.0 + float(parts[1]) * 60.0 + float(parts[2])
        return float(text)
    except Exception:
        return None


class MusicCutterPage(ctk.CTkScrollableFrame):
    """صفحة تقطيع وتعديل المقاطع الصوتية مع مشغل صوتي مباشر."""

    FORMAT_OPTIONS = ["MP3", "M4A", "WAV", "FLAC"]
    QUALITY_OPTIONS = ["320kbps", "256kbps", "192kbps", "128kbps"]

    def __init__(
        self,
        master: object,
        storage: StorageManager,
        toast: ToastManager,
        on_cut_completed: Optional[Callable[[str], None]] = None,
    ) -> None:
        super().__init__(master, fg_color=theme.COLOR_TRANSPARENT, corner_radius=0)
        self.storage = storage
        self.toast = toast
        self.on_cut_completed = on_cut_completed

        self.player = AudioPreviewPlayer()
        self._current_file: Optional[str] = None
        self._file_duration: float = 0.0
        self._is_cutting: bool = False
        self._user_is_seeking: bool = False
        self._timer_after_id: Optional[str] = None

        self._build_ui()
        self._schedule_timer()

    def _build_ui(self) -> None:
        # رأس الصفحة
        header = ctk.CTkFrame(self, fg_color=theme.COLOR_TRANSPARENT)
        header.pack(fill="x", padx=theme.SPACE_LG, pady=(theme.SPACE_SM, theme.SPACE_LG))

        ctk.CTkLabel(
            header,
            text=i18n.t("page_cutter_title"),
            font=theme.get_title_large_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        ).pack(fill="x")

        ctk.CTkLabel(
            header,
            text=i18n.t("page_cutter_subtitle"),
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(2, 0))

        # ======================================================================
        # البطاقة 1: اختيار أو إفلات الملف
        # ======================================================================
        self.file_card = HoverCard(self)
        self.file_card.pack(fill="x", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))

        file_inner = ctk.CTkFrame(self.file_card, fg_color=theme.COLOR_TRANSPARENT)
        file_inner.pack(fill="x", padx=theme.SPACE_XL, pady=theme.SPACE_XL)

        # زر استعراض الملف
        pick_row = ctk.CTkFrame(file_inner, fg_color=theme.COLOR_TRANSPARENT)
        pick_row.pack(fill="x")

        PrimaryButton(
            pick_row,
            text=i18n.t("cutter_select_file"),
            icon_name="music",
            width=190,
            command=self._pick_file_dialog,
        ).pack(side=i18n.side_start)

        self.file_status_lbl = ctk.CTkLabel(
            pick_row,
            text=i18n.t("cutter_drop_hint"),
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        )
        self.file_status_lbl.pack(
            side=i18n.side_start,
            fill="x",
            expand=True,
            padx=(theme.SPACE_LG, 0) if not i18n.is_rtl else (0, theme.SPACE_LG),
        )

        # معلومات الملف الحالي
        self.meta_frame = ctk.CTkFrame(
            file_inner,
            fg_color=theme.BG_INPUT,
            corner_radius=theme.RADIUS_BUTTON,
        )

        meta_inner = ctk.CTkFrame(self.meta_frame, fg_color=theme.COLOR_TRANSPARENT)
        meta_inner.pack(fill="x", padx=theme.SPACE_LG, pady=theme.SPACE_MD)

        ic_lbl = ctk.CTkLabel(
            meta_inner,
            text="",
            image=get_icon("scissors", size=22, color_pair=theme.PRIMARY_COLOR),
        )
        ic_lbl.pack(
            side=i18n.side_start,
            padx=(0, theme.SPACE_MD) if not i18n.is_rtl else (theme.SPACE_MD, 0),
        )

        txt_col = ctk.CTkFrame(meta_inner, fg_color=theme.COLOR_TRANSPARENT)
        txt_col.pack(side=i18n.side_start, fill="x", expand=True)

        self.filename_lbl = ctk.CTkLabel(
            txt_col,
            text="",
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        )
        self.filename_lbl.pack(fill="x")

        self.file_duration_lbl = ctk.CTkLabel(
            txt_col,
            text="",
            font=theme.get_small_font(i18n.lang),
            text_color=theme.ACCENT_COLOR,
            anchor=i18n.align_start,
        )
        self.file_duration_lbl.pack(fill="x")

        self.media_badge = StatusBadge(
            meta_inner,
            text=i18n.t("mode_audio"),
            kind="active",
        )
        self.media_badge.pack(side=i18n.side_end, padx=theme.SPACE_SM)

        # ======================================================================
        # البطاقة 2: مشغل الصوت وشريط التمرير الحي (Live Seek Bar) وأزرار Start / End
        # ======================================================================
        self.player_card = HoverCard(self)
        self.player_card.pack(fill="x", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))

        player_inner = ctk.CTkFrame(self.player_card, fg_color=theme.COLOR_TRANSPARENT)
        player_inner.pack(fill="x", padx=theme.SPACE_XL, pady=theme.SPACE_XL)

        ctk.CTkLabel(
            player_inner,
            text=i18n.t("cutter_player_section"),
            font=theme.get_section_title_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_MD))

        # شريط التمرير (Seek Bar)
        seek_box = ctk.CTkFrame(player_inner, fg_color=theme.COLOR_TRANSPARENT)
        seek_box.pack(fill="x", pady=(0, theme.SPACE_SM))

        self.seek_slider = ctk.CTkSlider(
            seek_box,
            from_=0.0,
            to=100.0,
            number_of_steps=1000,
            progress_color=theme.ACCENT_COLOR,
            button_color=theme.ACCENT_COLOR,
            button_hover_color=theme.ACCENT_HOVER,
            command=self._on_seek_slider_moved,
        )
        self.seek_slider.set(0.0)
        self.seek_slider.pack(fill="x", pady=(0, theme.SPACE_XS))

        # ربط أحداث الضغط لتعليق التحديث التلقائي أثناء سحب المستخدم للسيك بار
        self.seek_slider.bind("<ButtonPress-1>", lambda _e: self._set_user_seeking(True))
        self.seek_slider.bind("<ButtonRelease-1>", lambda _e: self._on_seek_released())

        time_row = ctk.CTkFrame(player_inner, fg_color=theme.COLOR_TRANSPARENT)
        time_row.pack(fill="x", pady=(0, theme.SPACE_MD))

        self.playback_time_lbl = ctk.CTkLabel(
            time_row,
            text="00:00.0 / 00:00.0",
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.ACCENT_COLOR,
            anchor=i18n.align_start,
        )
        self.playback_time_lbl.pack(side=i18n.side_start)

        # صف أزرار التحكم وأزرار التعيين السريع
        ctrl_row = ctk.CTkFrame(player_inner, fg_color=theme.COLOR_TRANSPARENT)
        ctrl_row.pack(fill="x")

        self.play_pause_btn = PrimaryButton(
            ctrl_row,
            text=i18n.t("cutter_btn_play"),
            icon_name="play",
            width=130,
            command=self._toggle_playback,
        )
        self.play_pause_btn.pack(side=i18n.side_start, padx=(0, theme.SPACE_SM) if not i18n.is_rtl else (theme.SPACE_SM, 0))

        self.stop_playback_btn = SecondaryButton(
            ctrl_row,
            text=i18n.t("cutter_btn_stop"),
            icon_name="x",
            width=100,
            command=self.stop_playback,
        )
        self.stop_playback_btn.pack(side=i18n.side_start, padx=(0, theme.SPACE_XL) if not i18n.is_rtl else (theme.SPACE_XL, 0))

        # زري تعيين البداية والنهاية أثناء الاستماع
        self.set_start_btn = SecondaryButton(
            ctrl_row,
            text=i18n.t("cutter_set_start"),
            icon_name="scissors",
            width=140,
            command=self._set_current_as_start,
        )
        self.set_start_btn.pack(side=i18n.side_start, padx=(0, theme.SPACE_SM) if not i18n.is_rtl else (theme.SPACE_SM, 0))

        self.set_end_btn = SecondaryButton(
            ctrl_row,
            text=i18n.t("cutter_set_end"),
            icon_name="scissors",
            width=140,
            command=self._set_current_as_end,
        )
        self.set_end_btn.pack(side=i18n.side_start)

        # ======================================================================
        # البطاقة 3: تحديد البداية والنهاية بدقة والمعاينة
        # ======================================================================
        self.range_card = HoverCard(self)
        self.range_card.pack(fill="x", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))

        range_inner = ctk.CTkFrame(self.range_card, fg_color=theme.COLOR_TRANSPARENT)
        range_inner.pack(fill="x", padx=theme.SPACE_XL, pady=theme.SPACE_XL)

        ctk.CTkLabel(
            range_inner,
            text=i18n.t("cutter_range_section"),
            font=theme.get_section_title_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_MD))

        # صف شريط و حقل البداية
        start_row = ctk.CTkFrame(range_inner, fg_color=theme.COLOR_TRANSPARENT)
        start_row.pack(fill="x", pady=theme.SPACE_XS)

        ctk.CTkLabel(
            start_row,
            text=i18n.t("cutter_start_label"),
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_SECONDARY,
            width=110,
            anchor=i18n.align_start,
        ).pack(side=i18n.side_start)

        self.start_slider = ctk.CTkSlider(
            start_row,
            from_=0.0,
            to=100.0,
            number_of_steps=1000,
            progress_color=theme.PRIMARY_COLOR,
            button_color=theme.PRIMARY_COLOR,
            button_hover_color=theme.PRIMARY_HOVER,
            command=self._on_start_slider_moved,
        )
        self.start_slider.set(0.0)
        self.start_slider.pack(
            side=i18n.side_start,
            fill="x",
            expand=True,
            padx=(theme.SPACE_MD, theme.SPACE_MD),
        )

        self.start_time_var = ctk.StringVar(value="00:00.0")
        self.start_entry = ctk.CTkEntry(
            start_row,
            textvariable=self.start_time_var,
            width=95,
            height=theme.BUTTON_SMALL_HEIGHT,
            corner_radius=theme.RADIUS_CHIP,
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_COLOR,
        )
        self.start_entry.pack(side=i18n.side_end)
        self.start_entry.bind("<FocusOut>", lambda _e: self._on_start_entry_changed())
        self.start_entry.bind("<Return>", lambda _e: self._on_start_entry_changed())

        # صف شريط و حقل النهاية
        end_row = ctk.CTkFrame(range_inner, fg_color=theme.COLOR_TRANSPARENT)
        end_row.pack(fill="x", pady=theme.SPACE_XS)

        ctk.CTkLabel(
            end_row,
            text=i18n.t("cutter_end_label"),
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_SECONDARY,
            width=110,
            anchor=i18n.align_start,
        ).pack(side=i18n.side_start)

        self.end_slider = ctk.CTkSlider(
            end_row,
            from_=0.0,
            to=100.0,
            number_of_steps=1000,
            progress_color=theme.ACCENT_COLOR,
            button_color=theme.ACCENT_COLOR,
            button_hover_color=theme.ACCENT_HOVER,
            command=self._on_end_slider_moved,
        )
        self.end_slider.set(100.0)
        self.end_slider.pack(
            side=i18n.side_start,
            fill="x",
            expand=True,
            padx=(theme.SPACE_MD, theme.SPACE_MD),
        )

        self.end_time_var = ctk.StringVar(value="00:00.0")
        self.end_entry = ctk.CTkEntry(
            end_row,
            textvariable=self.end_time_var,
            width=95,
            height=theme.BUTTON_SMALL_HEIGHT,
            corner_radius=theme.RADIUS_CHIP,
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_COLOR,
        )
        self.end_entry.pack(side=i18n.side_end)
        self.end_entry.bind("<FocusOut>", lambda _e: self._on_end_entry_changed())
        self.end_entry.bind("<Return>", lambda _e: self._on_end_entry_changed())

        # عرض مدة المقطع المقتطع ومعاينة المقطع فقط
        preview_bar = ctk.CTkFrame(range_inner, fg_color=theme.COLOR_TRANSPARENT)
        preview_bar.pack(fill="x", pady=(theme.SPACE_LG, 0))

        self.segment_dur_lbl = ctk.CTkLabel(
            preview_bar,
            text=f"{i18n.t('cutter_segment_len')} 00:00.0",
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.ACCENT_COLOR,
            anchor=i18n.align_start,
        )
        self.segment_dur_lbl.pack(side=i18n.side_start, fill="x", expand=True)

        self.preview_segment_btn = SecondaryButton(
            preview_bar,
            text=i18n.t("cutter_btn_preview"),
            icon_name="play",
            width=160,
            command=self._toggle_segment_preview,
        )
        self.preview_segment_btn.pack(side=i18n.side_end)

        # ======================================================================
        # البطاقة 4: تأثيرات التلاشي وصيغة التصدير وزر التنفيذ
        # ======================================================================
        self.options_card = HoverCard(self)
        self.options_card.pack(fill="x", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))

        opt_inner = ctk.CTkFrame(self.options_card, fg_color=theme.COLOR_TRANSPARENT)
        opt_inner.pack(fill="x", padx=theme.SPACE_XL, pady=theme.SPACE_XL)

        # خيارات التلاشي الصوتي
        self.fade_section_frame = ctk.CTkFrame(opt_inner, fg_color=theme.COLOR_TRANSPARENT)
        self.fade_section_frame.pack(fill="x", pady=(0, theme.SPACE_MD))

        ctk.CTkLabel(
            self.fade_section_frame,
            text=i18n.t("cutter_fade_section"),
            font=theme.get_section_title_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_MD))

        fade_row = ctk.CTkFrame(self.fade_section_frame, fg_color=theme.COLOR_TRANSPARENT)
        fade_row.pack(fill="x", pady=(0, theme.SPACE_SM))

        ctk.CTkLabel(
            fade_row,
            text=i18n.t("cutter_fade_in"),
            font=theme.get_small_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
        ).pack(
            side=i18n.side_start,
            padx=(0, theme.SPACE_SM) if not i18n.is_rtl else (theme.SPACE_SM, 0),
        )

        self.fade_in_var = ctk.StringVar(value="0.0")
        ctk.CTkEntry(
            fade_row,
            textvariable=self.fade_in_var,
            width=65,
            height=32,
            corner_radius=theme.RADIUS_CHIP,
            font=theme.get_small_font(i18n.lang),
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_COLOR,
            text_color=theme.TEXT_PRIMARY,
        ).pack(
            side=i18n.side_start,
            padx=(0, theme.SPACE_XXL) if not i18n.is_rtl else (theme.SPACE_XXL, 0),
        )

        ctk.CTkLabel(
            fade_row,
            text=i18n.t("cutter_fade_out"),
            font=theme.get_small_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
        ).pack(
            side=i18n.side_start,
            padx=(0, theme.SPACE_SM) if not i18n.is_rtl else (theme.SPACE_SM, 0),
        )

        self.fade_out_var = ctk.StringVar(value="0.0")
        ctk.CTkEntry(
            fade_row,
            textvariable=self.fade_out_var,
            width=65,
            height=32,
            corner_radius=theme.RADIUS_CHIP,
            font=theme.get_small_font(i18n.lang),
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_COLOR,
            text_color=theme.TEXT_PRIMARY,
        ).pack(side=i18n.side_start)

        # نمط معالجة القص (سريع أو دقيق)
        self.mode_frame = ctk.CTkFrame(opt_inner, fg_color=theme.COLOR_TRANSPARENT)
        self.mode_frame.pack(fill="x", pady=(0, theme.SPACE_MD))

        ctk.CTkLabel(
            self.mode_frame,
            text=i18n.t("cutter_mode_label"),
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_XS))

        self.mode_chips = ChipSelector(
            self.mode_frame,
            primary_options=[i18n.t("cutter_mode_fast"), i18n.t("cutter_mode_accurate")],
            default_value=i18n.t("cutter_mode_fast"),
        )
        self.mode_chips.pack(fill="x")

        # صيغة وجودة التصدير
        ctk.CTkLabel(
            opt_inner,
            text=i18n.t("cutter_export_format"),
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_XS))

        self.format_chips = ChipSelector(
            opt_inner,
            primary_options=self.FORMAT_OPTIONS,
            default_value="MP3",
        )
        self.format_chips.pack(fill="x", pady=(0, theme.SPACE_MD))

        ctk.CTkLabel(
            opt_inner,
            text=i18n.t("cutter_export_quality"),
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_XS))

        self.quality_chips = ChipSelector(
            opt_inner,
            primary_options=self.QUALITY_OPTIONS,
            default_value="320kbps",
        )
        self.quality_chips.pack(fill="x", pady=(0, theme.SPACE_XL))

        # زر قص وحفظ المقطع
        self.cut_btn = PrimaryButton(
            opt_inner,
            text=i18n.t("cutter_btn_cut"),
            icon_name="scissors",
            height=theme.INPUT_HEIGHT,
            command=self.start_cutting,
        )
        self.cut_btn.pack(fill="x")

    # ==========================================================================
    # التعامل مع اختيار الملف وضبط أشرطة التمرير
    # ==========================================================================

    def _pick_file_dialog(self) -> None:
        """فتح نافذة اختيار ملف صوتي أو مرئي من القرص."""
        filetypes = [
            ("All Supported Media", "*.mp3 *.m4a *.wav *.flac *.aac *.ogg *.mp4 *.mkv *.webm"),
            ("Audio Files", "*.mp3 *.m4a *.wav *.flac *.aac *.ogg"),
            ("Video Files", "*.mp4 *.mkv *.webm *.avi *.mov"),
            ("All Files", "*.*"),
        ]
        chosen = filedialog.askopenfilename(
            parent=self.winfo_toplevel(),
            title=i18n.t("cutter_select_file"),
            filetypes=filetypes,
        )
        if chosen:
            self.load_file(chosen)

    def load_file(self, file_path: str) -> None:
        """تحميل الملف واستخراج مدته وضبط أشرطة البداية والنهاية."""
        p = Path(file_path)
        if not p.exists():
            self.toast.show(i18n.t("toast_cutter_no_file"), kind="error")
            return

        self.stop_playback()
        self._current_file = str(p.resolve())
        duration = get_media_duration(self._current_file)

        if duration <= 0.0:
            duration = 180.0  # قيمة تقديرية في حال تعذر القراءة المباشرة

        self._file_duration = duration

        # تحديث الواجهة
        self.filename_lbl.configure(text=p.name)
        self.file_duration_lbl.configure(
            text=f"{i18n.t('cutter_duration_label')} {_sec_to_time_str(duration)} ({duration:.1f}s)"
        )
        self.meta_frame.pack(fill="x", pady=(theme.SPACE_MD, 0))

        # تحديث شريط التمرير (Seek Bar)
        self.seek_slider.configure(from_=0.0, to=duration)
        self.seek_slider.set(0.0)
        self.playback_time_lbl.configure(
            text=f"00:00.0 / {_sec_to_time_str(duration)}"
        )

        # تحديث أشرطة القص
        self.start_slider.configure(from_=0.0, to=duration)
        self.start_slider.set(0.0)
        self.start_time_var.set("00:00.0")

        self.end_slider.configure(from_=0.0, to=duration)
        self.end_slider.set(duration)
        self.end_time_var.set(_sec_to_time_str(duration))

        # ضبط خيارات التصدير ونمط المعالجة بحسب نوع الملف (فيديو أو صوت)
        is_video = is_video_file(self._current_file)
        if is_video:
            self.media_badge.set_custom_badge(i18n.t("mode_video"), theme.ACCENT_COLOR, theme.ACCENT_TINT)
            self.mode_frame.pack(fill="x", pady=(0, theme.SPACE_MD))
            self.fade_section_frame.pack_forget()
            self.format_chips.set_options(["MP4", "MKV", "WebM", "GIF", "MP3"])
            self.format_chips.set_value("MP4")
            self.quality_chips.set_options(["Original", "1080p", "720p", "480p"])
            self.quality_chips.set_value("Original")
        else:
            self.media_badge.set_custom_badge(i18n.t("mode_audio"), theme.PRIMARY_COLOR, theme.PRIMARY_TINT)
            self.mode_frame.pack_forget()
            self.fade_section_frame.pack(fill="x", pady=(0, theme.SPACE_MD), before=self.format_chips)
            self.format_chips.set_options(self.FORMAT_OPTIONS)
            self.format_chips.set_value("MP3")
            self.quality_chips.set_options(self.QUALITY_OPTIONS)
            self.quality_chips.set_value("320kbps")

        self._update_segment_label()

    # ==========================================================================
    # المشغل الصوتي وشريط التمرير (Seek Bar)
    # ==========================================================================

    def _set_user_seeking(self, is_seeking: bool) -> None:
        self._user_is_seeking = is_seeking

    def _on_seek_slider_moved(self, value: float) -> None:
        self.playback_time_lbl.configure(
            text=f"{_sec_to_time_str(value)} / {_sec_to_time_str(self._file_duration)}"
        )

    def _on_seek_released(self) -> None:
        self._user_is_seeking = False
        target_pos = self.seek_slider.get()
        if self._current_file:
            self.player.seek(target_pos)

    def _toggle_playback(self) -> None:
        """تشغيل أو إيقاف مؤقت للأغنية بالكامل."""
        if not self._current_file:
            self.toast.show(i18n.t("toast_cutter_no_file"), kind="warning")
            return

        if self.player.is_playing():
            self.player.pause()
            self.play_pause_btn.configure(
                text=i18n.t("cutter_btn_play"),
                image=get_icon("play", size=18, color_pair=theme.TEXT_PRIMARY),
            )
        elif self.player.is_paused():
            self.player.resume()
            self.play_pause_btn.configure(
                text=i18n.t("cutter_btn_pause"),
                image=get_icon(
                    "pause",
                    size=18,
                    color_pair=(theme.COLOR_ON_PRIMARY, theme.COLOR_ON_PRIMARY),
                ),
            )
        else:
            start_pos = self.seek_slider.get()
            started = self.player.play(
                self._current_file,
                start_sec=start_pos,
                total_duration=self._file_duration,
            )
            if started:
                self.play_pause_btn.configure(
                    text=i18n.t("cutter_btn_pause"),
                    image=get_icon(
                        "pause",
                        size=18,
                        color_pair=(theme.COLOR_ON_PRIMARY, theme.COLOR_ON_PRIMARY),
                    ),
                )
            else:
                self.toast.show(i18n.t("toast_cutter_error"), kind="error")

    def stop_playback(self) -> None:
        """إيقاف التشغيل بالكامل."""
        self.player.stop()
        self.play_pause_btn.configure(
            text=i18n.t("cutter_btn_play"),
            image=get_icon(
                "play",
                size=18,
                color_pair=(theme.COLOR_ON_PRIMARY, theme.COLOR_ON_PRIMARY),
            ),
        )
        self.preview_segment_btn.configure(
            text=i18n.t("cutter_btn_preview"),
            image=get_icon("play", size=18, color_pair=theme.TEXT_PRIMARY),
        )

    def _set_current_as_start(self) -> None:
        """تعيين الموضع الحالي في المشغل كنقطة بداية للقص."""
        if not self._current_file:
            return
        curr_pos = self.player.get_current_position() if self.player.is_playing() or self.player.is_paused() else self.seek_slider.get()
        self._on_start_slider_moved(curr_pos)

    def _set_current_as_end(self) -> None:
        """تعيين الموضع الحالي في المشغل كنقطة نهاية للقص."""
        if not self._current_file:
            return
        curr_pos = self.player.get_current_position() if self.player.is_playing() or self.player.is_paused() else self.seek_slider.get()
        self._on_end_slider_moved(curr_pos)

    def _schedule_timer(self) -> None:
        """حلقة تحديث زمنية كل 100 ملي ثانية لتحديث شريط التمرير أثناء الاستماع."""
        if self.winfo_exists():
            if self.player.is_playing() and not self._user_is_seeking:
                pos = self.player.get_current_position()
                self.seek_slider.set(pos)
                self.playback_time_lbl.configure(
                    text=f"{_sec_to_time_str(pos)} / {_sec_to_time_str(self._file_duration)}"
                )
            elif not self.player.is_playing() and not self.player.is_paused():
                # في حال انتهاء التشغيل التلقائي
                if self.play_pause_btn.cget("text") == i18n.t("cutter_btn_pause"):
                    self.play_pause_btn.configure(
                        text=i18n.t("cutter_btn_play"),
                        image=get_icon(
                            "play",
                            size=18,
                            color_pair=(theme.COLOR_ON_PRIMARY, theme.COLOR_ON_PRIMARY),
                        ),
                    )

            self._timer_after_id = self.after(100, self._schedule_timer)

    # ==========================================================================
    # التحكم في أشرطة البداية والنهاية للقص
    # ==========================================================================

    def _on_start_slider_moved(self, value: float) -> None:
        if value >= self.end_slider.get():
            value = max(0.0, self.end_slider.get() - 0.5)
        self.start_slider.set(value)
        self.start_time_var.set(_sec_to_time_str(value))
        self._update_segment_label()

    def _on_end_slider_moved(self, value: float) -> None:
        if value <= self.start_slider.get():
            value = min(self._file_duration, self.start_slider.get() + 0.5)
        self.end_slider.set(value)
        self.end_time_var.set(_sec_to_time_str(value))
        self._update_segment_label()

    def _on_start_entry_changed(self) -> None:
        val = _time_str_to_sec(self.start_time_var.get())
        if val is not None and 0.0 <= val < self.end_slider.get():
            self.start_slider.set(val)
        else:
            self.start_time_var.set(_sec_to_time_str(self.start_slider.get()))
        self._update_segment_label()

    def _on_end_entry_changed(self) -> None:
        val = _time_str_to_sec(self.end_time_var.get())
        if val is not None and self.start_slider.get() < val <= self._file_duration:
            self.end_slider.set(val)
        else:
            self.end_time_var.set(_sec_to_time_str(self.end_slider.get()))
        self._update_segment_label()

    def _update_segment_label(self) -> None:
        diff = max(0.0, self.end_slider.get() - self.start_slider.get())
        self.segment_dur_lbl.configure(
            text=f"{i18n.t('cutter_segment_len')} {_sec_to_time_str(diff)} ({diff:.1f}s)"
        )

    # ==========================================================================
    # معاينة المقطع وقصه
    # ==========================================================================

    def _toggle_segment_preview(self) -> None:
        """معاينة الجزء المقتطع فقط بين البداية والنهاية."""
        if not self._current_file:
            self.toast.show(i18n.t("toast_cutter_no_file"), kind="warning")
            return

        if self.player.is_playing():
            self.stop_playback()
        else:
            start = self.start_slider.get()
            dur = max(0.5, self.end_slider.get() - start)
            started = self.player.play(
                self._current_file,
                start_sec=start,
                duration_sec=dur,
                total_duration=self._file_duration,
            )
            if started:
                self.preview_segment_btn.configure(
                    text=i18n.t("cutter_btn_stop_preview"),
                    image=get_icon("pause", size=18, color_pair=theme.ACCENT_COLOR),
                )
            else:
                self.toast.show(i18n.t("toast_cutter_error"), kind="error")

    def stop_preview(self) -> None:
        self.stop_playback()

    def start_cutting(self) -> None:
        """بدء معالجة وقص المقطع في خيط خلفي وحفظه."""
        if not self._current_file:
            self.toast.show(i18n.t("toast_cutter_no_file"), kind="error")
            return

        start = self.start_slider.get()
        end = self.end_slider.get()
        if start >= end:
            self.toast.show(i18n.t("toast_cutter_invalid_range"), kind="error")
            return

        self.stop_playback()
        self.cut_btn.set_loading(True, i18n.t("cutter_btn_cutting"))

        # استخراج خيارات التصدير
        fmt = self.format_chips.value.lower()
        quality = self.quality_chips.value
        try:
            fade_in = float(self.fade_in_var.get().strip() or "0")
        except ValueError:
            fade_in = 0.0

        try:
            fade_out = float(self.fade_out_var.get().strip() or "0")
        except ValueError:
            fade_out = 0.0

        save_dir = Path(str(self.storage.get_setting("download_dir")))
        save_dir.mkdir(parents=True, exist_ok=True)

        orig_stem = Path(self._current_file).stem
        out_name = f"{orig_stem}_cut_{int(start)}s_{int(end)}s.{fmt}"
        out_path = save_dir / out_name

        is_video = is_video_file(self._current_file)
        mode = "fast" if self.mode_chips.value == i18n.t("cutter_mode_fast") else "accurate"

        def _worker() -> None:
            if is_video and fmt != "mp3":
                success = cut_video(
                    input_path=self._current_file,  # type: ignore[arg-type]
                    output_path=str(out_path),
                    start_sec=start,
                    end_sec=end,
                    mode=mode,
                    fmt=fmt,
                )
            else:
                success = cut_audio(
                    input_path=self._current_file,  # type: ignore[arg-type]
                    output_path=str(out_path),
                    start_sec=start,
                    end_sec=end,
                    fmt=fmt,
                    quality=quality,
                    fade_in=fade_in,
                    fade_out=fade_out,
                )
            if self.winfo_exists():
                self.after(0, lambda: self._on_cut_finished(success, str(out_path), is_video))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_cut_finished(self, success: bool, output_file: str, is_video: bool = False) -> None:
        self.cut_btn.set_loading(False)
        if success:
            self.toast.show(i18n.t("toast_cutter_success"), kind="success")
            # إضافة تلقائية إلى سجل التحميلات
            p = Path(output_file)
            dur = get_media_duration(output_file)
            is_vid_record = is_video and self.format_chips.value.lower() != "mp3"
            self.storage.add_history_entry(
                title=p.name,
                url=self._current_file or "",
                channel="Media Cutter",
                media_type="video" if is_vid_record else "audio",
                quality=self.quality_chips.value,
                fmt=self.format_chips.value,
                save_path=str(p.parent),
                duration_str=format_duration(dur),
            )
            if self.on_cut_completed:
                self.on_cut_completed(output_file)
        else:
            self.toast.show(i18n.t("toast_cutter_error"), kind="error")


# اسم مستعار عام للصفحة لدعم تقطيع الفيديو والصوت
MediaCutterPage = MusicCutterPage
