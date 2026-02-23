from __future__ import annotations

from pathlib import Path

import httpx
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from podcast_dl.utils.console import get_console

console = get_console()


def download_episode(url: str, dest: Path, skip_existing: bool = True) -> Path:
    """Download audio to dest with a progress bar. Returns dest path."""
    if skip_existing and dest.exists() and dest.stat().st_size > 0:
        console.print(f"  [dim]Skipping (already exists):[/dim] {dest.name}")
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")

    with httpx.stream("GET", url, follow_redirects=True, timeout=60.0) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0)) or None

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
        ) as progress:
            task = progress.add_task(f"  Downloading {dest.name}", total=total)
            with tmp.open("wb") as f:
                for chunk in resp.iter_bytes(chunk_size=65536):
                    f.write(chunk)
                    progress.update(task, advance=len(chunk))

    tmp.rename(dest)
    console.print(f"  [green]Downloaded:[/green] {dest}")
    return dest
