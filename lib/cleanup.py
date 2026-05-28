"""Remove temporary download files."""
from pathlib import Path


def cleanup_temp_file(path: Path | None) -> None:
    if path is None:
        return
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


def cleanup_temp_glob(temp_dir: Path, pattern: str) -> None:
    if not temp_dir.exists():
        return
    for p in temp_dir.glob(pattern):
        try:
            p.unlink()
        except OSError:
            pass
