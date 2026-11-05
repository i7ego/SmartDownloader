"""
صفحة تحويل الفيديوهات والوسائط (ui/pages/converter_page.py).
تتيح:
- اختيار ملف فيديو من الجهاز وتحديد صيغته المستهدفة (MP4, MKV, WebM, AVI, GIF, MP3).
- اختيار الدقة المستهدفة (الأصلية، 1080p, 720p, 480p).
- اختيار جودة ونمط الضغط (جودة فائقة، متوازن، حجم صغير).
- متابعة نسبة التقدم أثناء التحويل مع إمكانية الإلغاء.
- حفظ الملف المحوّل في مجلد التحميلات وإضافته تلقائياً إلى السجل.
"""

import os
import threading
from pathlib import Path
from tkinter import filedialog
from typing import Callable, Optional
import customtkinter as ctk

from core.converter import convert_video, VideoConvertOptions
from core.cutter import get_media_duration
from core.downloader import format_duration
from core.storage import StorageManager
from ui import theme
from ui.i18n import i18n
from ui.icons import get_icon
from ui.components.buttons import PrimaryButton, SecondaryButton
from ui.components.feedback import ToastManager
from ui.components.widgets import ChipSelector, HoverCard, StatusBadge


def _sec_to_time_str(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins:02d}:{secs:04.1f}"


class ConverterPage(ctk.CTkScrollableFrame):
    """صفحة تحويل وتغيير دقة وضغط الفيديوهات."""

    FORMAT_OPTIONS = ["MP4", "MKV", "WebM", "AVI", "GIF", "MP3"]

    def __init__(
        self,
        master: object,
        storage: StorageManager,
        toast: ToastManager,
        on_converted: Optional[Callable[[str], None]] = None,
    ) -> None:
        super().__init__(master, fg_color=theme.COLOR_TRANSPARENT, corner_radius=0)
        self.storage = storage
        self.toast = toast
        self.on_converted = on_converted

        self._current_file: Optional[str] = None
        self._file_duration: float = 0.0
        self._is_converting: bool = False
        self._cancel_event: Optional[threading.Event] = None

        self._build_ui()

    def _build_ui(self) -> None:
        # رأس الصفحة
        header = ctk.CTkFrame(self, fg_color=theme.COLOR_TRANSPARENT)
        header.pack(fill="x", padx=theme.SPACE_LG, pady=(theme.SPACE_SM, theme.SPACE_LG))

        ctk.CTkLabel(
            header,
            text=i18n.t("page_converter_title"),
            font=theme.get_title_large_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        ).pack(fill="x")

        ctk.CTkLabel(
            header,
            text=i18n.t("page_converter_subtitle"),
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(2, 0))

        # ======================================================================
        # البطاقة 1: اختيار ملف الفيديو
        # ======================================================================
        self.file_card = HoverCard(self)
        self.file_card.pack(fill="x", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))

        file_inner = ctk.CTkFrame(self.file_card, fg_color=theme.COLOR_TRANSPARENT)
        file_inner.pack(fill="x", padx=theme.SPACE_XL, pady=theme.SPACE_XL)

        pick_row = ctk.CTkFrame(file_inner, fg_color=theme.COLOR_TRANSPARENT)
        pick_row.pack(fill="x")

        PrimaryButton(
            pick_row,
            text=i18n.t("conv_select_file"),
            icon_name="download",
            width=190,
            command=self._pick_file_dialog,
        ).pack(side=i18n.side_start)

        self.file_hint_lbl = ctk.CTkLabel(
            pick_row,
            text=i18n.t("conv_drop_hint"),
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        )
        self.file_hint_lbl.pack(
            side=i18n.side_start,
            fill="x",
            expand=True,
            padx=(theme.SPACE_LG, 0) if not i18n.is_rtl else (0, theme.SPACE_LG),
        )

        # معلومات الفيديو المختار
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
            image=get_icon("refresh", size=22, color_pair=theme.PRIMARY_COLOR),
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

        self.file_info_lbl = ctk.CTkLabel(
            txt_col,
            text="",
            font=theme.get_small_font(i18n.lang),
            text_color=theme.ACCENT_COLOR,
            anchor=i18n.align_start,
        )
        self.file_info_lbl.pack(fill="x")

        self.status_badge = StatusBadge(
            meta_inner,
            text=i18n.t("mode_video"),
            kind="accent",
        )
        self.status_badge.pack(side=i18n.side_end, padx=theme.SPACE_SM)

        # ======================================================================
        # البطاقة 2: خيارات التحويل (الصيغة، الدقة، الضغط)
        # ======================================================================
        self.options_card = HoverCard(self)
        self.options_card.pack(fill="x", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))

        opt_inner = ctk.CTkFrame(self.options_card, fg_color=theme.COLOR_TRANSPARENT)
        opt_inner.pack(fill="x", padx=theme.SPACE_XL, pady=theme.SPACE_XL)

        # 1. الصيغة المستهدفة
        ctk.CTkLabel(
            opt_inner,
            text=i18n.t("conv_target_format"),
            font=theme.get_section_title_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(0, theme.SPACE_XS))

        self.format_chips = ChipSelector(
            opt_inner,
            primary_options=self.FORMAT_OPTIONS,
            default_value="MP4",
            on_change=self._on_format_changed,
        )
        self.format_chips.pack(fill="x", pady=(0, theme.SPACE_LG))

        # 2. الدقة المستهدفة
        self.res_label = ctk.CTkLabel(
            opt_inner,
            text=i18n.t("conv_resolution"),
            font=theme.get_section_title_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        )
        self.res_label.pack(fill="x", pady=(0, theme.SPACE_XS))

        self.res_options = [
            i18n.t("conv_res_original"),
            i18n.t("conv_res_1080"),
            i18n.t("conv_res_720"),
            i18n.t("conv_res_480"),
        ]
        self.res_chips = ChipSelector(
            opt_inner,
            primary_options=self.res_options,
            default_value=self.res_options[0],
        )
        self.res_chips.pack(fill="x", pady=(0, theme.SPACE_LG))

        # 3. نمط الجودة والضغط
        self.preset_label = ctk.CTkLabel(
            opt_inner,
            text=i18n.t("conv_compression"),
            font=theme.get_section_title_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        )
        self.preset_label.pack(fill="x", pady=(0, theme.SPACE_XS))

        self.preset_options = [
            i18n.t("conv_preset_balanced"),
            i18n.t("conv_preset_high"),
            i18n.t("conv_preset_small"),
        ]
        self.preset_chips = ChipSelector(
            opt_inner,
            primary_options=self.preset_options,
            default_value=self.preset_options[0],
        )
        self.preset_chips.pack(fill="x", pady=(0, theme.SPACE_XL))

        # ======================================================================
        # البطاقة 3: مؤشر شريط التقدم عند التحويل
        # ======================================================================
        self.progress_card = HoverCard(self)

        prog_inner = ctk.CTkFrame(self.progress_card, fg_color=theme.COLOR_TRANSPARENT)
        prog_inner.pack(fill="x", padx=theme.SPACE_XL, pady=theme.SPACE_LG)

        prog_top = ctk.CTkFrame(prog_inner, fg_color=theme.COLOR_TRANSPARENT)
        prog_top.pack(fill="x", pady=(0, theme.SPACE_SM))

        self.progress_title_lbl = ctk.CTkLabel(
            prog_top,
            text=i18n.t("conv_btn_converting"),
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        )
        self.progress_title_lbl.pack(side=i18n.side_start)

        self.progress_pct_lbl = ctk.CTkLabel(
            prog_top,
            text="0%",
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.ACCENT_COLOR,
        )
        self.progress_pct_lbl.pack(side=i18n.side_end)

        self.progress_bar = ctk.CTkProgressBar(
            prog_inner,
            height=theme.PROGRESS_BAR_HEIGHT,
            corner_radius=4,
            fg_color=theme.BG_INPUT,
            progress_color=theme.ACCENT_COLOR,
        )
        self.progress_bar.pack(fill="x", pady=(0, theme.SPACE_SM))
        self.progress_bar.set(0.0)

        SecondaryButton(
            prog_inner,
            text=i18n.t("conv_btn_cancel"),
            icon_name="trash",
            width=130,
            command=self.cancel_conversion,
        ).pack(side=i18n.side_end)

        # ======================================================================
        # زر بدء التحويل
        # ======================================================================
        self.convert_btn = PrimaryButton(
            self,
            text=i18n.t("conv_btn_start"),
            icon_name="refresh",
            height=theme.INPUT_HEIGHT,
            command=self.start_conversion,
        )
        self.convert_btn.pack(fill="x", padx=theme.SPACE_LG, pady=(theme.SPACE_SM, theme.SPACE_XXL))

    def _on_format_changed(self, target_fmt: str) -> None:
        """إخفاء خيارات الدقة إذا تم اختيار استخراج الصوت فقط."""
        fmt = target_fmt.lower()
        if fmt in ["mp3", "m4a", "wav"]:
            self.res_label.pack_forget()
            self.res_chips.pack_forget()
        else:
            self.res_label.pack(fill="x", pady=(0, theme.SPACE_XS), before=self.preset_label)
            self.res_chips.pack(fill="x", pady=(0, theme.SPACE_LG), before=self.preset_label)

    def _pick_file_dialog(self) -> None:
        """فتح نافذة اختيار ملف فيديو من القرص."""
        filetypes = [
            ("Video Files", "*.mp4 *.mkv *.webm *.avi *.mov *.flv *.ts *.wmv"),
            ("All Files", "*.*"),
        ]
        chosen = filedialog.askopenfilename(
            parent=self.winfo_toplevel(),
            title=i18n.t("conv_select_file"),
            filetypes=filetypes,
        )
        if chosen:
            self.load_file(chosen)

    def load_file(self, file_path: str) -> None:
        """تحميل الفيديو وعرض معلوماته وضبط الواجهة."""
        p = Path(file_path)
        if not p.exists():
            self.toast.show(i18n.t("toast_conv_no_file"), kind="error")
            return

        self._current_file = str(p.resolve())
        duration = get_media_duration(self._current_file)
        self._file_duration = duration

        size_mb = p.stat().st_size / (1024 * 1024)
        size_str = f"{size_mb:.1f} MB"

        self.filename_lbl.configure(text=p.name)
        self.file_info_lbl.configure(
            text=f"{i18n.t('cutter_duration_label')} {_sec_to_time_str(duration)}  •  {size_str}"
        )
        self.meta_frame.pack(fill="x", pady=(theme.SPACE_MD, 0))

    def start_conversion(self) -> None:
        """بدء تحويل ومعالجة الفيديو في خيط خلفي."""
        if not self._current_file:
            self.toast.show(i18n.t("toast_conv_no_file"), kind="error")
            return

        if self._is_converting:
            return

        self._is_converting = True
        self._cancel_event = threading.Event()

        fmt = self.format_chips.value.lower()
        res_val = self.res_chips.value
        preset_val = self.preset_chips.value

        # تحديد المعاملات
        res_key = "original"
        if "1080" in res_val:
            res_key = "1080p"
        elif "720" in res_val:
            res_key = "720p"
        elif "480" in res_val:
            res_key = "480p"

        preset_key = "balanced"
        if preset_val == i18n.t("conv_preset_high"):
            preset_key = "high"
        elif preset_val == i18n.t("conv_preset_small"):
            preset_key = "small"

        opts = VideoConvertOptions(
            target_format=fmt,
            resolution=res_key,
            quality_preset=preset_key,
        )

        save_dir = Path(str(self.storage.get_setting("download_dir")))
        save_dir.mkdir(parents=True, exist_ok=True)

        orig_stem = Path(self._current_file).stem
        out_name = f"{orig_stem}_converted_{res_key}.{fmt}"
        out_path = save_dir / out_name

        self.convert_btn.set_loading(True, i18n.t("conv_btn_converting"))
        self.progress_bar.set(0.0)
        self.progress_pct_lbl.configure(text="0%")
        self.progress_card.pack(fill="x", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG), before=self.convert_btn)

        def _progress(pct: float) -> None:
            if self.winfo_exists():
                self.after(0, lambda: self._update_progress_ui(pct))

        def _worker() -> None:
            success = convert_video(
                input_path=self._current_file,  # type: ignore[arg-type]
                output_path=str(out_path),
                options=opts,
                progress_callback=_progress,
                cancel_event=self._cancel_event,
            )
            if self.winfo_exists():
                self.after(0, lambda: self._on_conversion_finished(success, str(out_path)))

        threading.Thread(target=_worker, daemon=True).start()

    def _update_progress_ui(self, pct: float) -> None:
        val = min(1.0, max(0.0, pct / 100.0))
        self.progress_bar.set(val)
        self.progress_pct_lbl.configure(text=f"{int(pct)}%")

    def cancel_conversion(self) -> None:
        """إلغاء عملية التحويل الجارية."""
        if self._cancel_event:
            self._cancel_event.set()
        self._is_converting = False
        self.convert_btn.set_loading(False)
        self.progress_card.pack_forget()

    def _on_conversion_finished(self, success: bool, output_file: str) -> None:
        self._is_converting = False
        self.convert_btn.set_loading(False)
        self.progress_card.pack_forget()

        if success:
            self.toast.show(i18n.t("toast_conv_success"), kind="success")
            p = Path(output_file)
            dur = get_media_duration(output_file)
            fmt = self.format_chips.value
            is_audio = fmt.lower() in ["mp3", "m4a", "wav"]
            self.storage.add_history_entry(
                title=p.name,
                url=self._current_file or "",
                channel="Video Converter",
                media_type="audio" if is_audio else "video",
                quality=self.res_chips.value,
                fmt=fmt,
                save_path=str(p.parent),
                duration_str=format_duration(dur),
            )
            if self.on_converted:
                self.on_converted(output_file)
        else:
            if self._cancel_event and not self._cancel_event.is_set():
                self.toast.show(i18n.t("toast_conv_error"), kind="error")
