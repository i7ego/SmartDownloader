"""
محرك التحليل والتحميل (core/downloader.py)
يدعم:
- تحليل الروابط الفردية وقوائم التشغيل عبر yt-dlp مع مسجل داخلي آمن (Silent Logger) متوافق مع pythonw.
- الاكتشاف التلقائي لمسار FFmpeg على النظام لدمج أعلى الجودات (1080p / 4K) وتحويل الصوتيات (MP3 / M4A).
- تحميل الصور المصغرة وقصّها بزوايا مستديرة (Rounded Thumbnail).
- إدارة مهام التحميل المتزامنة لقوائم التشغيل (Queue + Semaphore) مع حساب النسبة، السرعة، والوقت المتبقي.
- الإيقاف المؤقت (Pause)، الاستئناف (Resume)، والإلغاء (Cancel).
"""

import io
import os
import sys
import shutil
import subprocess
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from PIL import Image, ImageDraw
import requests
import yt_dlp

from ui import theme

_FFMPEG_CHECKED: Optional[bool] = None
_FFMPEG_PATH: Optional[str] = None


class _SilentYtdlpLogger:
    """مسجل صامت لـ yt-dlp لمنع أخطاء الترميز أو غياب stdout عند التشغيل عبر pythonw.exe."""

    def debug(self, msg: str) -> None:
        pass

    def info(self, msg: str) -> None:
        pass

    def warning(self, msg: str) -> None:
        pass

    def error(self, msg: str) -> None:
        pass


def _verify_ffmpeg_binary(exe_path: str) -> bool:
    """التحقق من أن ملف ffmpeg.exe قابل للتنفيذ الفعلي."""
    try:
        res = subprocess.run(
            [exe_path, "-version"],
            capture_output=True,
            timeout=4,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        return res.returncode == 0
    except Exception:
        return False


def has_working_ffmpeg() -> bool:
    """البحث عن برنامج FFmpeg على النظام والتحقق من عمله الفعلي."""
    global _FFMPEG_CHECKED, _FFMPEG_PATH
    if _FFMPEG_CHECKED is not None:
        return _FFMPEG_CHECKED

    candidates: List[Path] = []

    # 1. فحص مسار التطبيق المحلي أو حزمة EXE المستقلة (مجلد bin أو بجانب التطبيق)
    app_dirs: List[Path] = []
    if hasattr(sys, "_MEIPASS"):
        app_dirs.extend([Path(sys._MEIPASS), Path(sys._MEIPASS) / "bin"])
    if hasattr(sys, "executable") and sys.executable:
        app_dirs.extend([Path(sys.executable).parent, Path(sys.executable).parent / "bin"])
    app_dirs.extend([
        Path(__file__).resolve().parent.parent,
        Path(__file__).resolve().parent.parent / "bin",
    ])
    for ad in app_dirs:
        ff = ad / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        if ff.exists():
            candidates.append(ff)

    # 2. فحص imageio_ffmpeg إن وُجد
    try:
        import imageio_ffmpeg  # type: ignore[import-not-found]
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe:
            candidates.append(Path(exe))
    except Exception:
        pass

    # 2. فحص المسارات المعروفة على جهاز المستخدم (hermes tools / WinGet / Program Files)
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        hermes_tools = Path(local_app_data) / "hermes" / "tools"
        if hermes_tools.exists():
            candidates.extend(hermes_tools.glob("ffmpeg*/bin/ffmpeg.exe"))
        winget_pkgs = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        if winget_pkgs.exists():
            candidates.extend(winget_pkgs.glob("*FFmpeg*/**/bin/ffmpeg.exe"))

    # 3. فحص PATH العام
    which_ff = shutil.which("ffmpeg")
    if which_ff:
        candidates.append(Path(which_ff))

    for cand in candidates:
        if cand.exists() and _verify_ffmpeg_binary(str(cand)):
            _FFMPEG_PATH = str(cand.parent)
            # إضافة مجلد FFmpeg إلى PATH للعملية الحالية
            os.environ["PATH"] = f"{_FFMPEG_PATH}{os.pathsep}{os.environ.get('PATH', '')}"
            _FFMPEG_CHECKED = True
            return True

    _FFMPEG_CHECKED = False
    return False


def format_duration(seconds: Optional[float]) -> str:
    """تنسيق المدة بالثواني إلى صيغة MM:SS أو HH:MM:SS."""
    if not seconds or seconds <= 0:
        return "00:00"
    total = int(seconds)
    hrs, rem = divmod(total, 3600)
    mins, secs = divmod(rem, 60)
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


def format_speed(bytes_per_sec: Optional[float]) -> str:
    """تنسيق سرعة التحميل بشكل مقروء."""
    if not bytes_per_sec or bytes_per_sec <= 0:
        return "0 KB/s"
    if bytes_per_sec >= 1024 * 1024:
        return f"{bytes_per_sec / (1024 * 1024):.1f} MB/s"
    return f"{bytes_per_sec / 1024:.0f} KB/s"


def create_rounded_thumbnail(
    pil_img: Optional[Image.Image],
    size: tuple[int, int] = (160, 92),
    radius: int = theme.RADIUS_THUMBNAIL,
) -> Image.Image:
    """تجهيز صورة مصغرة بزوايا مستديرة، أو إنشاء صورة افتراضية أنيقة عند عدم توفرها."""
    if pil_img is None:
        img = Image.new("RGBA", size, theme.DARK_BG_ELEVATED)
        draw = ImageDraw.Draw(img)
        cx, cy = size[0] // 2, size[1] // 2
        r = min(size) // 4
        draw.ellipse(
            (cx - r, cy - r, cx + r, cy + r),
            fill=theme.COLOR_PRIMARY,
        )
        draw.polygon(
            [(cx - r // 3, cy - r // 2), (cx - r // 3, cy + r // 2), (cx + r // 2, cy)],
            fill=theme.COLOR_ON_PRIMARY,
        )
    else:
        img = pil_img.convert("RGBA").resize(size, Image.Resampling.LANCZOS)

    mask = Image.new("L", size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)

    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def fetch_thumbnail_image(url: Optional[str], size: tuple[int, int] = (160, 92)) -> Image.Image:
    """تحميل الصورة المصغرة من الإنترنت وتحويلها إلى صورة بزوايا مستديرة."""
    if url:
        try:
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200:
                raw_img = Image.open(io.BytesIO(resp.content))
                return create_rounded_thumbnail(raw_img, size=size)
        except Exception:
            pass
    return create_rounded_thumbnail(None, size=size)


@dataclass
class MediaInfo:
    """نتيجة تحليل رابط فيديو أو قائمة تشغيل."""

    url: str
    title: str
    channel: str
    duration_seconds: float = 0.0
    duration_str: str = "00:00"
    thumbnail_url: Optional[str] = None
    thumbnail_image: Optional[Image.Image] = None
    is_playlist: bool = False
    playlist_entries: List[Dict[str, Any]] = field(default_factory=list)
    selected_indices: List[int] = field(default_factory=list)
    video_qualities: List[str] = field(
        default_factory=lambda: ["4K", "1440p", "1080p", "720p", "480p", "360p"]
    )
    video_formats: List[str] = field(
        default_factory=lambda: ["MP4", "MKV", "WEBM"]
    )
    audio_qualities: List[str] = field(
        default_factory=lambda: ["320kbps", "256kbps", "192kbps", "128kbps"]
    )
    audio_formats: List[str] = field(
        default_factory=lambda: ["MP3", "M4A", "WAV", "FLAC", "OPUS"]
    )


@dataclass
class DownloadTask:
    """بيانات وحالة مهمة تحميل واحدة."""

    task_id: str
    url: str
    title: str
    channel: str
    duration_str: str
    media_type: str             # "video" أو "audio"
    quality: str                # مثل "1080p" أو "320kbps"
    fmt: str                    # مثل "MP4" أو "MP3"
    save_dir: str
    thumbnail_image: Optional[Image.Image] = None
    subtitles: bool = False
    embed_thumbnail: bool = False
    speed_limit_kbps: int = 0
    filename_template: str = "%(title)s.%(ext)s"

    status: str = "downloading"  # queued, downloading, paused, completed, failed
    progress: float = 0.0        # 0.0 إلى 1.0
    speed_str: str = "0 KB/s"
    eta_str: str = "--:--"
    error_message: str = ""

    pause_event: threading.Event = field(default_factory=threading.Event)
    cancel_event: threading.Event = field(default_factory=threading.Event)

    def __post_init__(self) -> None:
        self.pause_event.set()  # غير متوقف افتراضياً


class DownloadCancelledError(Exception):
    """استثناء داخلي عند إلغاء التحميل من قِبل المستخدم."""


class DownloadManager:
    """مدير التحليل والتحميل الخلفي مع دعم الطوابير المتزامنة لقوائم التشغيل."""

    def __init__(
        self,
        on_task_updated: Optional[Callable[[DownloadTask], None]] = None,
        on_task_completed: Optional[Callable[[DownloadTask], None]] = None,
        on_task_failed: Optional[Callable[[DownloadTask], None]] = None,
        max_concurrent: int = 3,
    ) -> None:
        self.tasks: List[DownloadTask] = []
        self.on_task_updated = on_task_updated
        self.on_task_completed = on_task_completed
        self.on_task_failed = on_task_failed
        self._semaphore = threading.Semaphore(max_concurrent)

        # تهيئة مسار FFmpeg مبكراً
        has_working_ffmpeg()

    def analyze_url_async(
        self,
        url: str,
        on_success: Callable[[MediaInfo], None],
        on_error: Callable[[str], None],
    ) -> None:
        """تحليل الرابط في خيط خلفي (Background Thread) لعدم تجميد الواجهة."""

        def _worker() -> None:
            try:
                info = self.analyze_url(url)
                on_success(info)
            except Exception as exc:
                on_error(str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    def analyze_url(self, url: str) -> MediaInfo:
        """استخراج بيانات الفيديو أو قائمة التشغيل عبر yt-dlp."""
        clean_url = url.strip()
        if not clean_url or not (
            clean_url.startswith("http://") or clean_url.startswith("https://")
        ):
            raise ValueError("Invalid URL")

        # دعم روابط قوائم التشغيل الصريحة أو روابط الفيديو التي تحتوي على list=
        has_list_param = ("/playlist?" in clean_url) or ("list=" in clean_url)

        ydl_opts: Dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "logger": _SilentYtdlpLogger(),
            "extract_flat": "in_playlist",
            "skip_download": True,
            "noplaylist": not has_list_param,
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "socket_timeout": 15,
        }

        if "example.com" in clean_url or "demo" in clean_url:
            is_pl = "playlist" in clean_url or "list=" in clean_url
            entries = (
                [
                    {
                        "title": f"الدرس التعليمي رقم {i + 1}",
                        "duration_str": f"0{i + 3}:45",
                        "url": f"{clean_url}/{i+1}",
                    }
                    for i in range(5)
                ]
                if is_pl
                else []
            )
            return MediaInfo(
                url=clean_url,
                title="مقطع فيديو تجريبي عالي الدقة (4K UHD)"
                if not is_pl
                else "دورة البرمجة المتكاملة بلغة بايثون",
                channel="قناة التقنية العربية",
                duration_seconds=525,
                duration_str="08:45",
                thumbnail_image=create_rounded_thumbnail(None),
                is_playlist=is_pl,
                playlist_entries=entries,
                selected_indices=list(range(len(entries))),
            )

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                data = ydl.extract_info(clean_url, download=False)
        except Exception as exc:
            raise RuntimeError(f"تعذّر تحليل الرابط: {exc}") from exc

        if not data:
            raise RuntimeError("لم يتم العثور على بيانات للرابط المدخل")

        is_playlist = data.get("_type") == "playlist" or "entries" in data
        entries_list: List[Dict[str, Any]] = []
        if is_playlist:
            raw_entries = [e for e in (data.get("entries") or []) if e]
            for idx, entry in enumerate(raw_entries):
                # تخطي الفيديوهات المحذوفة أو الخاصة داخل قائمة التشغيل
                entry_title = str(entry.get("title") or "")
                if entry_title in ("[Deleted video]", "[Private video]"):
                    continue
                dur = entry.get("duration")
                raw_entry_url = (
                    entry.get("webpage_url")
                    or entry.get("url")
                    or entry.get("id")
                    or clean_url
                )
                entry_url = str(raw_entry_url)
                if not entry_url.startswith("http"):
                    entry_url = f"https://www.youtube.com/watch?v={entry_url}"
                entries_list.append(
                    {
                        "index": len(entries_list),
                        "title": entry_title or f"فيديو #{len(entries_list) + 1}",
                        "url": entry_url,
                        "duration_str": format_duration(dur),
                    }
                )

        title = data.get("title") or "فيديو بدون عنوان"
        channel = (
            data.get("uploader")
            or data.get("channel")
            or data.get("extractor_key")
            or "مصدر الوسائط"
        )
        duration = float(data.get("duration") or 0.0)
        thumb_url = data.get("thumbnail")
        if not thumb_url and data.get("thumbnails"):
            thumb_url = data["thumbnails"][-1].get("url")

        thumb_img = fetch_thumbnail_image(thumb_url)

        return MediaInfo(
            url=clean_url,
            title=title,
            channel=channel,
            duration_seconds=duration,
            duration_str=format_duration(duration),
            thumbnail_url=thumb_url,
            thumbnail_image=thumb_img,
            is_playlist=is_playlist and len(entries_list) > 0,
            playlist_entries=entries_list,
            selected_indices=list(range(len(entries_list))),
        )

    def start_download(
        self,
        media: MediaInfo,
        media_type: str,
        quality: str,
        fmt: str,
        save_dir: str,
        subtitles: bool = False,
        embed_thumbnail: bool = False,
        speed_limit_kbps: int = 0,
        filename_template: str = "%(title)s.%(ext)s",
    ) -> List[DownloadTask]:
        """إنشاء مهمة (أو مهام لقائمة التشغيل) وبدء التحميل في الخلفية."""
        created_tasks: List[DownloadTask] = []

        if media.is_playlist and media.playlist_entries:
            indices = (
                media.selected_indices
                if media.selected_indices
                else list(range(len(media.playlist_entries)))
            )
            for idx in indices:
                if 0 <= idx < len(media.playlist_entries):
                    entry = media.playlist_entries[idx]
                    task = DownloadTask(
                        task_id=uuid.uuid4().hex[:10],
                        url=str(entry.get("url") or media.url),
                        title=str(entry.get("title") or media.title),
                        channel=media.channel,
                        duration_str=str(entry.get("duration_str") or media.duration_str),
                        media_type=media_type,
                        quality=quality,
                        fmt=fmt,
                        save_dir=save_dir,
                        thumbnail_image=media.thumbnail_image,
                        subtitles=subtitles,
                        embed_thumbnail=embed_thumbnail,
                        speed_limit_kbps=speed_limit_kbps,
                        filename_template=filename_template,
                        status="queued",
                    )
                    self.tasks.insert(0, task)
                    created_tasks.append(task)
                    threading.Thread(
                        target=self._run_task, args=(task,), daemon=True
                    ).start()
        else:
            task = DownloadTask(
                task_id=uuid.uuid4().hex[:10],
                url=media.url,
                title=media.title,
                channel=media.channel,
                duration_str=media.duration_str,
                media_type=media_type,
                quality=quality,
                fmt=fmt,
                save_dir=save_dir,
                thumbnail_image=media.thumbnail_image,
                subtitles=subtitles,
                embed_thumbnail=embed_thumbnail,
                speed_limit_kbps=speed_limit_kbps,
                filename_template=filename_template,
                status="downloading",
            )
            self.tasks.insert(0, task)
            created_tasks.append(task)
            threading.Thread(target=self._run_task, args=(task,), daemon=True).start()

        return created_tasks

    def _build_format_selector(self, task: DownloadTask, ffmpeg_ok: bool) -> str:
        """بناء تعبير اختيار الجودة لـ yt-dlp مع مراعاة وجود FFmpeg أو عدمه."""
        if task.media_type == "audio":
            return "bestaudio/best"

        height_map = {
            "4K": 2160,
            "1440p": 1440,
            "1080p": 1080,
            "720p": 720,
            "480p": 480,
            "360p": 360,
            "240p": 240,
        }
        h = height_map.get(task.quality)

        if ffmpeg_ok:
            if h:
                return f"bestvideo[height<={h}]+bestaudio/best[height<={h}]/bestvideo+bestaudio/best"
            return "bestvideo+bestaudio/best"

        if h:
            return f"best[height<={h}]/best"
        return "best"

    def _run_task(self, task: DownloadTask) -> None:
        """تشغيل عملية التحميل الفعلية مع تنظيم التزامن عبر Semaphore."""
        with self._semaphore:
            if task.cancel_event.is_set():
                task.status = "failed"
                self._notify_update(task)
                return

            task.status = "downloading"
            self._notify_update(task)
            self._execute_download(task)

    def _execute_download(self, task: DownloadTask) -> None:
        Path(task.save_dir).mkdir(parents=True, exist_ok=True)

        # دعم الروابط التجريبية (example.com / demo) لاختبار شريط التقدم والإيقاف المؤقت
        if "example.com" in task.url or "demo" in task.url:
            self._simulate_download(task)
            return

        def _progress_hook(d: Dict[str, Any]) -> None:
            if task.cancel_event.is_set():
                raise DownloadCancelledError("Cancelled by user")

            while not task.pause_event.is_set():
                if task.cancel_event.is_set():
                    raise DownloadCancelledError("Cancelled by user")
                time.sleep(0.2)

            if d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes") or 0
                if total > 0:
                    task.progress = min(0.99, max(0.0, downloaded / total))
                task.speed_str = format_speed(d.get("speed"))
                task.eta_str = format_duration(d.get("eta"))
                task.status = "downloading"
                self._notify_update(task)
            elif d.get("status") == "finished":
                task.progress = 1.0
                task.speed_str = "0 KB/s"
                task.eta_str = "00:00"
                self._notify_update(task)

        ffmpeg_ok = has_working_ffmpeg()
        outtmpl = str(
            Path(task.save_dir) / (task.filename_template or "%(title)s.%(ext)s")
        )
        ydl_opts: Dict[str, Any] = {
            "format": self._build_format_selector(task, ffmpeg_ok=ffmpeg_ok),
            "outtmpl": outtmpl,
            "progress_hooks": [_progress_hook],
            "quiet": True,
            "no_warnings": True,
            "logger": _SilentYtdlpLogger(),
            "noplaylist": True,
            "nocheckcertificate": True,
            "windowsfilenames": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["default", "ios", "android_vr"],
                }
            },
            "writesubtitles": task.subtitles,
            "writethumbnail": task.embed_thumbnail,
        }

        if ffmpeg_ok and _FFMPEG_PATH:
            ydl_opts["ffmpeg_location"] = _FFMPEG_PATH
            if task.media_type == "video":
                ydl_opts["merge_output_format"] = task.fmt.lower()
            elif task.media_type == "audio":
                audio_codec = task.fmt.lower()
                bitrate = task.quality.replace("kbps", "").strip()
                if not bitrate.isdigit():
                    bitrate = "192"
                ydl_opts["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": audio_codec,
                        "preferredquality": bitrate,
                    }
                ]

        if task.speed_limit_kbps and task.speed_limit_kbps > 0:
            ydl_opts["ratelimit"] = task.speed_limit_kbps * 1024

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ret = ydl.download([task.url])
                if ret != 0:
                    raise RuntimeError(f"yt-dlp exited with code {ret}")
            task.status = "completed"
            task.progress = 1.0
            task.eta_str = "00:00"
            self._notify_update(task)
            if self.on_task_completed:
                self.on_task_completed(task)
        except DownloadCancelledError:
            task.status = "failed"
            task.error_message = "Cancelled"
            self._notify_update(task)
        except Exception as exc:
            task.status = "failed"
            task.error_message = str(exc)
            self._notify_update(task)
            if self.on_task_failed:
                self.on_task_failed(task)

    def _simulate_download(self, task: DownloadTask) -> None:
        """محاكاة تقدم التحميل للروابط التجريبية لاختبار الواجهة التفاعلية."""
        steps = 25
        for step in range(1, steps + 1):
            if task.cancel_event.is_set():
                task.status = "failed"
                self._notify_update(task)
                return
            while not task.pause_event.is_set():
                if task.cancel_event.is_set():
                    task.status = "failed"
                    self._notify_update(task)
                    return
                time.sleep(0.15)
            time.sleep(0.12)
            task.progress = step / steps
            task.speed_str = "4.8 MB/s"
            task.eta_str = format_duration((steps - step) * 0.5)
            task.status = "downloading"
            self._notify_update(task)

        task.status = "completed"
        task.progress = 1.0
        task.speed_str = "0 KB/s"
        task.eta_str = "00:00"
        self._notify_update(task)
        if self.on_task_completed:
            self.on_task_completed(task)

    def pause_task(self, task: DownloadTask) -> None:
        if task.status in ("downloading", "queued"):
            task.pause_event.clear()
            task.status = "paused"
            task.speed_str = "0 KB/s"
            self._notify_update(task)

    def resume_task(self, task: DownloadTask) -> None:
        if task.status == "paused":
            task.status = "downloading"
            task.pause_event.set()
            self._notify_update(task)

    def cancel_task(self, task: DownloadTask) -> None:
        task.cancel_event.set()
        task.pause_event.set()
        task.status = "failed"
        self._notify_update(task)

    def pause_all(self) -> None:
        for task in self.tasks:
            if task.status in ("downloading", "queued"):
                self.pause_task(task)

    def resume_all(self) -> None:
        for task in self.tasks:
            if task.status == "paused":
                self.resume_task(task)

    def _notify_update(self, task: DownloadTask) -> None:
        if self.on_task_updated:
            self.on_task_updated(task)


def open_folder_in_explorer(folder_path: str) -> bool:
    """فتح مجلد الحفظ في مستكشف الملفات."""
    p = Path(folder_path)
    if not p.exists():
        return False
    try:
        if os.name == "nt":
            os.startfile(str(p))  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", str(p)])
        return True
    except Exception:
        return False
