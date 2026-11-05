"""
ملف الثيم المركزي (ui/theme.py)
يحتوي على جميع ثوابت الألوان، الخطوط، الأحجام، المسافات، والزوايا المستديرة.
لا يُكتب أي لون أو حجم خط أو مسافة مباشرة داخل الكود خارج هذا الملف.
"""

import os
import sys
import ctypes
from pathlib import Path
from typing import Tuple, Optional
import customtkinter as ctk

# ==============================================================================
# 1. لوحة الألوان (Color Palette) - الوضع الداكن (الافتراضي) والوضع الفاتح
# ==============================================================================

# --- ألوان الوضع الداكن (Dark Mode - Default) ---
DARK_BG_MAIN = "#0F1117"
DARK_BG_SIDEBAR = "#161923"
DARK_BG_CARD = "#1C2030"
DARK_BG_CARD_HOVER = "#23283B"
DARK_BG_INPUT = "#141722"
DARK_BG_ELEVATED = "#24293D"
DARK_BORDER = "#2A2F45"
DARK_TEXT_PRIMARY = "#F5F6FA"
DARK_TEXT_SECONDARY = "#9AA0B5"
DARK_TEXT_MUTED = "#656B82"

# --- ألوان الوضع الفاتح (Light Mode) ---
LIGHT_BG_MAIN = "#F5F7FB"
LIGHT_BG_SIDEBAR = "#FFFFFF"
LIGHT_BG_CARD = "#FFFFFF"
LIGHT_BG_CARD_HOVER = "#F0F3F9"
LIGHT_BG_INPUT = "#F8FAFC"
LIGHT_BG_ELEVATED = "#EEF1F8"
LIGHT_BORDER = "#E3E7F0"
LIGHT_TEXT_PRIMARY = "#1E2233"
LIGHT_TEXT_SECONDARY = "#646B82"
LIGHT_TEXT_MUTED = "#9AA0B5"

# --- الألوان البارزة المشتركة (Primary & Accent - أقصى حد لونان بارزان) ---
COLOR_PRIMARY = "#6C5CE7"           # بنفسجي أساسي
COLOR_PRIMARY_HOVER = "#5A4BD1"     # بنفسجي عند التحويم
COLOR_PRIMARY_PRESSED = "#4839B5"   # بنفسجي عند الضغط
COLOR_PRIMARY_DISABLED_DARK = "#3A346E"
COLOR_PRIMARY_DISABLED_LIGHT = "#B6AEF3"

# خلفية التبويب النشط (Primary خفيف يتناسب مع الثيم)
DARK_PRIMARY_TINT = "#211F3D"
LIGHT_PRIMARY_TINT = "#EFErFD".replace("r", "E")  # #EFEEFD

COLOR_ACCENT = "#00CEC9"            # تركواز للتقدم والعناصر النشطة
COLOR_ACCENT_HOVER = "#00B5B0"
DARK_ACCENT_TINT = "#122E35"
LIGHT_ACCENT_TINT = "#E5FBFB"

# --- ألوان الحالات (Status Colors - للحالات فقط) ---
COLOR_SUCCESS = "#2ECC71"           # أخضر للنجاح/مكتمل
DARK_SUCCESS_TINT = "#163128"
LIGHT_SUCCESS_TINT = "#E8F9F0"

COLOR_WARNING = "#F39C12"           # برتقالي للتحذير/متوقف
DARK_WARNING_TINT = "#332919"
LIGHT_WARNING_TINT = "#FEF5E7"

COLOR_ERROR = "#E74C3C"             # أحمر للخطأ/فشل
COLOR_ERROR_HOVER = "#C0392B"
DARK_ERROR_TINT = "#321D22"
LIGHT_ERROR_TINT = "#FDEDEC"

# ألوان ثابتة للنصوص فوق الأزرار الملونة
COLOR_ON_PRIMARY = "#FFFFFF"
COLOR_TRANSPARENT = "transparent"

# ==============================================================================
# 2. ثنائيات الألوان المتوافقة مع CustomTkinter: (Light, Dark)
# ==============================================================================

BG_MAIN: Tuple[str, str] = (LIGHT_BG_MAIN, DARK_BG_MAIN)
BG_SIDEBAR: Tuple[str, str] = (LIGHT_BG_SIDEBAR, DARK_BG_SIDEBAR)
BG_CARD: Tuple[str, str] = (LIGHT_BG_CARD, DARK_BG_CARD)
BG_CARD_HOVER: Tuple[str, str] = (LIGHT_BG_CARD_HOVER, DARK_BG_CARD_HOVER)
BG_INPUT: Tuple[str, str] = (LIGHT_BG_INPUT, DARK_BG_INPUT)
BG_ELEVATED: Tuple[str, str] = (LIGHT_BG_ELEVATED, DARK_BG_ELEVATED)

BORDER_COLOR: Tuple[str, str] = (LIGHT_BORDER, DARK_BORDER)

TEXT_PRIMARY: Tuple[str, str] = (LIGHT_TEXT_PRIMARY, DARK_TEXT_PRIMARY)
TEXT_SECONDARY: Tuple[str, str] = (LIGHT_TEXT_SECONDARY, DARK_TEXT_SECONDARY)
TEXT_MUTED: Tuple[str, str] = (LIGHT_TEXT_MUTED, DARK_TEXT_MUTED)

PRIMARY_COLOR: Tuple[str, str] = (COLOR_PRIMARY, COLOR_PRIMARY)
PRIMARY_HOVER: Tuple[str, str] = (COLOR_PRIMARY_HOVER, COLOR_PRIMARY_HOVER)
PRIMARY_PRESSED: Tuple[str, str] = (COLOR_PRIMARY_PRESSED, COLOR_PRIMARY_PRESSED)
PRIMARY_DISABLED: Tuple[str, str] = (COLOR_PRIMARY_DISABLED_LIGHT, COLOR_PRIMARY_DISABLED_DARK)
PRIMARY_TINT: Tuple[str, str] = (LIGHT_PRIMARY_TINT, DARK_PRIMARY_TINT)

ACCENT_COLOR: Tuple[str, str] = (COLOR_ACCENT, COLOR_ACCENT)
ACCENT_HOVER: Tuple[str, str] = (COLOR_ACCENT_HOVER, COLOR_ACCENT_HOVER)
ACCENT_TINT: Tuple[str, str] = (LIGHT_ACCENT_TINT, DARK_ACCENT_TINT)

SUCCESS_COLOR: Tuple[str, str] = (COLOR_SUCCESS, COLOR_SUCCESS)
SUCCESS_TINT: Tuple[str, str] = (LIGHT_SUCCESS_TINT, DARK_SUCCESS_TINT)

WARNING_COLOR: Tuple[str, str] = (COLOR_WARNING, COLOR_WARNING)
WARNING_TINT: Tuple[str, str] = (LIGHT_WARNING_TINT, DARK_WARNING_TINT)

ERROR_COLOR: Tuple[str, str] = (COLOR_ERROR, COLOR_ERROR)
ERROR_HOVER: Tuple[str, str] = (COLOR_ERROR_HOVER, COLOR_ERROR_HOVER)
ERROR_TINT: Tuple[str, str] = (LIGHT_ERROR_TINT, DARK_ERROR_TINT)

GHOST_HOVER: Tuple[str, str] = (LIGHT_BG_ELEVATED, DARK_BG_ELEVATED)

# ==============================================================================
# 3. الخطوط والأحجام الثابتة (Typography)
# ==============================================================================

FONT_FAMILY_AR_PRIMARY = "Cairo"
FONT_FAMILY_AR_FALLBACK = "Tajawal"
FONT_FAMILY_EN_PRIMARY = "Segoe UI Variable"
FONT_FAMILY_EN_FALLBACK = "Inter"

# الأحجام الثابتة المعتمدة في المواصفات
FONT_SIZE_TITLE_LARGE = 24     # العنوان الكبير: 24
FONT_SIZE_SECTION_TITLE = 18   # عنوان القسم: 18
FONT_SIZE_BODY = 14            # النص العادي: 14
FONT_SIZE_SMALL = 12           # النص الصغير: 12

FONT_WEIGHT_BOLD = "bold"
FONT_WEIGHT_NORMAL = "normal"

# ==============================================================================
# 4. المسافات، الأبعاد، والزوايا المستديرة (Layout & Spacing & Radii)
# ==============================================================================

# أبعاد النافذة
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 650
WINDOW_DEFAULT_WIDTH = 1120
WINDOW_DEFAULT_HEIGHT = 720

# الشريط الجانبي
SIDEBAR_WIDTH = 220
SIDEBAR_INDICATOR_WIDTH = 4

# الزوايا المستديرة (بين 10 و 16 لكل العناصر)
RADIUS_CHIP = 10               # شرائح الجودة والصيغة والشارات
RADIUS_BUTTON = 12             # الأزرار (حتى 12px)
RADIUS_INPUT = 12              # حقول الإدخال
RADIUS_CARD = 16               # البطاقات الرئيسية
RADIUS_THUMBNAIL = 12          # الصورة المصغرة

# ارتفاعات الأزرار والحقول
BUTTON_HEIGHT = 42             # ارتفاع ثابت للأزرار بين 40 و 44px
BUTTON_SMALL_HEIGHT = 36
ICON_BUTTON_SIZE = 40          # أزرار الأيقونات (Ghost/Icon)
INPUT_HEIGHT = 46              # ارتفاع حقل الرابط الرئيسي
PROGRESS_BAR_HEIGHT = 8        # شريط تقدم نحيف بزوايا مستديرة

# المسافات (Spacing)
SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 12
SPACE_LG = 16                  # المسافة بين البطاقات (16-24px)
SPACE_XL = 20
SPACE_XXL = 24                 # الهوامش الخارجية لمنطقة المحتوى

# الحدود
BORDER_WIDTH_THIN = 1
BORDER_WIDTH_ACTIVE = 2

# أوقات التفاعل والحركة (بالملي ثانية)
TOAST_DURATION_MS = 3000       # 3 ثوانٍ للإشعارات المنبثقة
FADE_STEP_MS = 18              # خطوة الانتقال السلس بين التبويبات
SPINNER_INTERVAL_MS = 90       # سرعة مؤشر التحميل الدوار

# إصدار التطبيق
APP_VERSION = "v1.0.0"
APP_NAME_AR = "محمّل الوسائط الذكي"
APP_NAME_EN = "Smart Media Downloader"


# ==============================================================================
# 5. مدير الخطوط والثيم (Theme & Font Helpers)
# ==============================================================================

def load_bundled_fonts(assets_dir: Optional[Path] = None) -> None:
    """تحميل الخطوط العربية المضمّنة (Cairo / Tajawal) في نظام ويندوز عند توفرها."""
    if assets_dir is None:
        if hasattr(sys, "_MEIPASS"):
            assets_dir = Path(sys._MEIPASS) / "assets" / "fonts"
        else:
            assets_dir = Path(__file__).resolve().parent.parent / "assets" / "fonts"
    if not assets_dir.exists():
        return

    if os.name == "nt":
        FR_PRIVATE = 0x10
        for font_file in assets_dir.glob("*.ttf"):
            try:
                ctypes.windll.gdi32.AddFontResourceExW(str(font_file), FR_PRIVATE, 0)
            except Exception:
                pass


def get_font_family(lang: str = "ar") -> str:
    """إرجاع اسم عائلة الخط المناسبة حسب اللغة الحالية."""
    if lang == "ar":
        return FONT_FAMILY_AR_PRIMARY
    return FONT_FAMILY_EN_PRIMARY


def get_font(
    size: int = FONT_SIZE_BODY,
    weight: str = FONT_WEIGHT_NORMAL,
    lang: str = "ar",
) -> ctk.CTkFont:
    """إنشاء كائن خط CustomTkinter بالمقاس والسمك المحددين في الثيم."""
    family = get_font_family(lang)
    return ctk.CTkFont(family=family, size=size, weight=weight)


def get_title_large_font(lang: str = "ar") -> ctk.CTkFont:
    """خط العنوان الكبير (24 Bold)."""
    return get_font(size=FONT_SIZE_TITLE_LARGE, weight=FONT_WEIGHT_BOLD, lang=lang)


def get_section_title_font(lang: str = "ar") -> ctk.CTkFont:
    """خط عنوان القسم (18 Bold)."""
    return get_font(size=FONT_SIZE_SECTION_TITLE, weight=FONT_WEIGHT_BOLD, lang=lang)


def get_body_font(lang: str = "ar", bold: bool = False) -> ctk.CTkFont:
    """خط النص العادي (14)."""
    weight = FONT_WEIGHT_BOLD if bold else FONT_WEIGHT_NORMAL
    return get_font(size=FONT_SIZE_BODY, weight=weight, lang=lang)


def get_small_font(lang: str = "ar", bold: bool = False) -> ctk.CTkFont:
    """خط النص الصغير (12)."""
    weight = FONT_WEIGHT_BOLD if bold else FONT_WEIGHT_NORMAL
    return get_font(size=FONT_SIZE_SMALL, weight=weight, lang=lang)


def resolve_color(color_tuple: Tuple[str, str], mode: Optional[str] = None) -> str:
    """استخراج اللون النصي المفرد (Hex) حسب الوضع الحالي (Light أو Dark)."""
    if mode is None:
        mode = ctk.get_appearance_mode()
    if str(mode).lower() == "light":
        return color_tuple[0]
    return color_tuple[1]


def init_theme(mode: str = "Dark") -> None:
    """تهيئة إعدادات المظهر الافتراضية لـ CustomTkinter."""
    ctk.set_appearance_mode(mode)
    load_bundled_fonts()
