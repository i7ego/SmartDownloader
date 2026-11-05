"""
التلميحات المساعدة (Tooltips) والإشعارات المنبثقة (Toast Notifications).
تلتزم بالكامل بثوابت الألوان والخطوط والمسافات في ui/theme.py.
"""

import tkinter as tk
from typing import Optional
import customtkinter as ctk

from ui import theme
from ui.i18n import i18n
from ui.icons import get_icon


class Tooltip:
    """نص مساعد يظهر عند تحويم الماوس على أي زر أو أيقونة."""

    def __init__(self, widget: tk.Widget, text: str, delay_ms: int = 350) -> None:
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self._after_id: Optional[str] = None
        self._tip_window: Optional[tk.Toplevel] = None

        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        self.widget.bind("<ButtonPress>", self._on_leave, add="+")
        self.widget.bind("<Destroy>", self._on_destroy, add="+")

    def set_text(self, text: str) -> None:
        self.text = text

    def _on_enter(self, _event: Optional[tk.Event] = None) -> None:
        self._cancel_timer()
        if self.text:
            self._after_id = self.widget.after(self.delay_ms, self._show)

    def _on_leave(self, _event: Optional[tk.Event] = None) -> None:
        self._cancel_timer()
        self._hide()

    def _on_destroy(self, _event: Optional[tk.Event] = None) -> None:
        self._cancel_timer()
        self._hide()

    def _cancel_timer(self) -> None:
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self) -> None:
        if self._tip_window or not self.text:
            return
        try:
            if not self.widget.winfo_exists():
                return
            x = self.widget.winfo_rootx() + (self.widget.winfo_width() // 2)
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + theme.SPACE_SM

            self._tip_window = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_attributes("-topmost", True)

            bg_hex = theme.resolve_color(theme.BG_ELEVATED)
            tw.configure(bg=bg_hex)

            frame = ctk.CTkFrame(
                tw,
                fg_color=theme.BG_ELEVATED,
                border_color=theme.BORDER_COLOR,
                border_width=theme.BORDER_WIDTH_THIN,
                corner_radius=theme.RADIUS_CHIP,
            )
            frame.pack(fill="both", expand=True)

            label = ctk.CTkLabel(
                frame,
                text=self.text,
                font=theme.get_small_font(i18n.lang),
                text_color=theme.TEXT_PRIMARY,
                padx=theme.SPACE_MD,
                pady=theme.SPACE_XS,
            )
            label.pack()

            tw.update_idletasks()
            tip_w = tw.winfo_reqwidth()
            screen_w = tw.winfo_screenwidth()
            pos_x = max(theme.SPACE_SM, min(x - tip_w // 2, screen_w - tip_w - theme.SPACE_SM))
            tw.wm_geometry(f"+{pos_x}+{y}")
        except Exception:
            self._hide()

    def _hide(self) -> None:
        if self._tip_window is not None:
            try:
                self._tip_window.destroy()
            except Exception:
                pass
            self._tip_window = None


class ToastManager:
    """
    مدير الإشعارات المنبثقة (Toast) في زاوية النافذة.
    يعرض إشعارات (success / error / warning / info) تختفي تلقائياً بعد 3 ثوانٍ.
    """

    def __init__(self, root: ctk.CTk) -> None:
        self.root = root
        self._active_toasts: list[ctk.CTkFrame] = []

    def show(
        self,
        message: str,
        kind: str = "info",
        duration_ms: int = theme.TOAST_DURATION_MS,
    ) -> None:
        """عرض إشعار منبثق في الزاوية السفلية للنافذة."""
        if not self.root.winfo_exists():
            return

        if kind == "success":
            accent = theme.SUCCESS_COLOR
            bg_tint = theme.SUCCESS_TINT
            icon_name = "check"
        elif kind == "error":
            accent = theme.ERROR_COLOR
            bg_tint = theme.ERROR_TINT
            icon_name = "alert_circle"
        elif kind == "warning":
            accent = theme.WARNING_COLOR
            bg_tint = theme.WARNING_TINT
            icon_name = "alert_triangle"
        else:
            accent = theme.ACCENT_COLOR
            bg_tint = theme.ACCENT_TINT
            icon_name = "info"

        toast = ctk.CTkFrame(
            self.root,
            fg_color=bg_tint,
            border_color=accent,
            border_width=theme.BORDER_WIDTH_ACTIVE,
            corner_radius=theme.RADIUS_BUTTON,
        )

        inner = ctk.CTkFrame(toast, fg_color=theme.COLOR_TRANSPARENT)
        inner.pack(
            fill="both",
            expand=True,
            padx=theme.SPACE_LG,
            pady=theme.SPACE_MD,
        )

        icon_img = get_icon(icon_name, size=18, color_pair=accent)
        icon_lbl = ctk.CTkLabel(inner, text="", image=icon_img)
        icon_lbl.pack(side=i18n.side_start, padx=(0, theme.SPACE_SM) if not i18n.is_rtl else (theme.SPACE_SM, 0))

        msg_lbl = ctk.CTkLabel(
            inner,
            text=message,
            font=theme.get_body_font(i18n.lang, bold=True),
            text_color=theme.TEXT_PRIMARY,
            justify=i18n.justify,
        )
        msg_lbl.pack(side=i18n.side_start)

        self._active_toasts.append(toast)
        self._reposition_toasts()

        def _dismiss() -> None:
            if toast in self._active_toasts:
                self._active_toasts.remove(toast)
            try:
                toast.destroy()
            except Exception:
                pass
            self._reposition_toasts()

        toast.after(duration_ms, _dismiss)

    def _reposition_toasts(self) -> None:
        """ترتيب الإشعارات النشطة في الزاوية السفلية المناسبة لاتجاه اللغة."""
        bottom_offset = theme.SPACE_XXL
        for toast in reversed(self._active_toasts):
            if not toast.winfo_exists():
                continue
            if i18n.is_rtl:
                # في الوضع العربي توضع في الزاوية السفلية اليسرى لكي لا تغطي الشريط الجانبي الأيمن
                toast.place(
                    relx=0.0,
                    rely=1.0,
                    x=theme.SPACE_XXL,
                    y=-bottom_offset,
                    anchor="sw",
                )
            else:
                toast.place(
                    relx=1.0,
                    rely=1.0,
                    x=-theme.SPACE_XXL,
                    y=-bottom_offset,
                    anchor="se",
                )
            toast.lift()
            bottom_offset += 58
