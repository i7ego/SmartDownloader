"""
اختبارات وحدة لمحرك تحويل الفيديوهات (core/converter.py).
"""

import subprocess
from pathlib import Path
import pytest

from core.converter import convert_video, VideoConvertOptions
from core.cutter import _get_ffmpeg_tool


@pytest.fixture
def sample_video(tmp_path: Path) -> Path:
    """إنشاء ملف فيديو تجريبي قصير عبر FFmpeg."""
    ffmpeg_exe = _get_ffmpeg_tool("ffmpeg")
    if not ffmpeg_exe:
        pytest.skip("FFmpeg غير متوفر")

    video_path = tmp_path / "test_input.mp4"
    cmd = [
        ffmpeg_exe, "-y",
        "-f", "lavfi", "-i", "testsrc=duration=2:size=640x360:rate=15",
        "-f", "lavfi", "-i", "sine=frequency=1000:duration=2",
        "-c:v", "libx264", "-c:a", "aac",
        str(video_path),
    ]
    res = subprocess.run(cmd, capture_output=True)
    assert res.returncode == 0
    assert video_path.exists()
    return video_path


def test_convert_video_to_mp4_resolution(sample_video: Path, tmp_path: Path) -> None:
    """التحقق من تحويل الفيديو وتغيير دقته إلى 480p."""
    output_mp4 = tmp_path / "output_480p.mp4"
    opts = VideoConvertOptions(
        target_format="mp4",
        resolution="480p",
        quality_preset="balanced",
    )
    progress_records = []
    success = convert_video(
        input_path=str(sample_video),
        output_path=str(output_mp4),
        options=opts,
        progress_callback=lambda p: progress_records.append(p),
    )
    assert success is True
    assert output_mp4.exists()
    assert output_mp4.stat().st_size > 0
    assert len(progress_records) > 0


def test_convert_video_to_audio_mp3(sample_video: Path, tmp_path: Path) -> None:
    """التحقق من استخراج الصوت بصيغة MP3 من ملف الفيديو."""
    output_mp3 = tmp_path / "extracted.mp3"
    opts = VideoConvertOptions(
        target_format="mp3",
        quality_preset="high",
    )
    success = convert_video(
        input_path=str(sample_video),
        output_path=str(output_mp3),
        options=opts,
    )
    assert success is True
    assert output_mp3.exists()
    assert output_mp3.stat().st_size > 0


def test_convert_video_to_gif(sample_video: Path, tmp_path: Path) -> None:
    """التحقق من تحويل الفيديو إلى صورة متحركة GIF عالية الدقة."""
    output_gif = tmp_path / "converted.gif"
    opts = VideoConvertOptions(
        target_format="gif",
        resolution="360p",
    )
    success = convert_video(
        input_path=str(sample_video),
        output_path=str(output_gif),
        options=opts,
    )
    assert success is True
    assert output_gif.exists()
    assert output_gif.stat().st_size > 0
