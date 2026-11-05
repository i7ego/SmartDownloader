"""
الأزرار الموحدة وفق المواصفات:
1) PrimaryButton: خلفية ملوّنة ونص أبيض، للإجراء الرئيسي.
2) SecondaryButton: خلفية شفافة مع حدود رفيعة، للإجراءات الثانوية.
3) GhostIconButton: أيقونة فقط بدون خلفية وتظهر خلفية خفيفة عند التحويم، لأزرار الجدول/البطاقات.

جميع الأزرار:
- بزوايا مستديرة (RADIUS_BUTTON = 12px)
- ارتفاع ثابت (BUTTON_HEIGHT = 42px)
- أيقونة قبل النص (حسب اتجاه اللغة RTL/LTR)
- حالات واضحة: عادي، تحويم (Hover)، ضغط (Pressed)، معطّل (Disabled)، وتحميل (Loading) مع مؤشر دوّار.
- نص مساعد (Tooltip) عند تحويم الماوس.
"""

from typing import Callable, Optional, Tuple
import customtkinter as ctk

from ui import theme
from ui.i18n import i18n
from ui.icons import get_icon
from ui.components.feedback import Tooltip

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class BaseAppButton(ctk.CTkButton):
    """الفئة الأساسية للأزرار مع دعم حالات التحميل، الضغط، التعطيل، والتلميحات."""

    def __init__(
        self,
        master: object,
        text: str = "",
        icon_name: Optional[str] = None,
        icon_color: Optional[Tuple[str, str]] = None,
        command: Optional[Callable[[], None]] = None,
        tooltip: str = "",
        height: int = theme.BUTTON_HEIGHT,
        width: int = 120,
        normal_fg: Tuple[str, str] | str = theme.PRIMARY_COLOR,
        hover_fg: Tuple[str, str] | str = theme.PRIMARY_HOVER,
        pressed_fg: Tuple[str, str] | str = theme.PRIMARY_PRESSED,
        disabled_fg: Tuple[str, str] | str = theme.PRIMARY_DISABLED,
        normal_text_color: Tuple[str, str] | str = theme.COLOR_ON_PRIMARY,
        disabled_text_color: Tuple[str, str] | str = theme.TEXT_MUTED,
        border_width: int = 0,
        border_color: Tuple[str, str] | str = theme.BORDER_COLOR,
        bold: bool = True,
        **kwargs: object,
    ) -> None:
        self._original_text = text
        self._icon_name = icon_name
        self._icon_color = icon_color
        self._user_command = command
        self._normal_fg = normal_fg
        self._hover_fg = hover_fg
        self._pressed_fg = pressed_fg
        self._disabled_fg = disabled_fg
        self._normal_text_color = normal_text_color
        self._disabled_text_color = disabled_text_color
        self._is_loading = False
        self._is_disabled = False
        self._spinner_idx = 0
        self._spinner_after_id: Optional[str] = None
        self._loading_label = text

        self._icon_img = (
            get_icon(icon_name, size=18, color_pair=icon_color)
            if icon_name
            else None
        )

        # الأيقونة قبل النص: في العربية (RTL) اليمين هو قبل النص، وفي الإنجليزية اليسار
        compound = "right" if i18n.is_rtl else "left"

        super().__init__(
            master,
            text=text,
            image=self._icon_img,
            compound=compound,
            command=self._handle_click,
            height=height,
            width=width,
            corner_radius=theme.RADIUS_BUTTON,
            fg_color=normal_fg,
            hover_color=hover_fg,
            text_color=normal_text_color,
            text_color_disabled=disabled_text_color,
            border_width=border_width,
            border_color=border_color,
            font=theme.get_body_font(i18n.lang, bold=bold),
            **kwargs,
        )

        self._tooltip_obj: Optional[Tooltip] = (
            Tooltip(self, tooltip) if tooltip else None
        )

        # تفاعل بصري خفيف لحالة الضغط دون الكتابة فوق دالة _on_release الخاصة بـ CTkButton
        self.bind("<ButtonPress-1>", self._handle_press_visual, add="+")

    def _handle_click(self) -> None:
        if self._is_loading or self._is_disabled:
            return
        if self._user_command:
            self._user_command()

    def _handle_press_visual(self, _event: object = None) -> None:
        """تلوين لحظي عند الضغط باستخدام عناصر اللوحة مباشرة دون تعطيل حدث النقر."""
        if self._is_loading or self._is_disabled:
            return
        try:
            pressed_col = self._apply_appearance_mode(self._pressed_fg)
            if pressed_col != "transparent":
                self._canvas.itemconfig("inner_parts", fill=pressed_col, outline=pressed_col)
                if self._text_label is not None:
                    self._text_label.configure(bg=pressed_col)
                if self._image_label is not None:
                    self._image_label.configure(bg=pressed_col)
        except Exception:
            pass

    def set_tooltip(self, text: str) -> None:
        if self._tooltip_obj:
            self._tooltip_obj.set_text(text)
        elif text:
            self._tooltip_obj = Tooltip(self, text)

    def set_disabled(self, disabled: bool) -> None:
        """تفعيل أو تعطيل الزر مع مظهر شفافية 40%."""
        self._is_disabled = disabled
        if disabled:
            self.configure(
                state="disabled",
                fg_color=self._disabled_fg,
                text_color=self._disabled_text_color,
            )
        else:
            self.configure(
                state="normal",
                fg_color=self._normal_fg,
                text_color=self._normal_text_color,
            )

    def set_loading(self, loading: bool, loading_text: Optional[str] = None) -> None:
        """تفعيل أو إيقاف حالة التحميل (Loading) مع مؤشر دوّار صغير."""
        self._is_loading = loading
        if loading:
            self._spinner_idx = 0
            self._loading_label = loading_text if loading_text is not None else self._original_text
            self.configure(image=None)
            self._animate_spinner()
        else:
            if self._spinner_after_id:
                try:
                    self.after_cancel(self._spinner_after_id)
                except Exception:
                    pass
                self._spinner_after_id = None
            compound = "right" if i18n.is_rtl else "left"
            self.configure(
                text=self._original_text,
                image=self._icon_img,
                compound=compound,
                fg_color=self._normal_fg,
            )

    def _animate_spinner(self) -> None:
        if not self._is_loading or not self.winfo_exists():
            return
        frame_char = SPINNER_FRAMES[self._spinner_idx % len(SPINNER_FRAMES)]
        self._spinner_idx += 1
        if self._loading_label:
            display = (
                f"{self._loading_label}  {frame_char}"
                if i18n.is_rtl
                else f"{frame_char}  {self._loading_label}"
            )
        else:
            display = frame_char
        self.configure(text=display)
        self._spinner_after_id = self.after(theme.SPINNER_INTERVAL_MS, self._animate_spinner)


class PrimaryButton(BaseAppButton):
    """1) زر Primary: خلفية ملوّنة (Primary) ونص أبيض، للإجراء الرئيسي."""

    def __init__(
        self,
        master: object,
        text: str = "",
        icon_name: Optional[str] = None,
        command: Optional[Callable[[], None]] = None,
        tooltip: str = "",
        height: int = theme.BUTTON_HEIGHT,
        width: int = 130,
        **kwargs: object,
    ) -> None:
        super().__init__(
            master,
            text=text,
            icon_name=icon_name,
            icon_color=(theme.COLOR_ON_PRIMARY, theme.COLOR_ON_PRIMARY),
            command=command,
            tooltip=tooltip,
            height=height,
            width=width,
            normal_fg=theme.PRIMARY_COLOR,
            hover_fg=theme.PRIMARY_HOVER,
            pressed_fg=theme.PRIMARY_PRESSED,
            disabled_fg=theme.PRIMARY_DISABLED,
            normal_text_color=theme.COLOR_ON_PRIMARY,
            disabled_text_color=theme.TEXT_SECONDARY,
            border_width=0,
            bold=True,
            **kwargs,
        )


class SecondaryButton(BaseAppButton):
    """2) زر Secondary: خلفية شفافة مع حدود رفيعة، للإجراءات الثانوية."""

    def __init__(
        self,
        master: object,
        text: str = "",
        icon_name: Optional[str] = None,
        command: Optional[Callable[[], None]] = None,
        tooltip: str = "",
        height: int = theme.BUTTON_HEIGHT,
        width: int = 110,
        **kwargs: object,
    ) -> None:
        super().__init__(
            master,
            text=text,
            icon_name=icon_name,
            icon_color=theme.TEXT_PRIMARY,
            command=command,
            tooltip=tooltip,
            height=height,
            width=width,
            normal_fg=theme.COLOR_TRANSPARENT,
            hover_fg=theme.GHOST_HOVER,
            pressed_fg=theme.BORDER_COLOR,
            disabled_fg=theme.COLOR_TRANSPARENT,
            normal_text_color=theme.TEXT_PRIMARY,
            disabled_text_color=theme.TEXT_MUTED,
            border_width=theme.BORDER_WIDTH_THIN,
            border_color=theme.BORDER_COLOR,
            bold=False,
            **kwargs,
        )


class GhostIconButton(BaseAppButton):
    """3) زر Ghost/Icon: أيقونة فقط بدون خلفية وتظهر خلفية خفيفة عند التحويم، مع Tooltip."""

    def __init__(
        self,
        master: object,
        icon_name: str,
        tooltip: str,
        command: Optional[Callable[[], None]] = None,
        icon_color: Optional[Tuple[str, str]] = None,
        size: int = theme.ICON_BUTTON_SIZE,
        **kwargs: object,
    ) -> None:
        super().__init__(
            master,
            text="",
            icon_name=icon_name,
            icon_color=icon_color or theme.TEXT_SECONDARY,
            command=command,
            tooltip=tooltip,
            height=size,
            width=size,
            normal_fg=theme.COLOR_TRANSPARENT,
            hover_fg=theme.GHOST_HOVER,
            pressed_fg=theme.BORDER_COLOR,
            disabled_fg=theme.COLOR_TRANSPARENT,
            normal_text_color=theme.TEXT_PRIMARY,
            disabled_text_color=theme.TEXT_MUTED,
            border_width=0,
            bold=False,
            **kwargs,
        )
