"""
نظام الترجمة ودعم اللغتين العربية والإنجليزية واتجاه التخطيط (RTL / LTR).
"""

from typing import Dict

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "ar": {
        # اسم البرنامج والتبويبات
        "app_title": "محمّل الوسائط الذكي",
        "tab_new": "تحميل جديد",
        "tab_active": "التحميلات الجارية",
        "tab_cutter": "تقطيع الوسائط",
        "tab_converter": "تحويل الفيديو",
        "tab_history": "السجل",
        "tab_settings": "الإعدادات",

        # الشريط الجانبي السفلي
        "theme_dark": "الوضع الداكن",
        "theme_light": "الوضع الفاتح",
        "toggle_theme_tip": "تبديل الوضع الداكن / الفاتح",
        "lang_label": "English",
        "toggle_lang_tip": "تغيير لغة الواجهة (العربية / الإنجليزية)",

        # صفحة تحميل جديد
        "page_new_title": "تحميل جديد",
        "page_new_subtitle": "الصق الرابط، اختر الجودة، واضغط تحميل في 3 خطوات بسيطة",
        "url_placeholder": "ضع رابط الفيديو أو قائمة التشغيل هنا (Ctrl+V للصق والتحليل التلقائي)...",
        "btn_paste": "لصق",
        "btn_paste_tip": "لصق الرابط من الحافظة (Ctrl+V)",
        "btn_analyze": "تحليل",
        "btn_analyze_loading": "جارٍ التحليل...",
        "btn_analyze_tip": "تحليل الرابط واستخراج الجودات المتاحة",
        "btn_clear_tip": "مسح الرابط",
        "drag_drop_title": "اسحب الرابط هنا أو الصقه",
        "drag_drop_subtitle": "يدعم روابط يوتيوب، منصات التواصل، وقوائم التشغيل الكاملة",

        # بطاقة المعاينة
        "preview_channel": "القناة:",
        "preview_duration": "المدة:",
        "preview_playlist_badge": "قائمة تشغيل",
        "preview_choose_videos": "اختيار الفيديوهات",

        # نوع الوسائط والشرائح
        "media_type_label": "نوع التحميل",
        "mode_video": "فيديو",
        "mode_audio": "صوت فقط",
        "quality_label": "الجودة",
        "format_label": "الصيغة",
        "chip_best": "أفضل جودة",
        "chip_more": "المزيد ▾",

        # مكان الحفظ والخيارات المتقدمة
        "save_path_label": "مكان الحفظ",
        "btn_change_folder": "تغيير",
        "btn_change_folder_tip": "اختيار مجلد حفظ مختلف",
        "advanced_options": "خيارات متقدمة",
        "opt_subtitles": "تحميل الترجمة المصاحبة (إن وجدت)",
        "opt_embed_thumbnail": "تضمين الصورة المصغرة داخل الملف",
        "opt_speed_limit": "الحد الأقصى للسرعة (KB/s - 0 بلا حد):",
        "opt_custom_filename": "قالب اسم الملف:",
        "btn_start_download": "ابدأ التحميل",
        "btn_start_loading": "جارٍ بدء التحميل...",

        # صفحة التحميلات الجارية
        "page_active_title": "التحميلات الجارية",
        "page_active_subtitle": "متابعة تقدم التحميلات الحالية والتحكم بها",
        "btn_pause_all": "إيقاف الكل مؤقتاً",
        "btn_resume_all": "استئناف الكل",
        "btn_clear_completed": "مسح المكتمل",
        "empty_active_title": "لا توجد تحميلات جارية حالياً",
        "empty_active_subtitle": "ابدأ بلصق رابط في تبويب «تحميل جديد» وستظهر تحمبلاتك هنا مباشرةً.",
        "status_downloading": "قيد التحميل",
        "status_completed": "مكتمل",
        "status_paused": "متوقف",
        "status_failed": "فشل",
        "status_queued": "في الانتظار",
        "speed_label": "السرعة:",
        "eta_label": "المتبقي:",
        "tip_pause": "إيقاف مؤقت",
        "tip_resume": "استئناف التحميل",
        "tip_cancel": "إلغاء التحميل",
        "tip_open_folder": "فتح المجلد",
        "tip_retry": "إعادة المحاولة",
        "tip_cut_audio": "قص وتعديل هذا المقطع",
        "tip_convert_media": "تحويل وتغيير صيغة هذا الملف",

        # صفحة تقطيع الصوت والفيديو
        "page_cutter_title": "تقطيع الوسائط (فيديو وصوت)",
        "page_cutter_subtitle": "حدد أي ملف فيديو أو صوت لقص جزء معين منه وحفظه بأعلى جودة وسرعة فائقة",
        "cutter_select_file": "اختيار ملف فيديو أو صوت",
        "cutter_drop_hint": "اسحب ملف الفيديو أو الصوت هنا أو اضغط لاختياره من جهازك",
        "cutter_drop_supported": "يدعم MP4, MKV, WebM, AVI, MOV, MP3, WAV, FLAC, M4A وغيرها",
        "cutter_file_label": "الملف الحالي:",
        "cutter_duration_label": "إجمالي المدة:",
        "cutter_mode_label": "نمط معالجة القص",
        "cutter_mode_fast": "سريع بدون فقد جودة (Lossless)",
        "cutter_mode_accurate": "دقيق مع إعادة ترميز",
        "cutter_range_section": "تحديد وقت البداية والنهاية",
        "cutter_player_section": "المشغل التفاعلي وشريط التمرير (Seek Bar)",
        "cutter_set_start": "تعيين كبداية [",
        "cutter_set_end": "تعيين كنهاية ]",
        "cutter_btn_play": "تشغيل",
        "cutter_btn_pause": "إيقاف مؤقت",
        "cutter_btn_stop": "إيقاف",
        "cutter_start_label": "وقت البداية:",
        "cutter_end_label": "وقت النهاية:",
        "cutter_segment_len": "مدة المقطع المقتطع:",
        "cutter_btn_preview": "معاينة المقطع",
        "cutter_btn_stop_preview": "إيقاف المعاينة",
        "cutter_fade_section": "تأثيرات التلاشي الصوتي (للصوتيات)",
        "cutter_fade_in": "تلاشي في البداية (Fade In ثوانٍ):",
        "cutter_fade_out": "تلاشي في النهاية (Fade Out ثوانٍ):",
        "cutter_export_format": "صيغة التصدير",
        "cutter_export_quality": "الجودة / الدقة",
        "cutter_btn_cut": "قص وحفظ الملف",
        "cutter_btn_cutting": "جارٍ قص ومعالجة الملف...",
        "toast_cutter_no_file": "يرجى اختيار ملف فيديو أو صوت أولاً",
        "toast_cutter_invalid_range": "وقت البداية يجب أن يكون أقل من وقت النهاية",
        "toast_cutter_success": "تم قص وحفظ الملف بنجاح في مجلد التحميلات",
        "toast_cutter_error": "حدث خطأ أثناء قص الملف، تحقق من صلاحية الملف المدخل",

        # صفحة تحويل الفيديوهات
        "page_converter_title": "تحويل الفيديوهات والوسائط",
        "page_converter_subtitle": "تحويل وتغيير دقة وضغط الفيديوهات لأي صيغة بسرعة وسهولة وبأعلى جودة",
        "conv_select_file": "اختيار فيديو للتحويل",
        "conv_drop_hint": "اسحب ملف الفيديو هنا أو اضغط لاختياره من جهازك",
        "conv_target_format": "الصيغة المستهدفة",
        "conv_resolution": "الدقة المستهدفة (Resolution)",
        "conv_compression": "نمط الجودة والضغط",
        "conv_res_original": "نفس الدقة",
        "conv_res_1080": "1080p (FHD)",
        "conv_res_720": "720p (HD)",
        "conv_res_480": "480p (SD)",
        "conv_preset_high": "أعلى جودة",
        "conv_preset_balanced": "متوازن",
        "conv_preset_small": "مضغوط (حجم صغير)",
        "conv_btn_start": "بدء تحويل الفيديو",
        "conv_btn_converting": "جارٍ تحويل ومعالجة الفيديو...",
        "conv_btn_cancel": "إلغاء التحويل",
        "conv_progress_label": "نسبة التقدم:",
        "toast_conv_no_file": "يرجى اختيار ملف فيديو أولاً للتحويل",
        "toast_conv_success": "تم تحويل وحفظ الفيديو بنجاح في مجلد التحميلات",
        "toast_conv_error": "حدث خطأ أثناء تحويل الفيديو، يرجى التحقق من الملف المدخل",

        # صفحة السجل
        "page_history_title": "سجل التحميلات",
        "page_history_subtitle": "جميع الملفات التي تم تحميلها سابقاً",
        "search_history_placeholder": "ابحث في السجل بالعنوان أو القناة...",
        "btn_clear_history": "مسح السجل",
        "empty_history_title": "سجل التحميلات فارغ",
        "empty_history_subtitle": "ستظهر هنا جميع الفيديوهات والملفات الصوتية بعد اكتمال تحميلها.",
        "tip_delete_record": "حذف من السجل",

        # صفحة الإعدادات
        "page_settings_title": "الإعدادات",
        "page_settings_subtitle": "تخصيص المظهر واللغة وخيارات التحميل الافتراضية",
        "settings_appearance_section": "المظهر واللغة",
        "settings_theme_label": "وضع المظهر",
        "settings_lang_label": "لغة الواجهة",
        "settings_defaults_section": "الإعدادات الافتراضية للتحميل",
        "settings_default_path": "مجلد الحفظ الافتراضي",
        "settings_default_quality": "الجودة الافتراضية",
        "settings_default_format": "الصيغة الافتراضية",
        "settings_concurrent": "عدد التحميلات المتزامنة",
        "settings_auto_analyze": "تحليل الرابط تلقائياً عند اللصق (Ctrl+V)",
        "settings_minimize_tray": "تصغير البرنامج إلى شريط النظام (System Tray) عند الإغلاق",
        "settings_about_section": "معلومات البرنامج والمطور",
        "dev_copyright": "Copyright © by Ahmed Hagag",
        "dev_contact": "ahmed.m.hagag22@gmail.com",
        "dev_contact_label": "للتواصل والدعم الفني:",
        "btn_copy_email": "نسخ البريد",
        "toast_email_copied": "تم نسخ البريد الإلكتروني إلى الحافظة",
        "btn_save_settings": "حفظ الإعدادات",
        "btn_show_welcome": "عرض شاشة الترحيب",

        # نافذة قوائم التشغيل
        "playlist_dialog_title": "اختيار فيديوهات قائمة التشغيل",
        "playlist_search_placeholder": "ابحث عن فيديو داخل القائمة...",
        "playlist_select_all": "تحديد الكل",
        "playlist_invert": "عكس التحديد",
        "playlist_selected_count": "المحدد: {selected} من {total}",
        "playlist_confirm": "تأكيد الاختيار",
        "playlist_cancel": "إلغاء",

        # شاشة الترحيب
        "welcome_title": "مرحباً بك في محمّل الوسائط الذكي",
        "welcome_subtitle": "صُمم ليتيح لك تحميل الفيديوهات والصوتيات بأعلى جودة وفي 3 خطوات فقط:",
        "welcome_step1_title": "1. الصق الرابط",
        "welcome_step1_desc": "انسخ رابط الفيديو أو قائمة التشغيل واضغط Ctrl+V ليتم تحليله تلقائياً.",
        "welcome_step2_title": "2. اختر الجودة والصيغة",
        "welcome_step2_desc": "حدد (فيديو أو صوت) واختر شريحة الجودة المناسبة مثل 1080p أو 4K أو MP3.",
        "welcome_step3_title": "3. اضغط ابدأ التحميل",
        "welcome_step3_desc": "تابع السرعة والوقت المتبقي لحظة بلحظة في تبويب التحميلات الجارية.",
        "welcome_start_btn": "ابدأ الاستخدام الآن",

        # الإشعارات المنبثقة (Toasts)
        "toast_pasted": "تم لصق الرابط من الحافظة",
        "toast_empty_clipboard": "الحافظة فارغة أو لا تحتوي على نص",
        "toast_invalid_url": "يرجى إدخال رابط صحيح أولاً",
        "toast_analyze_success": "تم تحليل الرابط بنجاح",
        "toast_analyze_error": "تعذّر تحليل الرابط، تحقق من الاتصال أو صحة الرابط",
        "toast_download_started": "بدأ التحميل وأُضيف إلى التحميلات الجارية",
        "toast_download_completed": "اكتمل التحميل بنجاح: {title}",
        "toast_download_failed": "فشل التحميل: {title}",
        "toast_settings_saved": "تم حفظ الإعدادات بنجاح",
        "toast_history_cleared": "تم مسح سجل التحميلات",
        "toast_folder_missing": "المجلد غير موجود على الجهاز",

        # قائمة System Tray
        "tray_open": "فتح البرنامج",
        "tray_pause_all": "إيقاف الكل",
        "tray_exit": "خروج",
    },
    "en": {
        "app_title": "Smart Media Downloader",
        "tab_new": "New Download",
        "tab_active": "Active Downloads",
        "tab_cutter": "Media Cutter",
        "tab_converter": "Video Converter",
        "tab_history": "History",
        "tab_settings": "Settings",

        "theme_dark": "Dark Mode",
        "theme_light": "Light Mode",
        "toggle_theme_tip": "Switch Dark / Light Mode",
        "lang_label": "العربية",
        "toggle_lang_tip": "Switch interface language (Arabic / English)",

        "page_new_title": "New Download",
        "page_new_subtitle": "Paste link, pick quality, and hit download in 3 easy steps",
        "url_placeholder": "Paste video or playlist URL here (Ctrl+V to auto-paste & analyze)...",
        "btn_paste": "Paste",
        "btn_paste_tip": "Paste URL from clipboard (Ctrl+V)",
        "btn_analyze": "Analyze",
        "btn_analyze_loading": "Analyzing...",
        "btn_analyze_tip": "Analyze URL and fetch available formats",
        "btn_clear_tip": "Clear URL",
        "drag_drop_title": "Drag & drop link here or paste it",
        "drag_drop_subtitle": "Supports YouTube, social media videos, and full playlists",

        "preview_channel": "Channel:",
        "preview_duration": "Duration:",
        "preview_playlist_badge": "Playlist",
        "preview_choose_videos": "Select Videos",

        "media_type_label": "Download Type",
        "mode_video": "Video",
        "mode_audio": "Audio Only",
        "quality_label": "Quality",
        "format_label": "Format",
        "chip_best": "Best",
        "chip_more": "More ▾",

        "save_path_label": "Save Location",
        "btn_change_folder": "Change",
        "btn_change_folder_tip": "Choose a different download folder",
        "advanced_options": "Advanced Options",
        "opt_subtitles": "Download subtitles (if available)",
        "opt_embed_thumbnail": "Embed thumbnail in media file",
        "opt_speed_limit": "Speed limit (KB/s - 0 for unlimited):",
        "opt_custom_filename": "Filename template:",
        "btn_start_download": "Start Download",
        "btn_start_loading": "Starting...",

        "page_active_title": "Active Downloads",
        "page_active_subtitle": "Monitor progress and control current downloads",
        "btn_pause_all": "Pause All",
        "btn_resume_all": "Resume All",
        "btn_clear_completed": "Clear Completed",
        "empty_active_title": "No active downloads right now",
        "empty_active_subtitle": "Paste a link in 'New Download' and your transfers will appear here.",
        "status_downloading": "Downloading",
        "status_completed": "Completed",
        "status_paused": "Paused",
        "status_failed": "Failed",
        "status_queued": "Queued",
        "speed_label": "Speed:",
        "eta_label": "ETA:",
        "tip_pause": "Pause",
        "tip_resume": "Resume",
        "tip_cancel": "Cancel",
        "tip_open_folder": "Open Folder",
        "tip_retry": "Retry",
        "tip_cut_audio": "Cut and edit this audio",
        "tip_convert_media": "Convert and resize this media",

        "page_cutter_title": "Media Cutter (Video & Audio)",
        "page_cutter_subtitle": "Select any video or audio file to trim and export with high precision and speed",
        "cutter_select_file": "Choose Video or Audio File",
        "cutter_drop_hint": "Drag & drop video or audio file here or click to browse",
        "cutter_drop_supported": "Supports MP4, MKV, WebM, AVI, MOV, MP3, WAV, FLAC, M4A and more",
        "cutter_file_label": "Selected File:",
        "cutter_duration_label": "Total Duration:",
        "cutter_mode_label": "Cut Processing Mode",
        "cutter_mode_fast": "Fast Lossless Cut (No re-encode)",
        "cutter_mode_accurate": "Accurate (Re-encode)",
        "cutter_range_section": "Set Start and End Time",
        "cutter_player_section": "Interactive Player & Seek Bar",
        "cutter_set_start": "Set Start [",
        "cutter_set_end": "Set End ]",
        "cutter_btn_play": "Play",
        "cutter_btn_pause": "Pause",
        "cutter_btn_stop": "Stop",
        "cutter_start_label": "Start Time:",
        "cutter_end_label": "End Time:",
        "cutter_segment_len": "Segment Duration:",
        "cutter_btn_preview": "Preview Segment",
        "cutter_btn_stop_preview": "Stop Preview",
        "cutter_fade_section": "Audio Fade Effects (Audio files)",
        "cutter_fade_in": "Fade In (seconds):",
        "cutter_fade_out": "Fade Out (seconds):",
        "cutter_export_format": "Export Format",
        "cutter_export_quality": "Quality / Resolution",
        "cutter_btn_cut": "Cut & Save Media",
        "cutter_btn_cutting": "Cutting media...",
        "toast_cutter_no_file": "Please select a video or audio file first",
        "toast_cutter_invalid_range": "Start time must be less than end time",
        "toast_cutter_success": "Media cut and saved successfully to Downloads",
        "toast_cutter_error": "Failed to cut media, please verify the input file",

        # Video Converter Page
        "page_converter_title": "Video & Media Converter",
        "page_converter_subtitle": "Convert, resize, and compress videos to any format easily with top quality",
        "conv_select_file": "Choose Video to Convert",
        "conv_drop_hint": "Drag & drop video file here or click to browse",
        "conv_target_format": "Target Format",
        "conv_resolution": "Target Resolution",
        "conv_compression": "Quality & Compression Preset",
        "conv_res_original": "Original",
        "conv_res_1080": "1080p (FHD)",
        "conv_res_720": "720p (HD)",
        "conv_res_480": "480p (SD)",
        "conv_preset_high": "High Quality",
        "conv_preset_balanced": "Balanced",
        "conv_preset_small": "Small Size (Compressed)",
        "conv_btn_start": "Start Video Conversion",
        "conv_btn_converting": "Converting video...",
        "conv_btn_cancel": "Cancel",
        "conv_progress_label": "Progress:",
        "toast_conv_no_file": "Please select a video file first",
        "toast_conv_success": "Video converted and saved successfully to Downloads",
        "toast_conv_error": "Failed to convert video, please verify input file",

        "page_history_title": "Download History",
        "page_history_subtitle": "All previously downloaded media files",
        "search_history_placeholder": "Search history by title or channel...",
        "btn_clear_history": "Clear History",
        "empty_history_title": "Download history is empty",
        "empty_history_subtitle": "Completed video and audio downloads will be listed here.",
        "tip_delete_record": "Remove from history",

        "page_settings_title": "Settings",
        "page_settings_subtitle": "Customize theme, language, and smart default options",
        "settings_appearance_section": "Appearance & Language",
        "settings_theme_label": "Appearance Mode",
        "settings_lang_label": "Interface Language",
        "settings_defaults_section": "Smart Download Defaults",
        "settings_default_path": "Default Save Folder",
        "settings_default_quality": "Default Video Quality",
        "settings_default_format": "Default Container Format",
        "settings_concurrent": "Concurrent Downloads",
        "settings_auto_analyze": "Automatically analyze URL on paste (Ctrl+V)",
        "settings_minimize_tray": "Minimize to System Tray on close",
        "settings_about_section": "About & Developer",
        "dev_copyright": "Copyright © by Ahmed Hagag",
        "dev_contact": "ahmed.m.hagag22@gmail.com",
        "dev_contact_label": "Contact & Support:",
        "btn_copy_email": "Copy Email",
        "toast_email_copied": "Email copied to clipboard",
        "btn_save_settings": "Save Settings",
        "btn_show_welcome": "Show Welcome Guide",

        "playlist_dialog_title": "Select Playlist Videos",
        "playlist_search_placeholder": "Filter videos in playlist...",
        "playlist_select_all": "Select All",
        "playlist_invert": "Invert Selection",
        "playlist_selected_count": "Selected: {selected} of {total}",
        "playlist_confirm": "Confirm Selection",
        "playlist_cancel": "Cancel",

        "welcome_title": "Welcome to Smart Media Downloader",
        "welcome_subtitle": "Download videos and audio in top quality in just 3 simple steps:",
        "welcome_step1_title": "1. Paste Link",
        "welcome_step1_desc": "Copy any video or playlist link and press Ctrl+V to analyze automatically.",
        "welcome_step2_title": "2. Pick Quality & Format",
        "welcome_step2_desc": "Choose Video or Audio and click a quality chip like 1080p, 4K, or MP3.",
        "welcome_step3_title": "3. Start Download",
        "welcome_step3_desc": "Track live progress, speed, and ETA in the Active Downloads tab.",
        "welcome_start_btn": "Get Started Now",

        "toast_pasted": "Link pasted from clipboard",
        "toast_empty_clipboard": "Clipboard is empty",
        "toast_invalid_url": "Please enter a valid URL first",
        "toast_analyze_success": "Link analyzed successfully",
        "toast_analyze_error": "Failed to analyze link, check URL or connection",
        "toast_download_started": "Download started and added to Active tab",
        "toast_download_completed": "Download completed: {title}",
        "toast_download_failed": "Download failed: {title}",
        "toast_settings_saved": "Settings saved successfully",
        "toast_history_cleared": "Download history cleared",
        "toast_folder_missing": "Folder does not exist on disk",

        "tray_open": "Open Window",
        "tray_pause_all": "Pause All",
        "tray_exit": "Exit",
    },
}


class I18nManager:
    """مدير اللغة واتجاه الواجهة (RTL للعربية / LTR للإنجليزية)."""

    def __init__(self, lang: str = "en") -> None:
        self._lang = lang if lang in TRANSLATIONS else "en"

    @property
    def lang(self) -> str:
        return self._lang

    @lang.setter
    def lang(self, value: str) -> None:
        if value in TRANSLATIONS:
            self._lang = value

    @property
    def is_rtl(self) -> bool:
        return self._lang == "ar"

    def t(self, key: str, **kwargs: object) -> str:
        """استرجاع النص المترجم حسب المفتاح مع دعم المتغيرات."""
        table = TRANSLATIONS.get(self._lang, TRANSLATIONS["ar"])
        text = table.get(key, TRANSLATIONS["ar"].get(key, key))
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text

    @property
    def align_start(self) -> str:
        """محاذاة البداية (يمين في العربية، يسار في الإنجليزية)."""
        return "e" if self.is_rtl else "w"

    @property
    def align_end(self) -> str:
        """محاذاة النهاية (يسار في العربية، يمين في الإنجليزية)."""
        return "w" if self.is_rtl else "e"

    @property
    def side_start(self) -> str:
        """الجانب الأول في Pack (right في العربية، left في الإنجليزية)."""
        return "right" if self.is_rtl else "left"

    @property
    def side_end(self) -> str:
        """الجانب المقابل في Pack (left في العربية، right في الإنجليزية)."""
        return "left" if self.is_rtl else "right"

    @property
    def justify(self) -> str:
        """اتجاه محاذاة الفقرات النصية."""
        return "right" if self.is_rtl else "left"


# كائن مشترك افتراضي
i18n = I18nManager("ar")
