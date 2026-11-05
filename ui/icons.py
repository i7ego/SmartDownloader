"""
مولّد ومدير الأيقونات الحديثة بنمط Lucide / Phosphor (بدقة عالية وسماكة خط موحدة).
تتلوّن الأيقونات تلقائياً حسب الثيم (Dark / Light) باستخدام CTkImage.
"""

import math
from typing import Dict, Tuple, Optional
from PIL import Image, ImageDraw
import customtkinter as ctk

from ui import theme

# ذاكرة تخزين مؤقت للأيقونات لمنع إعادة الرسم
_ICON_CACHE: Dict[Tuple[str, int, str, str], ctk.CTkImage] = {}


def _draw_lucide_icon(name: str, size: int, color: str) -> Image.Image:
    """
    رسم أيقونة خطية بنمط Lucide بدقة مضاعفة 4x (Supersampling) لضمان نعومة الحواف
    وسماكة خط موحدة.
    """
    scale = 4
    canvas_size = size * scale
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # سماكة خط موحدة (2px على مقياس 24px)
    stroke = max(2, int(round((size / 24.0) * 2.0 * scale)))

    def p(x: float, y: float) -> Tuple[float, float]:
        """تحويل إحداثيات من شبكة 24×24 القياسية في Lucide إلى حجم اللوحة الفعلي."""
        return (x / 24.0 * canvas_size, y / 24.0 * canvas_size)

    def line(pts, width: int = stroke):
        coords = [p(x, y) for x, y in pts]
        draw.line(coords, fill=color, width=width, joint="curve")
        # رسم نهايات دائرية (Round Caps) لنمط Lucide
        r = width / 2.0
        for cx, cy in coords:
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)

    def rect_round(x1: float, y1: float, x2: float, y2: float, rad: float = 3.0):
        c1 = p(x1, y1)
        c2 = p(x2, y2)
        draw.rounded_rectangle(
            (c1[0], c1[1], c2[0], c2[1]),
            radius=rad / 24.0 * canvas_size,
            outline=color,
            width=stroke,
        )

    def circle(cx: float, cy: float, r: float):
        x1, y1 = p(cx - r, cy - r)
        x2, y2 = p(cx + r, cy + r)
        draw.ellipse((x1, y1, x2, y2), outline=color, width=stroke)

    if name == "download":
        line([(12, 3), (12, 15)])
        line([(7, 10), (12, 15), (17, 10)])
        line([(4, 17), (4, 19), (20, 19), (20, 17)])

    elif name == "activity":
        line([(22, 12), (18, 12), (15, 20), (9, 4), (6, 12), (2, 12)])

    elif name == "history":
        x1, y1 = p(3, 3)
        x2, y2 = p(21, 21)
        draw.arc((x1, y1, x2, y2), start=210, end=510, fill=color, width=stroke)
        line([(3, 4), (3, 9), (8, 9)])
        line([(12, 7), (12, 12), (15.5, 14)])

    elif name == "settings":
        circle(12, 12, 3.2)
        for angle_deg in range(0, 360, 45):
            rad = math.radians(angle_deg)
            x1 = 12 + math.cos(rad) * 6.8
            y1 = 12 + math.sin(rad) * 6.8
            x2 = 12 + math.cos(rad) * 9.5
            y2 = 12 + math.sin(rad) * 9.5
            line([(x1, y1), (x2, y2)])

    elif name == "link":
        line([(9, 15), (15, 9)])
        line([(11, 6), (14, 4), (19, 4), (20, 9), (18, 13)])
        line([(13, 18), (10, 20), (5, 20), (4, 15), (6, 11)])

    elif name == "paste":
        rect_round(6, 5, 18, 21, rad=2.5)
        rect_round(9, 3, 15, 6.5, rad=1.5)
        line([(9, 11), (15, 11)])
        line([(9, 15), (13, 15)])

    elif name == "sparkles" or name == "analyze":
        line([(12, 3), (13.8, 9.2), (20, 11), (13.8, 12.8), (12, 19), (10.2, 12.8), (4, 11), (10.2, 9.2), (12, 3)])
        line([(19, 3), (19, 7)])
        line([(17, 5), (21, 5)])

    elif name == "search":
        circle(11, 11, 6.5)
        line([(16, 16), (20.5, 20.5)])

    elif name == "upload_cloud":
        line([(12, 13), (12, 21)])
        line([(9, 16), (12, 13), (15, 16)])
        line([(7, 18), (4.5, 16.5), (4.5, 12.5), (7.5, 10.5), (9, 6.5), (14.5, 6.5), (16.5, 10.5), (19.5, 12), (19.5, 16.5), (17, 18)])

    elif name == "video":
        rect_round(3, 6, 15, 18, rad=2.5)
        line([(15, 10), (21, 7), (21, 17), (15, 14)])

    elif name == "music":
        line([(9, 18), (9, 6), (20, 4), (20, 16)])
        circle(6.5, 18, 2.5)
        circle(17.5, 16, 2.5)

    elif name == "scissors" or name == "cut":
        circle(6, 6, 3)
        circle(6, 18, 3)
        line([(8.12, 7.88), (20, 19.76)])
        line([(14.8, 14.8), (20, 4.24)])
        line([(8.12, 16.12), (12, 12)])

    elif name == "folder":
        line([(3, 7), (3, 19), (21, 19), (21, 9), (12, 9), (9.5, 6), (3, 6), (3, 7)])

    elif name == "play":
        line([(7, 5), (19, 12), (7, 19), (7, 5)])

    elif name == "pause":
        rect_round(6, 5, 10, 19, rad=1.5)
        rect_round(14, 5, 18, 19, rad=1.5)

    elif name == "x":
        line([(6, 6), (18, 18)])
        line([(18, 6), (6, 18)])

    elif name == "trash":
        line([(4, 7), (20, 7)])
        line([(9, 7), (9, 4), (15, 4), (15, 7)])
        line([(6, 7), (7, 20), (17, 20), (18, 7)])
        line([(10, 11), (10, 16)])
        line([(14, 11), (14, 16)])

    elif name == "sun":
        circle(12, 12, 4)
        for angle_deg in range(0, 360, 45):
            rad = math.radians(angle_deg)
            x1 = 12 + math.cos(rad) * 6.5
            y1 = 12 + math.sin(rad) * 6.5
            x2 = 12 + math.cos(rad) * 9.0
            y2 = 12 + math.sin(rad) * 9.0
            line([(x1, y1), (x2, y2)])

    elif name == "moon":
        x1, y1 = p(4, 4)
        x2, y2 = p(20, 20)
        draw.arc((x1, y1, x2, y2), start=45, end=245, fill=color, width=stroke)
        line([(12, 4), (10, 9), (14, 14), (19, 13)])

    elif name == "globe":
        circle(12, 12, 8.5)
        line([(3.5, 12), (20.5, 12)])
        line([(12, 3.5), (9, 12), (12, 20.5)])
        line([(12, 3.5), (15, 12), (12, 20.5)])

    elif name == "chevron_down":
        line([(6, 9), (12, 15), (18, 9)])

    elif name == "chevron_up":
        line([(6, 15), (12, 9), (18, 15)])

    elif name == "check":
        line([(5, 12.5), (10, 17.5), (19.5, 7)])

    elif name == "alert_triangle":
        line([(12, 4), (21, 19), (3, 19), (12, 4)])
        line([(12, 10), (12, 14)])
        circle(12, 16.8, 0.5)

    elif name == "alert_circle":
        circle(12, 12, 8.5)
        line([(12, 8), (12, 12.5)])
        circle(12, 16, 0.5)

    elif name == "info":
        circle(12, 12, 8.5)
        line([(12, 11.5), (12, 16.5)])
        circle(12, 8, 0.5)

    elif name == "list_video":
        line([(3, 7), (12, 7)])
        line([(3, 12), (12, 12)])
        line([(3, 17), (9, 17)])
        line([(15, 10), (21, 14), (15, 18), (15, 10)])

    elif name == "refresh":
        x1, y1 = p(4, 4)
        x2, y2 = p(20, 20)
        draw.arc((x1, y1, x2, y2), start=30, end=310, fill=color, width=stroke)
        line([(16, 4), (20, 5), (19, 9)])

    elif name == "inbox":
        rect_round(3, 5, 21, 19, rad=2.5)
        line([(3, 13), (8, 13), (10, 16), (14, 16), (16, 13), (21, 13)])

    elif name == "spinner":
        x1, y1 = p(4, 4)
        x2, y2 = p(20, 20)
        draw.arc((x1, y1, x2, y2), start=0, end=270, fill=color, width=stroke)

    else:
        circle(12, 12, 7)

    return img.resize((size, size), Image.Resampling.LANCZOS)


def get_icon(
    name: str,
    size: int = 20,
    color_pair: Optional[Tuple[str, str]] = None,
) -> ctk.CTkImage:
    """
    الحصول على أيقونة CTkImage تتلوّن تلقائياً حسب الوضع الفاتح أو الداكن.
    إذا لم يُمرّر color_pair، يُستخدم لون النص الأساسي من ui/theme.py.
    """
    if color_pair is None:
        color_pair = theme.TEXT_PRIMARY

    light_color, dark_color = color_pair
    cache_key = (name, size, light_color, dark_color)
    if cache_key in _ICON_CACHE:
        return _ICON_CACHE[cache_key]

    light_img = _draw_lucide_icon(name, size, light_color)
    dark_img = (
        light_img
        if light_color == dark_color
        else _draw_lucide_icon(name, size, dark_color)
    )

    ctk_icon = ctk.CTkImage(
        light_image=light_img,
        dark_image=dark_img,
        size=(size, size),
    )
    _ICON_CACHE[cache_key] = ctk_icon
    return ctk_icon


def create_app_logo_pil(size: int = 64) -> Image.Image:
    """إنشاء شعار البرنامج كصورة PIL عالية الدقة لاستخدامها في النافذة و System Tray."""
    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # خلفية مستديرة بلون Primary
    draw.rounded_rectangle(
        (0, 0, s - 1, s - 1),
        radius=int(s * 0.26),
        fill=theme.COLOR_PRIMARY,
    )
    # شريط تركواز Accent أسفل الأيقونة
    pad = int(s * 0.24)
    stroke = max(4, int(s * 0.09))
    draw.line(
        [(pad, int(s * 0.72)), (s - pad, int(s * 0.72))],
        fill=theme.COLOR_ACCENT,
        width=stroke,
    )
    # سهم التحميل بالأبيض
    cx = s // 2
    draw.line(
        [(cx, int(s * 0.24)), (cx, int(s * 0.56))],
        fill=theme.COLOR_ON_PRIMARY,
        width=stroke,
    )
    draw.line(
        [
            (int(s * 0.34), int(s * 0.44)),
            (cx, int(s * 0.58)),
            (int(s * 0.66), int(s * 0.44)),
        ],
        fill=theme.COLOR_ON_PRIMARY,
        width=stroke,
    )
    return img.resize((size, size), Image.Resampling.LANCZOS)
