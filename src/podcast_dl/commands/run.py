from __future__ import annotations

from pathlib import Path

import click

from podcast_dl.core import downloader, rss
from podcast_dl.core.transcriber import MODEL_SIZES, transcribe_file, write_transcript
from podcast_dl.utils.console import get_console
from podcast_dl.utils.paths import episode_audio_path, episode_transcript_path, get_output_dir

console = get_console()


@click.command("run")
@click.argument("url")
@click.option("--latest", default=1, show_default=True, help="Number of latest episodes to process")
@click.option("--direct", is_flag=True, help="Treat URL as a direct audio URL (not RSS)")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output directory")
@click.option(
    "--model", "-m", default="large-v3", show_default=True,
    type=click.Choice(MODEL_SIZES), help="Whisper model size"
)
@click.option("--language", "-l", default=None, help="Language code (e.g. zh, en). Auto-detect if omitted.")
@click.option(
    "--format", "fmt", default="txt", show_default=True,
    type=click.Choice(["txt", "srt", "json", "all"]), help="Output format"
)
@click.option(
    "--compute-type", default=None,
    type=click.Choice(["int8", "int8_float16", "float16", "float32"]),
    help="Compute type (auto-detected if omitted)"
)
@click.option("--skip-existing/--no-skip-existing", default=True, show_default=True)
def run(url, latest, direct, output, model, language, fmt, compute_type, skip_existing):
    """Download and transcribe podcasts in one step (full pipeline)."""
    out_dir = Path(output) if output else get_output_dir()

    if direct:
        title = url.split("/")[-1].split("?")[0]
        episodes = [rss.Episode(title=title, url=url, published=None,
                                duration_secs=None, description="")]
    else:
        console.log(f"Fetching RSS feed: [blue]{url}[/blue]")
        episodes = rss.parse_feed(url)
        episodes = episodes[:latest]
        console.log(f"Processing [bold]{len(episodes)}[/bold] episode(s)")

    for ep in episodes:
        console.rule(f"[yellow]{ep.title}[/yellow]")

        audio_path = episode_audio_path(out_dir, ep)
        downloader.download_episode(ep.url, audio_path, skip_existing=skip_existing)

        result = transcribe_file(
            audio_path,
            model_size=model,
            language=language,
            compute_type=compute_type,
        )

        transcript_base = episode_transcript_path(out_dir, ep)
        write_transcript(result, transcript_base, fmt)

    console.print(f"\n[bold green]Done![/bold green] Output in: {out_dir}")
