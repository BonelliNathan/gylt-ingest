"""Idempotent state tracking — keys never depend on title."""
import json
import re
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

from config import STATE_FILE


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_state(path: Path = STATE_FILE) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict[str, Any], path: Path = STATE_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def youtube_key(video_id: str) -> str:
    return f"youtube_{video_id}"


def instagram_key(url_hash: str) -> str:
    return f"instagram_{url_hash}"


def normalize_instagram_url(url: str) -> str:
    """Strip tracking params; keep canonical path."""
    url = url.strip()
    parsed = urlparse(url)
    # Remove query and fragment (utm_, igsh, etc.)
    clean = urlunparse((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", "", ""))
    return clean


def instagram_url_hash(url: str) -> str:
    """Stable 12-char hash from normalized URL."""
    normalized = normalize_instagram_url(url)
    return sha256(normalized.encode("utf-8")).hexdigest()[:12]


def is_processed(state: dict[str, Any], key: str) -> bool:
    return key in state


def mark_processed(
    state: dict[str, Any],
    key: str,
    *,
    title: str,
    source: str,
    method: str,
    platform: str,
    content_id: str,
) -> None:
    state[key] = {
        "title": title,
        "source": source,
        "processed_at": _now_iso(),
        "method": method,
        "platform": platform,
        "content_id": content_id,
    }


def update_title_if_changed(
    state: dict[str, Any],
    key: str,
    new_title: str,
    inbox_path: Path,
) -> bool:
    """Update title metadata without re-ingestion. Returns True if title changed."""
    entry = state.get(key)
    if not entry:
        return False
    old_title = entry.get("title", "")
    if old_title == new_title:
        return False
    entry["title"] = new_title
    entry["title_updated_at"] = _now_iso()
    if inbox_path.exists():
        _patch_note_title(inbox_path, new_title)
    return True


def _patch_note_title(note_path: Path, new_title: str) -> None:
    text = note_path.read_text(encoding="utf-8")
    # Update frontmatter title: line
    if re.search(r"^title:\s*.+$", text, re.MULTILINE):
        text = re.sub(
            r"^title:\s*.+$",
            f'title: "{_escape_yaml(new_title)}"',
            text,
            count=1,
            flags=re.MULTILINE,
        )
    # Update H1
    text = re.sub(r"^# .+$", f"# {new_title}", text, count=1, flags=re.MULTILINE)
    note_path.write_text(text, encoding="utf-8")


def _escape_yaml(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def inbox_path_for_key(
    key: str,
    *,
    youtube_dir: Path,
    instagram_dir: Path,
) -> Path | None:
    if key.startswith("youtube_"):
        vid = key.removeprefix("youtube_")
        return youtube_dir / f"{vid}.md"
    if key.startswith("instagram_"):
        h = key.removeprefix("instagram_")
        return instagram_dir / f"{h}.md"
    return None
