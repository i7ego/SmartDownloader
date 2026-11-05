"""
اختبارات وحدة لمعالجة وتقطيع الصوت والموسيقى (core/cutter.py).
"""

import subprocess
import wave
import struct
from pathlib import Path
import pytest

from core.cutter import (
    get_media_duration,
    cut_audio,
    cut_video,
    is_video_file,
    is_audio_file,
    AudioPreviewPlayer,
    MediaPreviewPlayer,
    _get_ffmpeg_tool,
)


def _create_dummy_wav(path: Path, duration_sec: float = 3.0, sample_rate: int = 44100) -> None:
    """إنشاء ملف WAV حقيقي صالح للاختبار البرمجي."""
    num_samples = int(duration_sec * sample_rate)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        # كتابة موجة صوتية صامتة أو نغمة بسيطة
        data = struct.pack(f"<{num_samples}h", *([1000] * num_samples))
        wf.writeframes(data)


def test_get_media_duration(tmp_path: Path) -> None:
    """التحقق من حساب مدة الملف الصوتي بدقة."""
    wav_path = tmp_path / "test.wav"
    _create_dummy_wav(wav_path, duration_sec=3.0)

    duration = get_media_duration(str(wav_path))
    assert 2.8 <= duration <= 3.2


def test_cut_audio_simple(tmp_path: Path) -> None:
    """اختبار قص جزء محدد من الملف الصوتي."""
    input_wav = tmp_path / "input.wav"
    output_mp3 = tmp_path / "output.mp3"
    _create_dummy_wav(input_wav, duration_sec=4.0)

    success = cut_audio(
        input_path=str(input_wav),
        output_path=str(output_mp3),
        start_sec=1.0,
        end_sec=3.0,
        fmt="mp3",
        quality="192kbps",
    )
    assert success is True
    assert output_mp3.exists()
    out_duration = get_media_duration(str(output_mp3))
    assert 1.8 <= out_duration <= 2.2


def test_cut_audio_with_fade(tmp_path: Path) -> None:
    """اختبار قص الصوت مع تفعيل تأثيرات التلاشي (Fade In / Out)."""
    input_wav = tmp_path / "input_fade.wav"
    output_wav = tmp_path / "output_fade.wav"
    _create_dummy_wav(input_wav, duration_sec=5.0)

    success = cut_audio(
        input_path=str(input_wav),
        output_path=str(output_wav),
        start_sec=1.0,
        end_sec=4.0,
        fmt="wav",
        fade_in=0.5,
        fade_out=0.5,
    )
    assert success is True
    assert output_wav.exists()


def test_preview_player_lifecycle(tmp_path: Path) -> None:
    """اختبار مشغل المعاينة الصوتية وبدء وتوقف العملية."""
    player = AudioPreviewPlayer()
    assert player.is_playing() is False

    wav_path = tmp_path / "preview.wav"
    _create_dummy_wav(wav_path, duration_sec=5.0)

    started = player.play(str(wav_path), start_sec=1.0, duration_sec=3.0)
    if started:
        pos = player.get_current_position()
        assert pos >= 0.9
        player.pause()
        assert player.is_paused() is True
        assert player.is_playing() is False

        player.seek(2.5)
        assert player.get_current_position() == 2.5

    player.stop()
    assert player.is_playing() is False
    assert player.is_paused() is False


def test_media_type_detection() -> None:
    """التحقق من التعرف التلقائي على ملفات الفيديو والصوت."""
    assert is_video_file("movie.mp4") is True
    assert is_video_file("clip.mkv") is True
    assert is_video_file("song.mp3") is False

    assert is_audio_file("song.mp3") is True
    assert is_audio_file("music.flac") is True
    assert is_audio_file("video.mp4") is False


def test_cut_video_and_gif(tmp_path: Path) -> None:
    """اختبار تقطيع الفيديو وإنشاء صورة متحركة GIF."""
    ffmpeg_exe = _get_ffmpeg_tool("ffmpeg")
    if not ffmpeg_exe:
        pytest.skip("FFmpeg غير متوفر")

    # إنشاء ملف فيديو تجريبي قصير عبر FFmpeg
    test_video = tmp_path / "sample.mp4"
    cmd_gen = [
        ffmpeg_exe, "-y",
        "-f", "lavfi", "-i", "testsrc=duration=3:size=320x240:rate=15",
        "-f", "lavfi", "-i", "sine=frequency=1000:duration=3",
        "-c:v", "libx264", "-c:a", "aac",
        str(test_video),
    ]
    res = subprocess.run(cmd_gen, capture_output=True)
    assert res.returncode == 0
    assert test_video.exists()

    # 1. اختبار القص السريع للفيديو (Fast Lossless)
    cut_mp4 = tmp_path / "cut_output.mp4"
    ok = cut_video(
        input_path=str(test_video),
        output_path=str(cut_mp4),
        start_sec=1.0,
        end_sec=2.5,
        mode="fast",
        fmt="mp4",
    )
    assert ok is True
    assert cut_mp4.exists()

    # 2. اختبار تصدير مقطع الفيديو كصورة GIF
    cut_gif = tmp_path / "animation.gif"
    ok_gif = cut_video(
        input_path=str(test_video),
        output_path=str(cut_gif),
        start_sec=0.5,
        end_sec=1.5,
        mode="accurate",
        fmt="gif",
    )
    assert ok_gif is True
    assert cut_gif.exists()
    assert cut_gif.stat().st_size > 0
