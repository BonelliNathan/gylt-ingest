#!/usr/bin/env python3
"""One-time interactive Telegram login (creates session file in telegram_session/)."""
import asyncio
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config import TELEGRAM_SESSION_DIR  # noqa: E402
from lib.env_config import load_dotenv  # noqa: E402


async def main() -> None:
    load_dotenv(BASE_DIR)
    api_id = os.environ.get("TELEGRAM_API_ID", "").strip()
    api_hash = os.environ.get("TELEGRAM_API_HASH", "").strip()
    if not api_id or not api_hash:
        print("Copy .env.example → .env and set TELEGRAM_API_ID / TELEGRAM_API_HASH")
        print("Create an app at https://my.telegram.org/apps")
        raise SystemExit(1)

    from telethon import TelegramClient

    session_name = os.environ.get("TELEGRAM_SESSION_NAME", "gylt_capture").strip()
    TELEGRAM_SESSION_DIR.mkdir(parents=True, exist_ok=True)
    session_path = str(TELEGRAM_SESSION_DIR / session_name)

    client = TelegramClient(session_path, int(api_id), api_hash)
    await client.start(
        phone=lambda: input("Phone (+33...): "),
        password=lambda: input("2FA password (or Enter if none): ") or None,
        code_callback=lambda: input("Code from Telegram: "),
    )
    me = await client.get_me()
    print(f"✓ Logged in as {me.first_name} (@{me.username}) — session: {session_path}.session")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
