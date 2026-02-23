from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime

import feedparser
import httpx


@dataclass
class Episode:
    title: str
    url: str
    published: datetime | None
    duration_secs: int | None
    description: str


def parse_feed(url: str) -> list[Episode]:
    """Parse an RSS feed and return episodes sorted newest-first.

    Uses httpx (with certifi) to fetch the feed content, avoiding
    SSL certificate issues with the system urllib on macOS.
    """
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=30.0)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
    except httpx.HTTPError as e:
        raise ValueError(f"Failed to fetch RSS feed: {e}") from e

    if feed.bozo and not feed.entries:
        raise ValueError(
            f"Failed to parse RSS feed: {url}\n"
            f"Reason: {feed.get('bozo_exception', 'unknown error')}"
        )

    episodes = []
    for entry in feed.entries:
        audio_url = _extract_audio_url(entry)
        if audio_url:
            episodes.append(
                Episode(
                    title=entry.get("title", "Unknown Episode"),
                    url=audio_url,
                    published=_parse_date(entry.get("published_parsed")),
                    duration_secs=_parse_duration(entry),
                    description=entry.get("summary", ""),
                )
            )
    return episodes


def _extract_audio_url(entry) -> str | None:
    for enc in entry.get("enclosures", []):
        mime = enc.get("type", "")
        if "audio" in mime or enc.get("href", "").endswith((".mp3", ".m4a", ".ogg", ".opus")):
            return enc.get("href") or enc.get("url")
    for media in entry.get("media_content", []):
        if "audio" in media.get("medium", "") or "audio" in media.get("type", ""):
            return media.get("url")
    return None


def _parse_date(parsed_time) -> datetime | None:
    if parsed_time is None:
        return None
    try:
        return datetime.fromtimestamp(time.mktime(parsed_time))
    except Exception:
        return None


def _parse_duration(entry) -> int | None:
    duration_str = entry.get("itunes_duration", "")
    if not duration_str:
        return None
    parts = str(duration_str).split(":")
    try:
        if len(parts) == 1:
            return int(parts[0])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except ValueError:
        return None
    return None
