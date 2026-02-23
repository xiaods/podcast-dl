import re
from pathlib import Path
from platformdirs import user_downloads_dir, user_cache_dir

APP_NAME = "podcast-dl"


def get_cache_dir() -> Path:
    """Whisper model weights cache directory."""
    return Path(user_cache_dir(APP_NAME))


def get_output_dir() -> Path:
    """Default output directory for audio and transcripts."""
    return Path(user_downloads_dir()) / APP_NAME


def episode_audio_path(base: Path, episode) -> Path:
    safe = _safe_filename(episode.title)
    suffix = episode.url.split("?")[0].rsplit(".", 1)[-1] or "mp3"
    if len(suffix) > 4 or not suffix.isalpha():
        suffix = "mp3"
    return base / f"{safe}.{suffix}"


def episode_transcript_path(base: Path, episode) -> Path:
    safe = _safe_filename(episode.title)
    return base / safe


def _safe_filename(name: str) -> str:
    return re.sub(r"[^\w\-_. ]", "_", name)[:120].strip()
