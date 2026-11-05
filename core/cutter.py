"""
محرك تقطيع ومعالجة المقاطع الصوتية (core/cutter.py).
يدعم:
- فحص وحساب مدة الملفات الصوتية والمرئية بدقة.
- استخراج وقص أي مقطع زمني (البداية والنهاية).
- تطبيق تأثيرات التلاشي الصوتي (Fade In / Fade Out).
- التصدير بصيغ متعددة (MP3, M4A, WAV, FLAC).
- تشغيل المعاينة الصوتية للمقطع المحدد وإيقافها فورياً.
"""

import os
import sys
import shutil
import subprocess
import threading
import time
import wave
from pathlib import Path
from typing import Optional, Set

from core.downloader import has_working_ffmpeg, _FFMPEG_PATH

VIDEO_EXTENSIONS: Set[str] = {
    ".mp4", ".mkv", ".webm", ".avi", ".mov", ".flv", ".ts", ".m4v", ".wmv", ".3gp"
}
AUDIO_EXTENSIONS: Set[str] = {
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".opus", ".wma"
}


def is_video_file(file_path: str) -> bool:
    """التحقق مما إذا كان الملف المعطى ملف فيديو بحسب لاحقته."""
    return Path(file_path).suffix.lower() in VIDEO_EXTENSIONS


def is_audio_file(file_path: str) -> bool:
    """التحقق مما إذا كان الملف المعطى ملف صوت بحسب لاحقته."""
    return Path(file_path).suffix.lower() in AUDIO_EXTENSIONS


def _get_ffmpeg_tool(tool_name: str = "ffmpeg") -> Optional[str]:
    """الحصول على المسار الكامل لأداة FFmpeg أو FFprobe أو FFplay."""
    has_working_ffmpeg()
    exe_name = f"{tool_name}.exe" if os.name == "nt" else tool_name

    # 1. البحث في المجلد المكتشف مسبقاً في downloader
    if _FFMPEG_PATH:
        p = Path(_FFMPEG_PATH) / exe_name
        if p.exists():
            return str(p)

    # 2. فحص مسار التطبيق المحلي أو حزمة EXE المستقلة (مجلد bin أو بجانب التطبيق)
    app_dirs = []
    if hasattr(sys, "_MEIPASS"):
        app_dirs.extend([Path(sys._MEIPASS), Path(sys._MEIPASS) / "bin"])
    if hasattr(sys, "executable") and sys.executable:
        app_dirs.extend([Path(sys.executable).parent, Path(sys.executable).parent / "bin"])
    app_dirs.extend([
        Path(__file__).resolve().parent.parent,
        Path(__file__).resolve().parent.parent / "bin",
    ])
    for ad in app_dirs:
        tool_file = ad / exe_name
        if tool_file.exists():
            return str(tool_file)

    # 3. فحص مسار hermes tools المعروف
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        hermes_tools = Path(local_app_data) / "hermes" / "tools"
        if hermes_tools.exists():
            for match in hermes_tools.glob(f"ffmpeg*/bin/{exe_name}"):
                if match.exists():
                    return str(match)

    # 3. فحص PATH في النظام
    found = shutil.which(tool_name)
    if found:
        return found

    return None


def get_media_duration(file_path: str) -> float:
    """استخراج مدة الملف الصوتي أو المرئي بالثواني."""
    p = Path(file_path)
    if not p.exists():
        return 0.0

    # محاولة سريعة لملفات WAV عبر wave module القياسي
    if p.suffix.lower() == ".wav":
        try:
            with wave.open(str(p), "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                if rate > 0:
                    return float(frames) / float(rate)
        except Exception:
            pass

    # استخدام ffprobe
    ffprobe_exe = _get_ffmpeg_tool("ffprobe")
    if ffprobe_exe:
        try:
            cmd = [
                ffprobe_exe,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(p),
            ]
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=6, creationflags=flags)
            if res.returncode == 0 and res.stdout.strip():
                val = float(res.stdout.strip())
                if val > 0:
                    return val
        except Exception:
            pass

    # محاولة عبر ffmpeg مباشرة (استخراج المدة من مخرجات السجل)
    ffmpeg_exe = _get_ffmpeg_tool("ffmpeg")
    if ffmpeg_exe:
        try:
            cmd = [ffmpeg_exe, "-i", str(p)]
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=6, creationflags=flags)
            output = res.stderr
            if "Duration:" in output:
                dur_str = output.split("Duration:")[1].split(",")[0].strip()
                parts = dur_str.split(":")
                if len(parts) == 3:
                    h, m, s = float(parts[0]), float(parts[1]), float(parts[2])
                    return h * 3600 + m * 60 + s
        except Exception:
            pass

    return 0.0


def cut_audio(
    input_path: str,
    output_path: str,
    start_sec: float,
    end_sec: float,
    fmt: str = "mp3",
    quality: str = "320kbps",
    fade_in: float = 0.0,
    fade_out: float = 0.0,
) -> bool:
    """
    قص مقطع صوتي وتصديره بالجودة والصيغة المطلوبة مع تأثيرات التلاشي الاختيارية.
    """
    inp = Path(input_path)
    out = Path(output_path)
    if not inp.exists():
        return False

    out.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_exe = _get_ffmpeg_tool("ffmpeg")
    if not ffmpeg_exe:
        return False

    start = max(0.0, start_sec)
    end = max(start + 0.1, end_sec)
    segment_duration = end - start

    # تجهيز فلاتر التلاشي إن وجدت
    filters = []
    if fade_in > 0.0:
        actual_in = min(fade_in, segment_duration / 2.0)
        filters.append(f"afade=t=in:st=0:d={actual_in:.2f}")

    if fade_out > 0.0:
        actual_out = min(fade_out, segment_duration / 2.0)
        out_start = max(0.0, segment_duration - actual_out)
        filters.append(f"afade=t=out:st={out_start:.2f}:d={actual_out:.2f}")

    # تجهيز خيارات الترميز حسب الصيغة والجودة
    fmt_lower = fmt.lower().strip()
    bitrate = quality.replace("kbps", "").strip()
    if not bitrate.isdigit():
        bitrate = "320"

    codec_args = []
    if fmt_lower == "mp3":
        codec_args = ["-c:a", "libmp3lame", "-b:a", f"{bitrate}k"]
    elif fmt_lower in ("m4a", "aac"):
        codec_args = ["-c:a", "aac", "-b:a", f"{bitrate}k"]
    elif fmt_lower == "wav":
        codec_args = ["-c:a", "pcm_s16le"]
    elif fmt_lower == "flac":
        codec_args = ["-c:a", "flac"]
    else:
        codec_args = ["-c:a", "libmp3lame", "-b:a", f"{bitrate}k"]

    cmd = [
        ffmpeg_exe,
        "-y",
        "-ss", f"{start:.3f}",
        "-to", f"{end:.3f}",
        "-i", str(inp),
        "-vn",  # استبعاد الفيديو واستخراج الصوت فقط
    ]

    if filters:
        cmd.extend(["-af", ",".join(filters)])

    cmd.extend(codec_args)
    cmd.append(str(out))

    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=60, creationflags=flags)
        return res.returncode == 0 and out.exists() and out.stat().st_size > 0
    except Exception:
        return False


def cut_video(
    input_path: str,
    output_path: str,
    start_sec: float,
    end_sec: float,
    mode: str = "fast",
    fmt: str = "mp4",
    remove_audio: bool = False,
) -> bool:
    """
    قص مقطع فيديو وتصديره بالصيغة والنمط المحددين:
    - mode="fast": قص فوري بدون إعادة ترميز (-c copy) للحفاظ التام على الجودة والسرعة الفائقة.
    - mode="accurate": قص دقيق مع إعادة الترميز لضمان دقة الإطارات (H.264 / AAC).
    - fmt="gif": تحويل المقطع المحدد إلى صورة متحركة GIF عالية الدقة عبر palettegen/paletteuse.
    - fmt="mp3": استخراج مسار الصوت فقط من الفيديو المحدد.
    """
    inp = Path(input_path)
    out = Path(output_path)
    if not inp.exists():
        return False

    ffmpeg_exe = _get_ffmpeg_tool("ffmpeg")
    if not ffmpeg_exe:
        return False

    start = max(0.0, start_sec)
    end = max(start + 0.1, end_sec)
    duration = end - start

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        try:
            out.unlink()
        except Exception:
            pass

    # إذا كانت الصيغة المطلوبة صوت فقط (mp3 / m4a / wav / flac)
    if fmt.lower() in ["mp3", "m4a", "wav", "flac"]:
        return cut_audio(
            input_path=input_path,
            output_path=output_path,
            start_sec=start,
            end_sec=end,
            fmt=fmt.lower(),
        )

    # وضع تحويل الفيديو إلى صورة متحركة GIF عالية الدقة
    if fmt.lower() == "gif":
        cmd = [
            ffmpeg_exe,
            "-y",
            "-ss", f"{start:.3f}",
            "-t", f"{duration:.3f}",
            "-i", str(inp),
            "-filter_complex", "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
            str(out),
        ]
    elif mode == "fast" and fmt.lower() not in ["webm"]:
        # قص سريع بدون فقدان للجودة (Lossless Stream Copy)
        cmd = [
            ffmpeg_exe,
            "-y",
            "-ss", f"{start:.3f}",
            "-to", f"{end:.3f}",
            "-i", str(inp),
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
        ]
        if remove_audio:
            cmd.append("-an")
        cmd.append(str(out))
    else:
        # قص دقيق مع إعادة الترميز (Accurate Re-encode)
        cmd = [
            ffmpeg_exe,
            "-y",
            "-ss", f"{start:.3f}",
            "-to", f"{end:.3f}",
            "-i", str(inp),
        ]
        if fmt.lower() == "webm":
            cmd.extend(["-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "32"])
            if not remove_audio:
                cmd.extend(["-c:a", "libopus", "-b:a", "128k"])
        elif fmt.lower() == "mkv":
            cmd.extend(["-c:v", "libx264", "-preset", "fast", "-crf", "22"])
            if not remove_audio:
                cmd.extend(["-c:a", "aac", "-b:a", "192k"])
        else:  # mp4
            cmd.extend(["-c:v", "libx264", "-preset", "fast", "-crf", "22"])
            if not remove_audio:
                cmd.extend(["-c:a", "aac", "-b:a", "192k"])

        if remove_audio:
            cmd.append("-an")
        cmd.append(str(out))

    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=120, creationflags=flags)
        return res.returncode == 0 and out.exists() and out.stat().st_size > 0
    except Exception:
        return False


class AudioPreviewPlayer:
    """مشغل صوتي تفاعلي مع دعم التقديم والتأخير (Seek Bar) والإيقاف المؤقت."""

    def __init__(self) -> None:
        self._process: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
        self._file_path: Optional[str] = None
        self._start_offset: float = 0.0
        self._started_at: float = 0.0
        self._paused_pos: float = 0.0
        self._is_paused: bool = False
        self._duration: float = 0.0

    def play(
        self,
        file_path: str,
        start_sec: float = 0.0,
        duration_sec: Optional[float] = None,
        total_duration: Optional[float] = None,
        show_video: bool = True,
    ) -> bool:
        """بدء أو استئناف تشغيل الوسائط (صوت أو فيديو) من موضع معين."""
        self.stop()
        p = Path(file_path)
        if not p.exists():
            return False

        ffplay_exe = _get_ffmpeg_tool("ffplay")
        if not ffplay_exe:
            return False

        start = max(0.0, start_sec)
        self._file_path = str(p.resolve())
        self._start_offset = start
        self._is_paused = False
        self._duration = total_duration or get_media_duration(self._file_path)

        cmd = [
            ffplay_exe,
            "-autoexit",
            "-ss", f"{start:.3f}",
        ]

        # إذا كان ملف فيديو ونريد عرض نافذة المعاينة
        if is_video_file(self._file_path) and show_video:
            cmd.extend([
                "-window_title", "SmartDownloader Preview",
                "-x", "640",
                "-y", "360",
            ])
        else:
            cmd.append("-nodisp")

        if duration_sec is not None and duration_sec > 0:
            cmd.extend(["-t", f"{duration_sec:.3f}"])

        cmd.append(str(p))
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

        try:
            with self._lock:
                self._started_at = time.time()
                self._process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=flags,
                )
            return True
        except Exception:
            return False

    def pause(self) -> None:
        """إيقاف مؤقت مع حفظ موضع التشغيل الحالي."""
        if not self.is_playing():
            return
        pos = self.get_current_position()
        self._terminate_process()
        self._paused_pos = pos
        self._is_paused = True

    def resume(self) -> bool:
        """استئناف التشغيل من الموضع المحفوظ."""
        if self._file_path and self._is_paused:
            return self.play(
                self._file_path,
                start_sec=self._paused_pos,
                total_duration=self._duration,
            )
        return False

    def seek(self, position_sec: float) -> bool:
        """الانتقال الفوري إلى موضع زمني محدد."""
        was_playing = self.is_playing()
        target_pos = max(0.0, min(self._duration, position_sec))
        if self._file_path:
            if was_playing:
                return self.play(
                    self._file_path,
                    start_sec=target_pos,
                    total_duration=self._duration,
                )
            else:
                self._paused_pos = target_pos
                self._is_paused = True
                return True
        return False

    def get_current_position(self) -> float:
        """استخراج موضع التشغيل الحالي بالثواني."""
        if self._is_paused:
            return self._paused_pos
        if self.is_playing():
            elapsed = time.time() - self._started_at
            curr = self._start_offset + elapsed
            if self._duration > 0:
                curr = min(self._duration, curr)
            return curr
        return self._start_offset

    def stop(self) -> None:
        """إيقاف التشغيل بالكامل وإعادة ضبط الحالة."""
        self._terminate_process()
        self._is_paused = False
        self._start_offset = 0.0
        self._paused_pos = 0.0

    def _terminate_process(self) -> None:
        with self._lock:
            if self._process is not None:
                try:
                    self._process.terminate()
                    self._process.wait(timeout=0.6)
                except Exception:
                    try:
                        self._process.kill()
                    except Exception:
                        pass
                self._process = None

    def is_playing(self) -> bool:
        """التحقق مما إذا كان الصوت قيد التشغيل حالياً."""
        with self._lock:
            if self._process is None or self._is_paused:
                return False
            poll_result = self._process.poll()
            if poll_result is not None:
                self._process = None
                return False
            return True

    def is_paused(self) -> bool:
        return self._is_paused


# اسم مستعار عام للمشغل لدعم الصوت والفيديو معاً
MediaPreviewPlayer = AudioPreviewPlayer
