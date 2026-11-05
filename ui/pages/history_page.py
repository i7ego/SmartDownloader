"""
صفحة "السجل" (سجل التحميلات السابقة) - ui/pages/history_page.py
تضم:
- شريط بحث فوري لتصفية السجل وزر مسح السجل.
- بطاقات متناسقة لعناصر السجل مع شارات مكتمل وأزرار أيقونات (فتح المجلد / حذف).
- حالة فارغة (Empty State) جميلة عندما لا توجد عناصر في السجل.
"""

from typing import Any, Callable, Dict, Optional
from pathlib import Path
import customtkinter as ctk

from core.downloader import open_folder_in_explorer
from core.storage import StorageManager
from ui import theme
from ui.i18n import i18n
from ui.components.buttons import GhostIconButton, SecondaryButton
from ui.components.feedback import ToastManager
from ui.components.widgets import EmptyState, HoverCard, StatusBadge


class HistoryPage(ctk.CTkScrollableFrame):
    """صفحة "السجل"."""

    def __init__(
        self,
        master: object,
        storage: StorageManager,
        toast: ToastManager,
        on_cut_item: Optional[Callable[[str], None]] = None,
        on_convert_item: Optional[Callable[[str], None]] = None,
    ) -> None:
        super().__init__(master, fg_color=theme.COLOR_TRANSPARENT, corner_radius=0)
        self.storage = storage
        self.toast = toast
        self.on_cut_item = on_cut_item
        self.on_convert_item = on_convert_item

        self._build_ui()
        self.refresh_history()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color=theme.COLOR_TRANSPARENT)
        header.pack(fill="x", padx=theme.SPACE_LG, pady=(theme.SPACE_SM, theme.SPACE_LG))

        title_box = ctk.CTkFrame(header, fg_color=theme.COLOR_TRANSPARENT)
        title_box.pack(side=i18n.side_start, fill="x", expand=True)

        ctk.CTkLabel(
            title_box,
            text=i18n.t("page_history_title"),
            font=theme.get_title_large_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        ).pack(fill="x")

        ctk.CTkLabel(
            title_box,
            text=i18n.t("page_history_subtitle"),
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(fill="x", pady=(2, 0))

        SecondaryButton(
            header,
            text=i18n.t("btn_clear_history"),
            icon_name="trash",
            width=130,
            command=self._clear_all,
        ).pack(side=i18n.side_end)

        # شريط البحث في السجل
        search_bar = ctk.CTkFrame(self, fg_color=theme.COLOR_TRANSPARENT)
        search_bar.pack(fill="x", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_history())

        search_entry = ctk.CTkEntry(
            search_bar,
            textvariable=self.search_var,
            placeholder_text=i18n.t("search_history_placeholder"),
            height=theme.BUTTON_HEIGHT,
            corner_radius=theme.RADIUS_INPUT,
            fg_color=theme.BG_CARD,
            border_color=theme.BORDER_COLOR,
            border_width=theme.BORDER_WIDTH_THIN,
            text_color=theme.TEXT_PRIMARY,
            font=theme.get_body_font(i18n.lang),
            justify=i18n.justify,
        )
        search_entry.pack(fill="x")

        self.list_container = ctk.CTkFrame(self, fg_color=theme.COLOR_TRANSPARENT)
        self.list_container.pack(fill="both", expand=True, padx=theme.SPACE_LG)

        self.empty_state = EmptyState(
            self.list_container,
            icon_name="history",
            title=i18n.t("empty_history_title"),
            subtitle=i18n.t("empty_history_subtitle"),
        )

    def refresh_history(self) -> None:
        for child in self.list_container.winfo_children():
            if child is not self.empty_state:
                child.destroy()

        query = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
        items = [
            item
            for item in self.storage.history
            if not query
            or query in str(item.get("title", "")).lower()
            or query in str(item.get("channel", "")).lower()
        ]

        if not items:
            self.empty_state.pack(fill="x", pady=theme.SPACE_XL)
            return

        self.empty_state.pack_forget()

        for entry in items:
            self._create_history_card(entry)

    def _create_history_card(self, entry: Dict[str, Any]) -> None:
        card = HoverCard(self.list_container)
        card.pack(fill="x", pady=(0, theme.SPACE_LG))

        inner = ctk.CTkFrame(card, fg_color=theme.COLOR_TRANSPARENT)
        inner.pack(fill="x", padx=theme.SPACE_LG, pady=theme.SPACE_LG)

        info_col = ctk.CTkFrame(inner, fg_color=theme.COLOR_TRANSPARENT)
        info_col.pack(side=i18n.side_start, fill="both", expand=True)

        top_row = ctk.CTkFrame(info_col, fg_color=theme.COLOR_TRANSPARENT)
        top_row.pack(fill="x", pady=(0, theme.SPACE_XS))

        ctk.CTkLabel(
            top_row,
            text=str(entry.get("title") or ""),
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_PRIMARY,
            anchor=i18n.align_start,
        ).pack(side=i18n.side_start, fill="x", expand=True)

        StatusBadge(top_row, status="completed").pack(
            side=i18n.side_end,
            padx=(theme.SPACE_SM, 0) if not i18n.is_rtl else (0, theme.SPACE_SM),
        )

        meta_text = (
            f"{entry.get('channel', '')}  •  "
            f"{entry.get('quality', '')} ({entry.get('format', '')})  •  "
            f"{entry.get('completed_at', '')}"
        )
        ctk.CTkLabel(
            info_col,
            text=meta_text,
            font=theme.get_small_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
            anchor=i18n.align_start,
        ).pack(fill="x")

        actions = ctk.CTkFrame(inner, fg_color=theme.COLOR_TRANSPARENT)
        actions.pack(
            side=i18n.side_end,
            padx=(theme.SPACE_MD, 0) if not i18n.is_rtl else (0, theme.SPACE_MD),
        )

        save_path = str(entry.get("save_path") or "")
        entry_id = str(entry.get("id") or "")

        if self.on_cut_item:
            GhostIconButton(
                actions,
                icon_name="scissors",
                tooltip=i18n.t("tip_cut_audio"),
                icon_color=theme.PRIMARY_COLOR,
                command=lambda e=entry: self._trigger_cut(e),
            ).pack(side=i18n.side_start, padx=2)

        if self.on_convert_item:
            GhostIconButton(
                actions,
                icon_name="refresh",
                tooltip=i18n.t("tip_convert_media"),
                icon_color=theme.ACCENT_COLOR,
                command=lambda e=entry: self._trigger_convert(e),
            ).pack(side=i18n.side_start, padx=2)

        GhostIconButton(
            actions,
            icon_name="folder",
            tooltip=i18n.t("tip_open_folder"),
            icon_color=theme.ACCENT_COLOR,
            command=lambda p=save_path: self._open_folder(p),
        ).pack(side=i18n.side_start, padx=2)

        GhostIconButton(
            actions,
            icon_name="trash",
            tooltip=i18n.t("tip_delete_record"),
            icon_color=theme.ERROR_COLOR,
            command=lambda eid=entry_id: self._delete_item(eid),
        ).pack(side=i18n.side_start, padx=2)

    def _trigger_cut(self, entry: Dict[str, Any]) -> None:
        """العثور على الملف وتحويله لصفحة التقطيع."""
        if not self.on_cut_item:
            return
        save_dir = Path(str(entry.get("save_path") or ""))
        title = str(entry.get("title") or "")
        fmt = str(entry.get("format") or "").lower()

        target_file: Optional[Path] = None
        if save_dir.is_file():
            target_file = save_dir
        elif save_dir.exists():
            # البحث عن الملف بالاسم والصيغة
            exact = save_dir / f"{title}.{fmt}"
            if exact.exists():
                target_file = exact
            else:
                for candidate in save_dir.glob(f"*{fmt}*"):
                    if candidate.is_file():
                        target_file = candidate
                        break

        if target_file and target_file.exists():
            self.on_cut_item(str(target_file))
        else:
            self.toast.show(i18n.t("toast_folder_missing"), kind="error")

    def _trigger_convert(self, entry: Dict[str, Any]) -> None:
        """العثور على الملف وتحويله لصفحة تحويل الفيديوهات."""
        if not self.on_convert_item:
            return
        save_dir = Path(str(entry.get("save_path") or ""))
        title = str(entry.get("title") or "")
        fmt = str(entry.get("format") or "").lower()

        target_file: Optional[Path] = None
        if save_dir.is_file():
            target_file = save_dir
        elif save_dir.exists():
            exact = save_dir / f"{title}.{fmt}"
            if exact.exists():
                target_file = exact
            else:
                for candidate in save_dir.glob(f"*{fmt}*"):
                    if candidate.is_file():
                        target_file = candidate
                        break

        if target_file and target_file.exists():
            self.on_convert_item(str(target_file))
        else:
            self.toast.show(i18n.t("toast_folder_missing"), kind="error")

    def _open_folder(self, path: str) -> None:
        if not open_folder_in_explorer(path):
            self.toast.show(i18n.t("toast_folder_missing"), kind="error")

    def _delete_item(self, entry_id: str) -> None:
        self.storage.remove_history_entry(entry_id)
        self.refresh_history()

    def _clear_all(self) -> None:
        self.storage.clear_history()
        self.refresh_history()
        self.toast.show(i18n.t("toast_history_cleared"), kind="info")
