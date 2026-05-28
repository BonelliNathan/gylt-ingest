"""Obsidian RAW note template for imported content."""
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _escape_yaml(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_raw_note(
    *,
    platform: str,
    title: str,
    source: str,
    transcript: str,
    tags: list[str],
    video_id: str | None = None,
) -> str:
    imported_at = _now_iso()
    tags_yaml = ", ".join(tags)
    video_id_line = f'video_id: "{video_id}"\n' if video_id else ""

    frontmatter = f"""---
type: imported_content
platform: {platform}
title: "{_escape_yaml(title)}"
source: "{_escape_yaml(source)}"
{video_id_line}imported_at: "{imported_at}"
status: raw
tags: [{tags_yaml}]
---

# {title}

**Source:** {source}

## Transcript

{transcript.strip()}

## AI Processing


## Related Concepts


## Actionable Ideas

"""
    return frontmatter
