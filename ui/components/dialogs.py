"""
نوافذ الحوار المتخصصة:
1) PlaylistDialog: نافذة حوار بتصميم متناسق تعرض فيديوهات قائمة التشغيل كبطاقات صغيرة
   مع Checkbox عصري وشريط بحث وأزرار "تحديد الكل" و"عكس التحديد".
2) WelcomeDialog: شاشة ترحيب مختصرة عند أول تشغيل تشرح الخطوات الأساسية الثلاث.
"""

from typing import Callable, Dict, List, Optional
import customtkinter as ctk

from ui import theme
from ui.i18n import i18n
from ui.icons import get_icon
from ui.components.buttons import PrimaryButton, SecondaryButton


class PlaylistDialog(ctk.CTkToplevel):
    """نافذة حوار اختيار فيديوهات قائمة التشغيل."""

    def __init__(
        self,
        master: ctk.CTk,
        entries: List[Dict[str, object]],
        selected_indices: Optional[List[int]],
        on_confirm: Callable[[List[int]], None],
    ) -> None:
        super().__init__(master)
        self.entries = entries
        self.on_confirm = on_confirm
        self.title(i18n.t("playlist_dialog_title"))
        self.geometry("680x540")
        self.minsize(580, 440)
        self.configure(fg_color=theme.BG_MAIN)
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        initial_set = (
            set(selected_indices)
            if selected_indices is not None
            else set(range(len(entries)))
        )
        self._vars: Dict[int, ctk.BooleanVar] = {
            idx: ctk.BooleanVar(value=(idx in initial_set))
            for idx in range(len(entries))
        }
        self._row_frames: Dict[int, ctk.CTkFrame] = {}

        self._build_ui()
        self._update_counter()

    def _build_ui(self) -> None:
        container = ctk.CTkFrame(self, fg_color=theme.COLOR_TRANSPARENT)
        container.pack(fill="both", expand=True, padx=theme.SPACE_XXL, pady=theme.SPACE_XXL)

        # العنوان وعداد التحديد
        header = ctk.CTkFrame(container, fg_color=theme.COLOR_TRANSPARENT)
        header.pack(fill="x", pady=(0, theme.SPACE_MD))

        title_lbl = ctk.CTkLabel(
            header,
            text=i18n.t("playlist_dialog_title"),
            font=theme.get_section_title_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
        )
        title_lbl.pack(side=i18n.side_start)

        self.count_lbl = ctk.CTkLabel(
            header,
            text="",
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.ACCENT_COLOR,
        )
        self.count_lbl.pack(side=i18n.side_end)

        # شريط البحث وأزرار تحديد الكل / عكس
        toolbar = ctk.CTkFrame(container, fg_color=theme.COLOR_TRANSPARENT)
        toolbar.pack(fill="x", pady=(0, theme.SPACE_MD))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter_rows())

        self.search_entry = ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            placeholder_text=i18n.t("playlist_search_placeholder"),
            height=theme.BUTTON_HEIGHT,
            corner_radius=theme.RADIUS_INPUT,
            fg_color=theme.BG_CARD,
            border_color=theme.BORDER_COLOR,
            border_width=theme.BORDER_WIDTH_THIN,
            text_color=theme.TEXT_PRIMARY,
            font=theme.get_body_font(i18n.lang),
            justify=i18n.justify,
        )
        self.search_entry.pack(
            side=i18n.side_start,
            fill="x",
            expand=True,
            padx=(0, theme.SPACE_SM) if not i18n.is_rtl else (theme.SPACE_SM, 0),
        )

        invert_btn = SecondaryButton(
            toolbar,
            text=i18n.t("playlist_invert"),
            icon_name="refresh",
            width=120,
            command=self._invert_selection,
        )
        invert_btn.pack(side=i18n.side_end, padx=(theme.SPACE_XS, 0) if not i18n.is_rtl else (0, theme.SPACE_XS))

        select_all_btn = SecondaryButton(
            toolbar,
            text=i18n.t("playlist_select_all"),
            icon_name="check",
            width=120,
            command=self._select_all,
        )
        select_all_btn.pack(side=i18n.side_end)

        # قائمة البطاقات الصغيرة القابلة للتمرير
        self.scroll = ctk.CTkScrollableFrame(
            container,
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_COLOR,
            border_width=theme.BORDER_WIDTH_THIN,
            corner_radius=theme.RADIUS_CARD,
        )
        self.scroll.pack(fill="both", expand=True, pady=(0, theme.SPACE_LG))

        for idx, item in enumerate(self.entries):
            card = ctk.CTkFrame(
                self.scroll,
                fg_color=theme.BG_CARD,
                border_color=theme.BORDER_COLOR,
                border_width=theme.BORDER_WIDTH_THIN,
                corner_radius=theme.RADIUS_CHIP,
            )
            card.pack(fill="x", padx=theme.SPACE_SM, pady=theme.SPACE_XS)

            title = str(item.get("title") or f"Video #{idx + 1}")
            duration = str(item.get("duration_str") or "")

            cb = ctk.CTkCheckBox(
                card,
                text=f"{idx + 1}. {title}",
                variable=self._vars[idx],
                command=self._update_counter,
                font=theme.get_body_font(i18n.lang),
                text_color=theme.TEXT_PRIMARY,
                fg_color=theme.PRIMARY_COLOR,
                hover_color=theme.PRIMARY_HOVER,
                border_color=theme.BORDER_COLOR,
                checkmark_color=theme.COLOR_ON_PRIMARY,
                corner_radius=6,
            )
            cb.pack(
                side=i18n.side_start,
                padx=theme.SPACE_MD,
                pady=theme.SPACE_MD,
                fill="x",
                expand=True,
            )

            if duration:
                dur_lbl = ctk.CTkLabel(
                    card,
                    text=duration,
                    font=theme.get_small_font(i18n.lang),
                    text_color=theme.TEXT_SECONDARY,
                )
                dur_lbl.pack(side=i18n.side_end, padx=theme.SPACE_MD)

            self._row_frames[idx] = card

        # أزرار التأكيد والإلغاء
        footer = ctk.CTkFrame(container, fg_color=theme.COLOR_TRANSPARENT)
        footer.pack(fill="x")

        confirm_btn = PrimaryButton(
            footer,
            text=i18n.t("playlist_confirm"),
            icon_name="check",
            width=160,
            command=self._confirm,
        )
        confirm_btn.pack(side=i18n.side_end)

        cancel_btn = SecondaryButton(
            footer,
            text=i18n.t("playlist_cancel"),
            icon_name="x",
            width=110,
            command=self.destroy,
        )
        cancel_btn.pack(
            side=i18n.side_end,
            padx=(0, theme.SPACE_SM) if not i18n.is_rtl else (theme.SPACE_SM, 0),
        )

    def _select_all(self) -> None:
        for idx, card in self._row_frames.items():
            if card.winfo_manager():
                self._vars[idx].set(True)
        self._update_counter()

    def _invert_selection(self) -> None:
        for idx, card in self._row_frames.items():
            if card.winfo_manager():
                self._vars[idx].set(not self._vars[idx].get())
        self._update_counter()

    def _filter_rows(self) -> None:
        query = self.search_var.get().strip().lower()
        for idx, item in enumerate(self.entries):
            title = str(item.get("title") or "").lower()
            card = self._row_frames[idx]
            if not query or query in title:
                card.pack(fill="x", padx=theme.SPACE_SM, pady=theme.SPACE_XS)
            else:
                card.pack_forget()

    def _update_counter(self) -> None:
        selected = sum(1 for v in self._vars.values() if v.get())
        self.count_lbl.configure(
            text=i18n.t(
                "playlist_selected_count",
                selected=selected,
                total=len(self.entries),
            )
        )

    def _confirm(self) -> None:
        chosen = [idx for idx, var in self._vars.items() if var.get()]
        self.on_confirm(chosen)
        self.destroy()


class WelcomeDialog(ctk.CTkToplevel):
    """شاشة ترحيب مختصرة عند أول تشغيل تشرح الخطوات الأساسية الثلاث."""

    def __init__(self, master: ctk.CTk, on_close: Optional[Callable[[], None]] = None) -> None:
        super().__init__(master)
        self.on_close = on_close
        self.title(i18n.t("welcome_title"))
        self.geometry("560x470")
        self.resizable(False, False)
        self.configure(fg_color=theme.BG_MAIN)
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._finish)

        card = ctk.CTkFrame(
            self,
            fg_color=theme.BG_CARD,
            border_color=theme.BORDER_COLOR,
            border_width=theme.BORDER_WIDTH_THIN,
            corner_radius=theme.RADIUS_CARD,
        )
        card.pack(fill="both", expand=True, padx=theme.SPACE_XXL, pady=theme.SPACE_XXL)

        inner = ctk.CTkFrame(card, fg_color=theme.COLOR_TRANSPARENT)
        inner.pack(fill="both", expand=True, padx=theme.SPACE_XXL, pady=theme.SPACE_XXL)

        title_lbl = ctk.CTkLabel(
            inner,
            text=i18n.t("welcome_title"),
            font=theme.get_title_large_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
        )
        title_lbl.pack(pady=(0, theme.SPACE_XS))

        sub_lbl = ctk.CTkLabel(
            inner,
            text=i18n.t("welcome_subtitle"),
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
            wraplength=460,
        )
        sub_lbl.pack(pady=(0, theme.SPACE_XL))

        steps = [
            ("link", i18n.t("welcome_step1_title"), i18n.t("welcome_step1_desc")),
            ("sparkles", i18n.t("welcome_step2_title"), i18n.t("welcome_step2_desc")),
            ("download", i18n.t("welcome_step3_title"), i18n.t("welcome_step3_desc")),
        ]

        for icon_name, st_title, st_desc in steps:
            row = ctk.CTkFrame(
                inner,
                fg_color=theme.BG_INPUT,
                corner_radius=theme.RADIUS_BUTTON,
            )
            row.pack(fill="x", pady=theme.SPACE_XS)

            badge = ctk.CTkFrame(
                row,
                width=42,
                height=42,
                corner_radius=theme.RADIUS_CHIP,
                fg_color=theme.PRIMARY_TINT,
            )
            badge.pack(side=i18n.side_start, padx=theme.SPACE_MD, pady=theme.SPACE_MD)
            badge.pack_propagate(False)

            ic = ctk.CTkLabel(
                badge,
                text="",
                image=get_icon(icon_name, size=20, color_pair=theme.PRIMARY_COLOR),
            )
            ic.place(relx=0.5, rely=0.5, anchor="center")

            txt_box = ctk.CTkFrame(row, fg_color=theme.COLOR_TRANSPARENT)
            txt_box.pack(
                side=i18n.side_start,
                fill="x",
                expand=True,
                padx=(0, theme.SPACE_MD) if not i18n.is_rtl else (theme.SPACE_MD, 0),
                pady=theme.SPACE_SM,
            )

            ctk.CTkLabel(
                txt_box,
                text=st_title,
                font=theme.get_body_font(i18n.lang, bold=True),
                text_color=theme.TEXT_PRIMARY,
                anchor=i18n.align_start,
            ).pack(fill="x")

            ctk.CTkLabel(
                txt_box,
                text=st_desc,
                font=theme.get_small_font(i18n.lang),
                text_color=theme.TEXT_SECONDARY,
                anchor=i18n.align_start,
                justify=i18n.justify,
                wraplength=370,
            ).pack(fill="x")

        ctk.CTkLabel(
            inner,
            text="Developed with care by Ahmed Hagag  •  ahmed.m.hagag22@gmail.com",
            font=theme.get_small_font(i18n.lang),
            text_color=theme.TEXT_MUTED,
            justify="center",
        ).pack(fill="x", pady=(theme.SPACE_MD, 0))

        start_btn = PrimaryButton(
            inner,
            text=i18n.t("welcome_start_btn"),
            icon_name="check",
            command=self._finish,
        )
        start_btn.pack(fill="x", pady=(theme.SPACE_MD, 0))

    def _finish(self) -> None:
        try:
            self.grab_release()
        except Exception:
            pass
        if self.on_close:
            self.on_close()
        self.destroy()
