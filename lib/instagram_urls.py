"""Extract and merge Instagram URLs from text."""
import re
from pathlib import Path

from lib.state import normalize_instagram_url

# reel, post, TV, stories highlights in links
INSTAGRAM_URL_PATTERN = re.compile(
    r"https?://(?:www\.)?instagram\.com/(?:reel|reels|p|tv)/[A-Za-z0-9_-]+/?",
    re.IGNORECASE,
)


def extract_instagram_urls(text: str) -> list[str]:
    """Return normalized unique Instagram URLs found in text (order preserved)."""
    seen: set[str] = set()
    urls: list[str] = []
    for match in INSTAGRAM_URL_PATTERN.finditer(text or ""):
        normalized = normalize_instagram_url(match.group(0))
        if normalized not in seen:
            seen.add(normalized)
            urls.append(normalized)
    return urls


def read_link_file(path: Path) -> list[str]:
    if not path.exists():
        return []
    urls: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for url in extract_instagram_urls(line):
            if url not in urls:
                urls.append(url)
        if line.startswith("http") and "instagram.com" in line and line not in urls:
            normalized = normalize_instagram_url(line)
            if normalized not in urls:
                urls.append(normalized)
    return urls


def append_new_links(path: Path, new_urls: list[str]) -> list[str]:
    """Append URLs not already in file. Returns list of URLs actually added."""
    existing = set(read_link_file(path))
    added: list[str] = []
    lines_to_append: list[str] = []
    for url in new_urls:
        if url in existing:
            continue
        existing.add(url)
        added.append(url)
        lines_to_append.append(url)

    if lines_to_append:
        path.parent.mkdir(parents=True, exist_ok=True)
        prefix = ""
        if path.exists() and path.stat().st_size > 0:
            prefix = "\n"
        with path.open("a", encoding="utf-8") as f:
            f.write(prefix + "\n".join(lines_to_append) + "\n")
    return added
