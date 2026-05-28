"""Configuration for content ingestion pipeline."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

PLAYLIST_URL = (
    "https://youtube.com/playlist?list=PLW31bEuRCQDnnC33X3MDRPB61RXBJf2bO&si=ocnmb9YWjzjvh1E8"
)

WHISPER_MODEL = "tiny"  # tiny | base — speed over fidelity; /today completes via web search

STATE_FILE = BASE_DIR / "processed_videos.json"
INSTAGRAM_LINKS_FILE = BASE_DIR / "instagram_links.txt"
TEMP_DIR = BASE_DIR / "temp"
INBOX_YOUTUBE = BASE_DIR / "Inbox" / "Youtube"
INBOX_INSTAGRAM = BASE_DIR / "Inbox" / "Instagram"
INBOX_ARCHIVED = BASE_DIR / "Inbox" / "_archived"

TRANSCRIPT_LANGUAGES = ("fr", "en", "fr-FR", "en-US")

# Telegram → instagram_links (optional; credentials in .env, see .env.example)
TELEGRAM_SESSION_DIR = BASE_DIR / "telegram_session"
TELEGRAM_SYNC_FILE = BASE_DIR / "telegram_sync.json"
TELEGRAM_DEFAULT_CHAT = "me"  # Saved Messages; or @user, numeric id, chat title
TELEGRAM_MESSAGE_LIMIT = 20
# If set, only messages containing this substring (e.g. "#gylt") are scanned
TELEGRAM_MESSAGE_FILTER = ""
