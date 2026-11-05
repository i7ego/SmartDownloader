"""
محرك تحويل وتغيير صيغ وضغط الفيديوهات (core/converter.py).
يدعم:
- التحويل بين جميع صيغ الفيديو الرئيسية: MP4, MKV, WebM, AVI, MOV, GIF.
- استخراج الصوت بصيغ MP3, M4A, WAV بجودات متعددة.
- تغيير الدقة وتصغير الأبعاد: 1080p (FHD), 720p (HD), 480p (SD), أو الحفاظ على الدقة الأصلية.
- أوضاع الضغط والجودة: جودة فائقة (High Quality), متوازن (Balanced), حجم صغير للمشاركة (Small Size).
- حساب نسبة التقدم في التحويل في الوقت الفعلي مع دعم الإلغاء.
"""

import os
import re
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from core.cutter import _get_ffmpeg_tool, get_media_duration


@dataclass
class VideoConvertOptions:
    """خيارات ومعاملات تحويل الفيديو."""
    target_format: str = "mp4"           # mp4, mkv, webm, avi, mov, gif, mp3
    resolution: str = "original"          # original, 1080p, 720p, 480p
    quality_preset: str = "balanced"      # high, balanced, small
    remove_audio: bool = False
    custom_bitrate: Optional[str] = None


def convert_video(
    input_path: str,
    output_path: str,
    options: Optional[VideoConvertOptions] = None,
    progress_callback: Optional[Callable[[float], None]] = None,
    cancel_event: Optional[threading.Event] = None,
) -> bool:
    """
    تحويل ملف الفيديو إلى الصيغة والدقة المحددة مع تتبع نسبة الإنجاز ودعم الإلغاء.
    """
    inp = Path(input_path)
    out = Path(output_path)
    if not inp.exists():
        return False

    ffmpeg_exe = _get_ffmpeg_tool("ffmpeg")
    if not ffmpeg_exe:
        return False

    if options is None:
        options = VideoConvertOptions()

    total_duration = get_media_duration(str(inp))
    fmt = options.target_format.lower().strip()
    res = options.resolution.lower().strip()
    preset = options.quality_preset.lower().strip()

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        try:
            out.unlink()
        except Exception:
            pass

    cmd = [ffmpeg_exe, "-y", "-i", str(inp)]

    # 1. إعدادات استخراج الصوت فقط (MP3 / WAV / M4A)
    if fmt in ["mp3", "wav", "m4a", "flac"]:
        cmd.append("-vn")
        if fmt == "mp3":
            b_rate = "320k" if preset == "high" else ("128k" if preset == "small" else "192k")
            cmd.extend(["-c:a", "libmp3lame", "-b:a", b_rate])
        elif fmt == "m4a":
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])
        elif fmt == "wav":
            cmd.extend(["-c:a", "pcm_s16le"])
        cmd.append(str(out))
    # 2. إعدادات تحويل الفيديو إلى صورة متحركة GIF
    elif fmt == "gif":
        scale_filter = "scale=480:-1:flags=lanczos"
        if "720" in res:
            scale_filter = "scale=720:-1:flags=lanczos"
        elif "360" in res or "480" in res:
            scale_filter = "scale=360:-1:flags=lanczos"
        
        cmd.extend([
            "-filter_complex",
            f"fps=15,{scale_filter},split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
            str(out),
        ])
    # 3. إعدادات تحويل الفيديو القياسي (MP4, MKV, WebM, AVI, MOV)
    else:
        video_filters = []
        if "1080" in res:
            video_filters.append("scale=-2:1080")
        elif "720" in res:
            video_filters.append("scale=-2:720")
        elif "480" in res:
            video_filters.append("scale=-2:480")

        if video_filters:
            cmd.extend(["-vf", ",".join(video_filters)])

        # إعدادات التكويد وجودة الضغط
        if fmt == "webm":
            crf_val = "22" if preset == "high" else ("38" if preset == "small" else "30")
            cmd.extend(["-c:v", "libvpx-vp9", "-b:v", "0", "-crf", crf_val])
            if not options.remove_audio:
                cmd.extend(["-c:a", "libopus", "-b:a", "128k"])
        elif fmt == "avi":
            q_scale = "2" if preset == "high" else ("6" if preset == "small" else "4")
            cmd.extend(["-c:v", "mpeg4", "-qscale:v", q_scale])
            if not options.remove_audio:
                cmd.extend(["-c:a", "libmp3lame", "-b:a", "192k"])
        else:  # mp4, mkv, mov
            crf_val = "18" if preset == "high" else ("28" if preset == "small" else "23")
            cmd.extend(["-c:v", "libx264", "-preset", "fast", "-crf", crf_val])
            if not options.remove_audio:
                cmd.extend(["-c:a", "aac", "-b:a", "192k"])

        if options.remove_audio:
            cmd.append("-an")

        cmd.append(str(out))

    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        proc = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            universal_newlines=True,
            encoding="utf-8",
            errors="replace",
            creationflags=flags,
        )

        time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")

        if proc.stderr:
            for line in proc.stderr:
                if cancel_event and cancel_event.is_set():
                    proc.kill()
                    if out.exists():
                        try:
                            out.unlink()
                        except Exception:
                            pass
                    return False

                if total_duration > 0 and progress_callback:
                    match = time_pattern.search(line)
                    if match:
                        hours, mins, secs = map(float, match.groups())
                        current_sec = hours * 3600 + mins * 60 + secs
                        progress = min(100.0, max(0.0, (current_sec / total_duration) * 100.0))
                        progress_callback(progress)

        proc.wait(timeout=300)
        success = proc.returncode == 0 and out.exists() and out.stat().st_size > 0
        if success and progress_callback:
            progress_callback(100.0)
        return success
    except Exception:
        return False
