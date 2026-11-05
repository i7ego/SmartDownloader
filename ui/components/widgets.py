"""
مكوّنات الواجهة التفاعلية:
- HoverCard: بطاقة بزوايا مستديرة (16px) وحدود خفيفة وتأثير تحويم.
- ChipSelector: شرائح اختيار الجودة والصيغة ([4K] [1080p] [720p] + قائمة "المزيد").
- StatusBadge: شارات ملوّنة لحالة التحميل (قيد التحميل، مكتمل، متوقف، فشل).
- MediaTypeSegmentedSwitch: مفتاح مقسّم كبير (فيديو | صوت) مع حركة سلسة.
- CollapsibleSection: قسم قابل للطي للخيارات المتقدمة.
- EmptyState: حالات فارغة جميلة بأيقونة ونص ودود.
"""

from typing import Callable, List, Optional, Tuple
import tkinter as tk
import customtkinter as ctk

from ui import theme
from ui.i18n import i18n
from ui.icons import get_icon


class HoverCard(ctk.CTkFrame):
    """بطاقة محتوى بزوايا مستديرة (RADIUS_CARD) وحدود خفيفة وتأثير تحويم اختياري."""

    def __init__(
        self,
        master: object,
        hover_effect: bool = True,
        **kwargs: object,
    ) -> None:
        super().__init__(
            master,
            fg_color=theme.BG_CARD,
            border_color=theme.BORDER_COLOR,
            border_width=theme.BORDER_WIDTH_THIN,
            corner_radius=theme.RADIUS_CARD,
            **kwargs,
        )
        self._hover_effect = hover_effect
        if hover_effect:
            self.bind("<Enter>", self._on_enter, add="+")
            self.bind("<Leave>", self._on_leave, add="+")

    def _on_enter(self, _event: object = None) -> None:
        if self._hover_effect:
            self.configure(border_color=theme.PRIMARY_COLOR)

    def _on_leave(self, _event: object = None) -> None:
        if self._hover_effect:
            self.configure(border_color=theme.BORDER_COLOR)


class ChipSelector(ctk.CTkFrame):
    """
    شرائح (Chips) قابلة للاختيار مثل [4K] [1080p] [720p] أو [MP4] [MKV] [WEBM].
    الشريحة المختارة تتلوّن بلون Primary، وتوجد قائمة "المزيد" للخيارات الأقل استخداماً.
    """

    def __init__(
        self,
        master: object,
        primary_options: List[str],
        more_options: Optional[List[str]] = None,
        default_value: Optional[str] = None,
        on_change: Optional[Callable[[str], None]] = None,
        **kwargs: object,
    ) -> None:
        super().__init__(master, fg_color=theme.COLOR_TRANSPARENT, **kwargs)
        self.primary_options = list(primary_options)
        self.more_options = list(more_options or [])
        self.on_change = on_change
        self._selected = default_value or (self.primary_options[0] if self.primary_options else "")
        self._chip_buttons: dict[str, ctk.CTkButton] = {}
        self._more_btn: Optional[ctk.CTkButton] = None

        self._build_chips()

    @property
    def value(self) -> str:
        return self._selected

    def set_options(
        self,
        primary_options: List[str],
        more_options: Optional[List[str]] = None,
        selected: Optional[str] = None,
    ) -> None:
        self.primary_options = list(primary_options)
        self.more_options = list(more_options or [])
        if selected is not None:
            self._selected = selected
        elif self._selected not in self.primary_options and self._selected not in self.more_options:
            self._selected = self.primary_options[0] if self.primary_options else ""
        self._build_chips()

    def set_value(self, value: str, trigger_callback: bool = False) -> None:
        self._selected = value
        self._refresh_visuals()
        if trigger_callback and self.on_change:
            self.on_change(self._selected)

    def _build_chips(self) -> None:
        for child in self.winfo_children():
            child.destroy()
        self._chip_buttons.clear()
        self._more_btn = None

        side = i18n.side_start
        pad_x = (0, theme.SPACE_SM) if not i18n.is_rtl else (theme.SPACE_SM, 0)

        for opt in self.primary_options:
            btn = ctk.CTkButton(
                self,
                text=opt,
                height=theme.BUTTON_SMALL_HEIGHT,
                width=max(64, len(opt) * 11 + 24),
                corner_radius=theme.RADIUS_CHIP,
                font=theme.get_body_font(i18n.lang, bold=True),
                border_width=theme.BORDER_WIDTH_THIN,
                command=lambda val=opt: self.set_value(val, trigger_callback=True),
            )
            btn.pack(side=side, padx=pad_x, pady=theme.SPACE_XS)
            self._chip_buttons[opt] = btn

        if self.more_options:
            self._more_btn = ctk.CTkButton(
                self,
                text=i18n.t("chip_more"),
                height=theme.BUTTON_SMALL_HEIGHT,
                width=86,
                corner_radius=theme.RADIUS_CHIP,
                font=theme.get_small_font(i18n.lang, bold=True),
                border_width=theme.BORDER_WIDTH_THIN,
                command=self._open_more_menu,
            )
            self._more_btn.pack(side=side, padx=pad_x, pady=theme.SPACE_XS)

        self._refresh_visuals()

    def _refresh_visuals(self) -> None:
        for opt, btn in self._chip_buttons.items():
            is_sel = opt == self._selected
            btn.configure(
                fg_color=theme.PRIMARY_COLOR if is_sel else theme.BG_ELEVATED,
                hover_color=theme.PRIMARY_HOVER if is_sel else theme.GHOST_HOVER,
                text_color=theme.COLOR_ON_PRIMARY if is_sel else theme.TEXT_PRIMARY,
                border_color=theme.PRIMARY_COLOR if is_sel else theme.BORDER_COLOR,
            )

        if self._more_btn:
            in_more = self._selected in self.more_options
            label = f"{self._selected} ▾" if in_more else i18n.t("chip_more")
            self._more_btn.configure(
                text=label,
                fg_color=theme.PRIMARY_COLOR if in_more else theme.COLOR_TRANSPARENT,
                hover_color=theme.PRIMARY_HOVER if in_more else theme.GHOST_HOVER,
                text_color=theme.COLOR_ON_PRIMARY if in_more else theme.TEXT_SECONDARY,
                border_color=theme.PRIMARY_COLOR if in_more else theme.BORDER_COLOR,
            )

    def _open_more_menu(self) -> None:
        if not self._more_btn or not self.more_options:
            return
        menu = tk.Menu(
            self,
            tearoff=0,
            bg=theme.resolve_color(theme.BG_ELEVATED),
            fg=theme.resolve_color(theme.TEXT_PRIMARY),
            activebackground=theme.COLOR_PRIMARY,
            activeforeground=theme.COLOR_ON_PRIMARY,
            relief="flat",
            bd=1,
        )
        for opt in self.more_options:
            menu.add_command(
                label=f"  {opt}  ",
                command=lambda val=opt: self.set_value(val, trigger_callback=True),
            )
        x = self._more_btn.winfo_rootx()
        y = self._more_btn.winfo_rooty() + self._more_btn.winfo_height() + 2
        menu.tk_popup(x, y)


class MediaTypeSegmentedSwitch(ctk.CTkFrame):
    """
    مفتاح مقسّم (Segmented Button) كبير لخيار (فيديو | صوت).
    """

    def __init__(
        self,
        master: object,
        default_mode: str = "video",
        on_change: Optional[Callable[[str], None]] = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            master,
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_COLOR,
            border_width=theme.BORDER_WIDTH_THIN,
            corner_radius=theme.RADIUS_BUTTON,
            **kwargs,
        )
        self._mode = default_mode
        self.on_change = on_change

        self.grid_columnconfigure((0, 1), weight=1)

        compound = "right" if i18n.is_rtl else "left"
        vid_col = 1 if i18n.is_rtl else 0
        aud_col = 0 if i18n.is_rtl else 1

        self.video_btn = ctk.CTkButton(
            self,
            text=i18n.t("mode_video"),
            image=get_icon("video", size=18, color_pair=(theme.COLOR_ON_PRIMARY, theme.COLOR_ON_PRIMARY)),
            compound=compound,
            height=theme.BUTTON_HEIGHT,
            corner_radius=theme.RADIUS_CHIP,
            font=theme.get_body_font(i18n.lang, bold=True),
            command=lambda: self.set_mode("video", trigger=True),
        )
        self.video_btn.grid(row=0, column=vid_col, sticky="ew", padx=theme.SPACE_XS, pady=theme.SPACE_XS)

        self.audio_btn = ctk.CTkButton(
            self,
            text=i18n.t("mode_audio"),
            image=get_icon("music", size=18, color_pair=theme.TEXT_SECONDARY),
            compound=compound,
            height=theme.BUTTON_HEIGHT,
            corner_radius=theme.RADIUS_CHIP,
            font=theme.get_body_font(i18n.lang, bold=True),
            command=lambda: self.set_mode("audio", trigger=True),
        )
        self.audio_btn.grid(row=0, column=aud_col, sticky="ew", padx=theme.SPACE_XS, pady=theme.SPACE_XS)

        self._refresh_visuals()

    @property
    def mode(self) -> str:
        return self._mode

    def set_mode(self, mode: str, trigger: bool = False) -> None:
        if mode not in ("video", "audio"):
            return
        self._mode = mode
        self._refresh_visuals()
        if trigger and self.on_change:
            self.on_change(self._mode)

    def _refresh_visuals(self) -> None:
        is_video = self._mode == "video"
        self.video_btn.configure(
            fg_color=theme.PRIMARY_COLOR if is_video else theme.COLOR_TRANSPARENT,
            hover_color=theme.PRIMARY_HOVER if is_video else theme.GHOST_HOVER,
            text_color=theme.COLOR_ON_PRIMARY if is_video else theme.TEXT_SECONDARY,
            image=get_icon(
                "video",
                size=18,
                color_pair=(theme.COLOR_ON_PRIMARY, theme.COLOR_ON_PRIMARY)
                if is_video
                else theme.TEXT_SECONDARY,
            ),
        )
        self.audio_btn.configure(
            fg_color=theme.PRIMARY_COLOR if not is_video else theme.COLOR_TRANSPARENT,
            hover_color=theme.PRIMARY_HOVER if not is_video else theme.GHOST_HOVER,
            text_color=theme.COLOR_ON_PRIMARY if not is_video else theme.TEXT_SECONDARY,
            image=get_icon(
                "music",
                size=18,
                color_pair=(theme.COLOR_ON_PRIMARY, theme.COLOR_ON_PRIMARY)
                if not is_video
                else theme.TEXT_SECONDARY,
            ),
        )


class StatusBadge(ctk.CTkFrame):
    """
    شارات (Badges) ملوّنة للحالة:
    - downloading: قيد التحميل (أزرق/تركواز Accent)
    - completed: مكتمل (أخضر Success)
    - paused: متوقف (برتقالي Warning)
    - failed: فشل (أحمر Error)
    """

    STATUS_STYLES: dict[str, Tuple[Tuple[str, str], Tuple[str, str], str]] = {
        "downloading": (theme.ACCENT_COLOR, theme.ACCENT_TINT, "status_downloading"),
        "queued": (theme.ACCENT_COLOR, theme.ACCENT_TINT, "status_queued"),
        "completed": (theme.SUCCESS_COLOR, theme.SUCCESS_TINT, "status_completed"),
        "paused": (theme.WARNING_COLOR, theme.WARNING_TINT, "status_paused"),
        "failed": (theme.ERROR_COLOR, theme.ERROR_TINT, "status_failed"),
    }

    def __init__(
        self,
        master: object,
        status: str = "downloading",
        text: Optional[str] = None,
        kind: Optional[str] = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            master,
            corner_radius=theme.RADIUS_CHIP,
            border_width=theme.BORDER_WIDTH_THIN,
            **kwargs,
        )
        self._label = ctk.CTkLabel(
            self,
            text="",
            font=theme.get_small_font(i18n.lang, bold=True),
            padx=theme.SPACE_MD,
            pady=2,
        )
        self._label.pack()
        if text:
            fg_color = theme.ACCENT_COLOR if kind == "accent" else theme.PRIMARY_COLOR
            bg_tint = theme.ACCENT_TINT if kind == "accent" else theme.PRIMARY_TINT
            self.set_custom_badge(text, fg_color, bg_tint)
        else:
            self.set_status(status)

    def set_custom_badge(self, text: str, fg_text: Tuple[str, str], bg_tint: Tuple[str, str]) -> None:
        self.configure(fg_color=bg_tint, border_color=fg_text)
        self._label.configure(text=text, text_color=fg_text)

    def set_status(self, status: str) -> None:
        fg_text, bg_tint, key = self.STATUS_STYLES.get(
            status, self.STATUS_STYLES["downloading"]
        )
        self.configure(fg_color=bg_tint, border_color=fg_text)
        self._label.configure(text=i18n.t(key), text_color=fg_text)


class CollapsibleSection(ctk.CTkFrame):
    """قسم قابل للطي (مثل "خيارات متقدمة") مخفي افتراضياً لسهولة الاستخدام."""

    def __init__(self, master: object, title: str, **kwargs: object) -> None:
        super().__init__(
            master,
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_COLOR,
            border_width=theme.BORDER_WIDTH_THIN,
            corner_radius=theme.RADIUS_BUTTON,
            **kwargs,
        )
        self._expanded = False
        self._title = title

        compound = "right" if i18n.is_rtl else "left"
        anchor = "e" if i18n.is_rtl else "w"

        self.header_btn = ctk.CTkButton(
            self,
            text=title,
            image=get_icon("chevron_down", size=18, color_pair=theme.TEXT_SECONDARY),
            compound=compound,
            anchor=anchor,
            height=theme.BUTTON_SMALL_HEIGHT,
            fg_color=theme.COLOR_TRANSPARENT,
            hover_color=theme.GHOST_HOVER,
            text_color=theme.TEXT_SECONDARY,
            font=theme.get_body_font(i18n.lang, bold=True),
            corner_radius=theme.RADIUS_BUTTON,
            command=self.toggle,
        )
        self.header_btn.pack(fill="x", padx=theme.SPACE_SM, pady=theme.SPACE_XS)

        self.content_frame = ctk.CTkFrame(self, fg_color=theme.COLOR_TRANSPARENT)

    def toggle(self) -> None:
        self._expanded = not self._expanded
        icon_name = "chevron_up" if self._expanded else "chevron_down"
        self.header_btn.configure(
            image=get_icon(icon_name, size=18, color_pair=theme.TEXT_SECONDARY)
        )
        if self._expanded:
            self.content_frame.pack(
                fill="x",
                padx=theme.SPACE_LG,
                pady=(theme.SPACE_XS, theme.SPACE_MD),
            )
        else:
            self.content_frame.pack_forget()


class EmptyState(ctk.CTkFrame):
    """حالة فارغة (Empty State) جميلة بأيقونة ونص ودود عندما لا توجد تحميلات."""

    def __init__(
        self,
        master: object,
        icon_name: str,
        title: str,
        subtitle: str,
        **kwargs: object,
    ) -> None:
        super().__init__(
            master,
            fg_color=theme.BG_CARD,
            border_color=theme.BORDER_COLOR,
            border_width=theme.BORDER_WIDTH_THIN,
            corner_radius=theme.RADIUS_CARD,
            **kwargs,
        )
        inner = ctk.CTkFrame(self, fg_color=theme.COLOR_TRANSPARENT)
        inner.pack(expand=True, pady=theme.SPACE_XXL * 2, padx=theme.SPACE_XXL)

        icon_circle = ctk.CTkFrame(
            inner,
            width=72,
            height=72,
            corner_radius=36,
            fg_color=theme.PRIMARY_TINT,
        )
        icon_circle.pack(pady=(0, theme.SPACE_LG))
        icon_circle.pack_propagate(False)

        icon_lbl = ctk.CTkLabel(
            icon_circle,
            text="",
            image=get_icon(icon_name, size=34, color_pair=theme.PRIMARY_COLOR),
        )
        icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        title_lbl = ctk.CTkLabel(
            inner,
            text=title,
            font=theme.get_section_title_font(i18n.lang),
            text_color=theme.TEXT_PRIMARY,
        )
        title_lbl.pack(pady=(0, theme.SPACE_XS))

        sub_lbl = ctk.CTkLabel(
            inner,
            text=subtitle,
            font=theme.get_body_font(i18n.lang),
            text_color=theme.TEXT_SECONDARY,
            wraplength=480,
        )
        sub_lbl.pack()
