from __future__ import annotations

from pathlib import Path

import click

from podcast_dl.core import downloader, rss
from podcast_dl.utils.console import get_console
from podcast_dl.utils.paths import episode_audio_path, get_output_dir

console = get_console()


@click.command("download")
@click.argument("url")
@click.option("--latest", default=0, help="Download only the N latest episodes (0 = all)")
@click.option("--direct", is_flag=True, help="Treat URL as a direct audio URL (not RSS)")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output directory")
@click.option("--filter", "keyword", default=None, help="Only episodes matching this keyword")
@click.option("--list", "list_only", is_flag=True, help="List episodes without downloading")
@click.option("--skip-existing/--no-skip-existing", default=True, show_default=True)
def download(url, latest, direct, output, keyword, list_only, skip_existing):
    """Download podcast audio from an RSS feed or direct URL."""
    out_dir = Path(output) if output else get_output_dir()

    if direct:
        episodes = [rss.Episode(title="episode", url=url, published=None,
                                duration_secs=None, description="")]
    else:
        console.log(f"Fetching RSS feed: [blue]{url}[/blue]")
        episodes = rss.parse_feed(url)
        console.log(f"Found [bold]{len(episodes)}[/bold] episodes")

    if keyword:
        episodes = [ep for ep in episodes if keyword.lower() in ep.title.lower()]
        console.log(f"Filtered to [bold]{len(episodes)}[/bold] episodes matching '{keyword}'")

    if latest and latest > 0:
        episodes = episodes[:latest]

    if list_only:
        for i, ep in enumerate(episodes, 1):
            date = ep.published.strftime("%Y-%m-%d") if ep.published else "unknown date"
            console.print(f"  {i:3}. [{date}] {ep.title}")
        return

    for ep in episodes:
        console.rule(f"[yellow]{ep.title}[/yellow]")
        audio_path = episode_audio_path(out_dir, ep)
        downloader.download_episode(ep.url, audio_path, skip_existing=skip_existing)
