#!/usr/bin/env python3
"""
Fetch Instagram URLs from a Telegram chat via Telethon (user account API).

Requires one-time login: ./venv/bin/python telegram_login.py
Credentials: 10 - Scripts/.env (see .env.example) — never commit .env or session files.
"""
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config import (  # noqa: E402
    INSTAGRAM_LINKS_FILE,
    TELEGRAM_DEFAULT_CHAT,
    TELEGRAM_MESSAGE_FILTER,
    TELEGRAM_MESSAGE_LIMIT,
    TELEGRAM_SESSION_DIR,
    TELEGRAM_SYNC_FILE,
)
from lib.env_config import load_dotenv  # noqa: E402
from lib.instagram_urls import append_new_links, extract_instagram_urls  # noqa: E402


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing {name} — copy .env.example to .env and fill api_id/api_hash "
            f"(from https://my.telegram.org/apps)"
        )
    return value


def load_sync_state() -> dict[str, Any]:
    if not TELEGRAM_SYNC_FILE.exists():
        return {"chats": {}}
    with TELEGRAM_SYNC_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def save_sync_state(state: dict[str, Any]) -> None:
    TELEGRAM_SYNC_FILE.parent.mkdir(parents=True, exist_ok=True)
    with TELEGRAM_SYNC_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def message_text(msg) -> str:
    return (getattr(msg, "message", None) or getattr(msg, "text", None) or "") or ""


async def _resolve_entity(client, chat: str):
    """Resolve chat by id, username, title, or dialog scan (groups/saved)."""
    chat = chat.strip()
    if chat.lower() in ("me", "saved", "saved messages"):
        return await client.get_entity("me")

    # Numeric id (with or without -100 prefix)
    raw = chat.lstrip("@")
    if raw.lstrip("-").isdigit():
        target = int(raw)
        async for dialog in client.iter_dialogs():
            if dialog.entity.id == target or dialog.entity.id == abs(target):
                return dialog.entity
        # Supergroup: try -100{id} form
        if target > 0:
            full = int(f"-100{target}")
            async for dialog in client.iter_dialogs():
                if dialog.entity.id == full:
                    return dialog.entity

    try:
        return await client.get_entity(chat)
    except Exception:
        pass

    # Match by exact dialog title (e.g. "SecondBrain")
    async for dialog in client.iter_dialogs():
        if (dialog.name or "").lower() == chat.lower():
            return dialog.entity

    raise ValueError(f"Cannot resolve Telegram chat: {chat!r}")


def passes_filter(text: str, filter_substring: str) -> bool:
    if not filter_substring:
        return True
    return filter_substring.lower() in text.lower()


async def fetch_links(
    *,
    chat: str,
    limit: int,
    message_filter: str,
    incremental: bool,
) -> tuple[list[str], int, str]:
    from telethon import TelegramClient

    api_id = int(_require_env("TELEGRAM_API_ID"))
    api_hash = _require_env("TELEGRAM_API_HASH")
    session_name = os.environ.get("TELEGRAM_SESSION_NAME", "gylt_capture").strip()

    TELEGRAM_SESSION_DIR.mkdir(parents=True, exist_ok=True)
    session_path = str(TELEGRAM_SESSION_DIR / session_name)

    client = TelegramClient(session_path, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        await client.disconnect()
        raise RuntimeError(
            "Telegram session not authorized. Run: ./venv/bin/python telegram_login.py"
        )

    try:
        entity = await _resolve_entity(client, chat)
        chat_key = str(getattr(entity, "id", chat))
        sync = load_sync_state()
        chat_sync = sync.get("chats", {}).get(chat_key, {})
        min_id = int(chat_sync.get("last_message_id", 0)) if incremental else 0

        messages = await client.get_messages(entity, limit=limit, min_id=min_id)
        if not messages:
            label = getattr(entity, "title", None) or getattr(entity, "username", chat)
            return [], 0, str(label)

        found_urls: list[str] = []
        max_id = min_id
        for msg in messages:
            if not msg or not msg.id:
                continue
            max_id = max(max_id, msg.id)
            text = message_text(msg)
            if not passes_filter(text, message_filter):
                continue
            for url in extract_instagram_urls(text):
                if url not in found_urls:
                    found_urls.append(url)

        if incremental and max_id > min_id:
            sync.setdefault("chats", {})[chat_key] = {
                "last_message_id": max_id,
                "chat_label": getattr(entity, "title", None)
                or getattr(entity, "username", chat),
            }
            save_sync_state(sync)

        label = getattr(entity, "title", None) or getattr(entity, "username", chat)
        return found_urls, len(messages), str(label)
    finally:
        await client.disconnect()


def main() -> int:
    load_dotenv(BASE_DIR)

    chat = os.environ.get("TELEGRAM_CHAT", TELEGRAM_DEFAULT_CHAT).strip()
    limit = int(os.environ.get("TELEGRAM_MESSAGE_LIMIT", str(TELEGRAM_MESSAGE_LIMIT)))
    message_filter = os.environ.get("TELEGRAM_MESSAGE_FILTER", TELEGRAM_MESSAGE_FILTER)
    incremental = os.environ.get("TELEGRAM_INCREMENTAL", "1").strip() not in (
        "0",
        "false",
        "False",
    )

    if not os.environ.get("TELEGRAM_API_ID") or not os.environ.get("TELEGRAM_API_HASH"):
        print("[SKIP] Telegram not configured (.env missing TELEGRAM_API_ID/HASH)")
        return 0

    try:
        urls, msg_count, label = asyncio.run(
            fetch_links(
                chat=chat,
                limit=limit,
                message_filter=message_filter,
                incremental=incremental,
            )
        )
    except Exception as e:
        print(f"[ERROR] Telegram fetch failed: {e}")
        return 1

    if not urls:
        print(f"[OK] Telegram @{label}: {msg_count} messages scanned, 0 Instagram links")
        return 0

    added = append_new_links(INSTAGRAM_LINKS_FILE, urls)
    print(
        f"[OK] Telegram ({label}): {msg_count} messages, "
        f"{len(urls)} link(s) found, {len(added)} new in instagram_links.txt"
    )
    for url in added:
        print(f"  + {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
