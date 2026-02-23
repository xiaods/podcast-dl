from __future__ import annotations

import click

from podcast_dl.commands.download import download
from podcast_dl.commands.run import run
from podcast_dl.commands.transcribe import transcribe


@click.group()
@click.version_option(package_name="podcast-dl")
def main() -> None:
    """podcast-dl: Download and transcribe podcasts to Chinese text.

    \b
    Examples:
      # Download + transcribe latest episode from RSS feed
      podcast-dl run https://feeds.example.com/podcast.rss

      # Download latest 3 episodes, output as SRT subtitles
      podcast-dl run https://feeds.example.com/podcast.rss --latest 3 --format srt

      # Transcribe a local audio file
      podcast-dl transcribe episode.mp3

      # Download only (no transcription)
      podcast-dl download https://feeds.example.com/podcast.rss --latest 5
    """


main.add_command(run)
main.add_command(download)
main.add_command(transcribe)
