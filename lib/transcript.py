"""Transcript retrieval: YouTube API first, Whisper fallback."""
from pathlib import Path

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

from config import TEMP_DIR, TRANSCRIPT_LANGUAGES, WHISPER_MODEL
from lib.cleanup import cleanup_temp_file

_whisper_model = None


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        import whisper

        _whisper_model = whisper.load_model(WHISPER_MODEL)
    return _whisper_model


def _transcript_from_api(video_id: str) -> str | None:
    api = YouTubeTranscriptApi()
    for lang in TRANSCRIPT_LANGUAGES:
        try:
            fetched = api.fetch(video_id, languages=[lang])
            return " ".join(snippet.text for snippet in fetched)
        except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
            continue
        except Exception:
            continue
    try:
        fetched = api.fetch(video_id)
        return " ".join(snippet.text for snippet in fetched)
    except Exception:
        return None


def _download_youtube_audio(video_id: str, temp_dir: Path) -> Path | None:
    temp_dir.mkdir(parents=True, exist_ok=True)
    out_template = str(temp_dir / f"{video_id}.%(ext)s")
    opts = {
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }
        ],
    }
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    except Exception:
        return None
    candidates = list(temp_dir.glob(f"{video_id}.*"))
    return candidates[0] if candidates else None


def _download_media(url: str, prefix: str, temp_dir: Path) -> Path | None:
    temp_dir.mkdir(parents=True, exist_ok=True)
    out_template = str(temp_dir / f"{prefix}.%(ext)s")
    opts = {
        "outtmpl": out_template,
        "quiet": True,
        "no_warnings": True,
        "format": "best[ext=mp4]/best",
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    except Exception:
        return None
    candidates = sorted(temp_dir.glob(f"{prefix}.*"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def _transcribe_whisper(audio_path: Path) -> str:
    model = _get_whisper_model()
    result = model.transcribe(str(audio_path), fp16=False)
    return (result.get("text") or "").strip()


def get_youtube_transcript(video_id: str, temp_dir: Path = TEMP_DIR) -> tuple[str, str]:
    """
    Returns (transcript_text, method) where method is 'youtube_api' or 'whisper'.
    Raises on total failure.
    """
    text = _transcript_from_api(video_id)
    if text and text.strip():
        return text.strip(), "youtube_api"

    audio_path = None
    try:
        audio_path = _download_youtube_audio(video_id, temp_dir)
        if not audio_path or not audio_path.exists():
            raise RuntimeError("Audio download failed")
        text = _transcribe_whisper(audio_path)
        if not text.strip():
            raise RuntimeError("Whisper returned empty transcript")
        return text, "whisper"
    finally:
        cleanup_temp_file(audio_path)


def get_instagram_transcript(url: str, url_hash: str, temp_dir: Path = TEMP_DIR) -> tuple[str, str]:
    """Download via yt-dlp and transcribe with Whisper."""
    media_path = None
    try:
        media_path = _download_media(url, url_hash, temp_dir)
        if not media_path or not media_path.exists():
            raise RuntimeError("Media download failed")
        text = _transcribe_whisper(media_path)
        if not text.strip():
            raise RuntimeError("Whisper returned empty transcript")
        return text, "whisper"
    finally:
        cleanup_temp_file(media_path)
