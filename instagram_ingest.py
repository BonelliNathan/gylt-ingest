#!/usr/bin/env python3
"""Ingest Instagram links → RAW Obsidian notes in Inbox/Instagram."""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config import (  # noqa: E402
    INSTAGRAM_LINKS_FILE,
    INBOX_INSTAGRAM,
    STATE_FILE,
    TEMP_DIR,
)
from lib.instagram_urls import read_link_file  # noqa: E402
from lib.markdown import build_raw_note  # noqa: E402
from lib.state import (  # noqa: E402
    instagram_key,
    instagram_url_hash,
    is_processed,
    load_state,
    mark_processed,
    normalize_instagram_url,
    save_state,
)
from lib.transcript import get_instagram_transcript  # noqa: E402


def main() -> int:
    INBOX_INSTAGRAM.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    state = load_state(STATE_FILE)
    links = read_link_file(INSTAGRAM_LINKS_FILE)
    ok = skip = err = 0

    if not links:
        print("No Instagram links in instagram_links.txt")
        save_state(state, STATE_FILE)
        return 0

    for raw_url in links:
        url = normalize_instagram_url(raw_url)
        url_hash = instagram_url_hash(url)
        key = instagram_key(url_hash)
        note_path = INBOX_INSTAGRAM / f"{url_hash}.md"
        title = f"Instagram {url_hash}"

        if is_processed(state, key):
            skip += 1
            continue

        try:
            transcript, method = get_instagram_transcript(url, url_hash, TEMP_DIR)
            content = build_raw_note(
                platform="instagram",
                title=title,
                source=url,
                transcript=transcript,
                tags=["instagram", "imported", "raw"],
            )
            note_path.write_text(content, encoding="utf-8")
            mark_processed(
                state,
                key,
                title=title,
                source=url,
                method=method,
                platform="instagram",
                content_id=url_hash,
            )
            ok += 1
            print(f"[OK] {url_hash} ({method})")
        except Exception as e:
            err += 1
            print(f"[ERROR] {url}: {e}")

    save_state(state, STATE_FILE)
    print(f"\nDone: {ok} new, {skip} skipped, {err} errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
