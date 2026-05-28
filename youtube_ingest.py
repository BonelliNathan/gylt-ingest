#!/usr/bin/env python3
"""Ingest YouTube playlist → RAW Obsidian notes in Inbox/Youtube."""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import yt_dlp  # noqa: E402

from config import (  # noqa: E402
    INBOX_YOUTUBE,
    PLAYLIST_URL,
    STATE_FILE,
    TEMP_DIR,
)
from lib.markdown import build_raw_note  # noqa: E402
from lib.state import (  # noqa: E402
    is_processed,
    load_state,
    mark_processed,
    save_state,
    update_title_if_changed,
    youtube_key,
)
from lib.transcript import get_youtube_transcript  # noqa: E402


def list_playlist_videos(playlist_url: str) -> list[dict]:
    opts = {
        "extract_flat": "in_playlist",
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
    entries = info.get("entries") or []
    videos = []
    for entry in entries:
        if not entry:
            continue
        vid = entry.get("id")
        if not vid:
            continue
        videos.append(
            {
                "id": vid,
                "title": entry.get("title") or vid,
                "url": entry.get("url") or f"https://www.youtube.com/watch?v={vid}",
            }
        )
    return videos


def main() -> int:
    INBOX_YOUTUBE.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    state = load_state(STATE_FILE)
    ok = skip = err = title_updates = 0

    try:
        videos = list_playlist_videos(PLAYLIST_URL)
    except Exception as e:
        print(f"[FATAL] Playlist fetch failed: {e}")
        return 1

    for video in videos:
        video_id = video["id"]
        title = video["title"]
        url = video["url"]
        key = youtube_key(video_id)
        note_path = INBOX_YOUTUBE / f"{video_id}.md"

        if is_processed(state, key):
            if update_title_if_changed(state, key, title, note_path):
                title_updates += 1
                print(f"[TITLE] {title}")
            else:
                skip += 1
            continue

        try:
            transcript, method = get_youtube_transcript(video_id, TEMP_DIR)
            content = build_raw_note(
                platform="youtube",
                title=title,
                source=url,
                transcript=transcript,
                tags=["youtube", "imported", "raw"],
                video_id=video_id,
            )
            note_path.write_text(content, encoding="utf-8")
            mark_processed(
                state,
                key,
                title=title,
                source=url,
                method=method,
                platform="youtube",
                content_id=video_id,
            )
            ok += 1
            print(f"[OK] {title} ({method})")
        except Exception as e:
            err += 1
            print(f"[ERROR] {title}: {e}")

    save_state(state, STATE_FILE)
    print(f"\nDone: {ok} new, {skip} skipped, {title_updates} title updates, {err} errors")
    return 0 if err == 0 else 0  # item errors don't fail the batch


if __name__ == "__main__":
    raise SystemExit(main())
