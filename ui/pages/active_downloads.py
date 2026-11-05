"""
صفحة "التحميلات الجارية" - ui/pages/active_downloads.py
تضم:
- شريط تقدّم نحيف بزوايا مستديرة بلون Accent مع نسبة مئوية وسرعة ووقت متبقٍ.
- بطاقة لكل تحميل: صورة مصغرة، عنوان، شريط تقدّم، أزرار أيقونات (إيقاف مؤقت/استئناف/إلغاء/فتح المجلد).
- شارات (Badges) ملوّنة للحالة: قيد التحميل (تركواز)، مكتمل (أخضر)، متوقف (برتقالي)، فشل (أحمر).
- حالة فارغة (Empty State) جميلة بأيقونة ونص ودود عندما لا توجد تحميلات.
"""

from typing import Dict
import customtkinter as ctk

from core.downloader import (
    DownloadManager,
    DownloadTask,
    create_rounded_thumbnail,
    open_folder_in_explorer,
)
from ui import theme
from ui.i18n import i18n
from ui.components.buttons import GhostIconButton, SecondaryButton
from ui.components.feedback import ToastManager
from ui.components.widgets import EmptyState, HoverCard, StatusBadge


class DownloadItemCard(HoverCard):
    """بطاقة تحميل مفردة داخل صفحة التحميلات الجارية."""

    def __init__(
        self,
        master: object,
        task: DownloadTask,
        downloader: DownloadManager,
        toast: ToastManager,
    ) -> None:
        super().__init__(master)
        self.task = task
        self.downloader = downloader
        self.toast = toast

        pil_img = task.thumbnail_image or create_rounded_thumbnail(None, size=(120, 68))
        self._thumb_ctk = ctk.CTkImage(
            light_image=pil_img,
            dark_image=pil_img,
            size=(120, 68),
        )

        self._build_ui()
        self.refresh_from_task()

    def _build_ui(self) -> None:
        inner = ctk.CTkFrame(self, fg_color=theme.COLOR_TRANSPARENT)
        inner.pack(fill="x", padx=theme.SPACE_LG, pady=theme.SPACE_LG)

        # الصورة المصغرة بزوايا مستديرة
        thumb_lbl = ctk.CTkLabel(inner, text="", image=self._thumb_ctk)
        thumb_lbl.pack(
            side=i18n.side_start,
            padx=(0, theme.SPACE_LG) if not i18n.is_rtl else (theme.SPACE_LG, 0),
        )

        # منطقة الوسط: العنوان + الشارة + شريط التقدم + الإحصائيات
        center = ctk.CTkFrame(inner, fg_color=theme.COLOR_TRANSPARENT)
        center.pack(side=i18n.side_start, fill="both", expand=True)

        top_row = ctk.CTkFrame(center, fg_color=theme.COLOR_TRANSPARENT)
        top_row.pack(fill="x", pady=(0, theme.SPACE_XS))

        self.title_lbl = ctk.CTkLabel(
            top_row,
            text=self.task.title,
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        )
        self.title_lbl.pack(side=i18n.side_start, fill="x", expand=True)

        self.badge = StatusBadge(top_row, status=self.task.status)
        self.badge.pack(
            side=i18n.side_end,
            padx=(theme.SPACE_SM, 0) if not i18n.is_rtl else (0, theme.SPACE_SM),
        )

        # شريط تقدّم نحيف بزوايا مستديرة بلون Accent
        self.progress_bar = ctk.CTkProgressBar(
            center,
            height=theme.PROGRESS_BAR_HEIGHT,
            corner_radius=theme.PROGRESS_BAR_HEIGHT // 2,
            fg_color=theme.BG_INPUT,
            progress_color=theme.ACCENT_COLOR,
        )
        self.progress_bar.pack(fill="x", pady=theme.SPACE_XS)
        self.progress_bar.set(self.task.progress)

        # صف النسبة المئوية والسرعة والوقت المتبقي
        stats_row = ctk.CTkFrame(center, fg_color=theme.COLOR_TRANSPARENT)
        stats_row.pack(fill="x")

        self.percent_lbl = ctk.CTkLabel(
            stats_row,
            text="0%",
            font=theme.get_small_font(i18n.lang, bold=True),
            text_color=theme.ACCENT_COLOR,
        )
        self.percent_lbl.pack(
            side=i18n.side_start,
            padx=(0, theme.SPACE_MD) if not i18n.is_rtl else (theme.SPACE_MD, 0),
        )

        self.meta_lbl = ctk.CTkLabel(
            stats_row,
            text=f"{self.task.quality} • {self.task.fmt}",
            font=theme.get_small_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
        )
        self.meta_lbl.pack(
            side=i18n.side_start,
            padx=(0, theme.SPACE_MD) if not i18n.is_rtl else (theme.SPACE_MD, 0),
        )

        self.speed_eta_lbl = ctk.CTkLabel(
            stats_row,
            text="",
            font=theme.get_small_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
        )
        self.speed_eta_lbl.pack(side=i18n.side_end)

        # أزرار الأيقونات (إيقاف مؤقت / استئناف / إلغاء / فتح المجلد)
        actions = ctk.CTkFrame(inner, fg_color=theme.COLOR_TRANSPARENT)
        actions.pack(
            side=i18n.side_end,
            padx=(theme.SPACE_MD, 0) if not i18n.is_rtl else (0, theme.SPACE_MD),
        )

        self.pause_resume_btn = GhostIconButton(
            actions,
            icon_name="pause",
            tooltip=i18n.t("tip_pause"),
            command=self._toggle_pause_resume,
        )
        self.pause_resume_btn.pack(side=i18n.side_start, padx=2)

        self.open_folder_btn = GhostIconButton(
            actions,
            icon_name="folder",
            tooltip=i18n.t("tip_open_folder"),
            icon_color=theme.ACCENT_COLOR,
            command=self._open_folder,
        )
        self.open_folder_btn.pack(side=i18n.side_start, padx=2)

        self.cancel_btn = GhostIconButton(
            actions,
            icon_name="x",
            tooltip=i18n.t("tip_cancel"),
            icon_color=theme.ERROR_COLOR,
            command=self._cancel,
        )
        self.cancel_btn.pack(side=i18n.side_start, padx=2)

    def _toggle_pause_resume(self) -> None:
        if self.task.status == "downloading":
            self.downloader.pause_task(self.task)
        elif self.task.status == "paused":
            self.downloader.resume_task(self.task)

    def _cancel(self) -> None:
        self.downloader.cancel_task(self.task)

    def _open_folder(self) -> None:
        if not open_folder_in_explorer(self.task.save_dir):
            self.toast.show(i18n.t("toast_folder_missing"), kind="error")

    def refresh_from_task(self) -> None:
        """تحديث عناصر البطاقة حسب الحالة الحالية للمهمة."""
        pct = int(round(self.task.progress * 100))
        self.progress_bar.set(self.task.progress)
        self.percent_lbl.configure(text=f"{pct}%")
        self.badge.set_status(self.task.status)

        if self.task.status == "downloading":
            self.progress_bar.configure(progress_color=theme.ACCENT_COLOR)
            self.speed_eta_lbl.configure(
                text=f"{i18n.t('speed_label')} {self.task.speed_str}   |   {i18n.t('eta_label')} {self.task.eta_str}"
            )
            self.pause_resume_btn.configure(
                image=self.pause_resume_btn._icon_img,
            )
            self.pause_resume_btn._icon_img = None  # لتحديث الأيقونة
            from ui.icons import get_icon
            self.pause_resume_btn.configure(
                image=get_icon("pause", size=18, color_pair=theme.TEXT_SECONDARY)
            )
            self.pause_resume_btn.set_tooltip(i18n.t("tip_pause"))
            self.pause_resume_btn.set_disabled(False)
            self.cancel_btn.set_disabled(False)

        elif self.task.status == "paused":
            self.progress_bar.configure(progress_color=theme.WARNING_COLOR)
            self.speed_eta_lbl.configure(text=i18n.t("status_paused"))
            from ui.icons import get_icon
            self.pause_resume_btn.configure(
                image=get_icon("play", size=18, color_pair=theme.ACCENT_COLOR)
            )
            self.pause_resume_btn.set_tooltip(i18n.t("tip_resume"))
            self.pause_resume_btn.set_disabled(False)

        elif self.task.status == "completed":
            self.progress_bar.configure(progress_color=theme.SUCCESS_COLOR)
            self.speed_eta_lbl.configure(text=i18n.t("status_completed"))
            self.pause_resume_btn.set_disabled(True)
            self.cancel_btn.set_disabled(True)

        elif self.task.status == "failed":
            self.progress_bar.configure(progress_color=theme.ERROR_COLOR)
            self.speed_eta_lbl.configure(text=i18n.t("status_failed"))
            self.pause_resume_btn.set_disabled(True)
            self.cancel_btn.set_disabled(True)


class ActiveDownloadsPage(ctk.CTkScrollableFrame):
    """صفحة "التحميلات الجارية"."""

    def __init__(
        self,
        master: object,
        downloader: DownloadManager,
        toast: ToastManager,
    ) -> None:
        super().__init__(master, fg_color=theme.COLOR_TRANSPARENT, corner_radius=0)
        self.downloader = downloader
        self.toast = toast
        self._cards: Dict[str, DownloadItemCard] = {}

        self._build_ui()
        self.refresh_list()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color=theme.COLOR_TRANSPARENT)
        header.pack(fill="x", padx=theme.SPACE_LG, pady=(theme.SPACE_SM, theme.SPACE_LG))

        title_box = ctk.CTkFrame(header, fg_color=theme.COLOR_TRANSPARENT)
        title_box.pack(side=i18n.side_start, fill="x", expand=True)

        ctk.CTkLabel(
            title_box,
            text=i18n.t("page_active_title"),
            font=theme.get_title_large_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        ).pack(fill="x")

        ctk.CTkLabel(
            title_box,
            text=i18n.t("page_active_subtitle"),
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(2, 0))

        # أزرار التحكم الجماعي
        toolbar = ctk.CTkFrame(header, fg_color=theme.COLOR_TRANSPARENT)
        toolbar.pack(side=i18n.side_end)

        SecondaryButton(
            toolbar,
            text=i18n.t("btn_pause_all"),
            icon_name="pause",
            width=135,
            command=self.downloader.pause_all,
        ).pack(side=i18n.side_start, padx=theme.SPACE_XS)

        SecondaryButton(
            toolbar,
            text=i18n.t("btn_resume_all"),
            icon_name="play",
            width=125,
            command=self.downloader.resume_all,
        ).pack(side=i18n.side_start, padx=theme.SPACE_XS)

        SecondaryButton(
            toolbar,
            text=i18n.t("btn_clear_completed"),
            icon_name="trash",
            width=130,
            command=self._clear_completed,
        ).pack(side=i18n.side_start, padx=theme.SPACE_XS)

        self.list_container = ctk.CTkFrame(self, fg_color=theme.COLOR_TRANSPARENT)
        self.list_container.pack(fill="both", expand=True, padx=theme.SPACE_LG)

        self.empty_state = EmptyState(
            self.list_container,
            icon_name="inbox",
            title=i18n.t("empty_active_title"),
            subtitle=i18n.t("empty_active_subtitle"),
        )

    def _clear_completed(self) -> None:
        self.downloader.tasks = [
            t for t in self.downloader.tasks if t.status not in ("completed", "failed")
        ]
        self.refresh_list()

    def refresh_list(self) -> None:
        """إعادة بناء أو تحديث قائمة بطاقات التحميل والحالة الفارغة."""
        tasks = self.downloader.tasks
        if not tasks:
            for card in list(self._cards.values()):
                card.destroy()
            self._cards.clear()
            self.empty_state.pack(fill="x", pady=theme.SPACE_XL)
            return

        self.empty_state.pack_forget()

        active_ids = {t.task_id for t in tasks}
        for tid in list(self._cards.keys()):
            if tid not in active_ids:
                self._cards[tid].destroy()
                del self._cards[tid]

        for task in tasks:
            if task.task_id in self._cards:
                self._cards[task.task_id].refresh_from_task()
            else:
                card = DownloadItemCard(
                    self.list_container,
                    task=task,
                    downloader=self.downloader,
                    toast=self.toast,
                )
                card.pack(fill="x", pady=(0, theme.SPACE_LG))
                self._cards[task.task_id] = card

    def update_single_task(self, task: DownloadTask) -> None:
        if task.task_id in self._cards:
            self._cards[task.task_id].refresh_from_task()
        else:
            self.refresh_list()
