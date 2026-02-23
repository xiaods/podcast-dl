from __future__ import annotations

from pathlib import Path

import click

from podcast_dl.core.transcriber import MODEL_SIZES, transcribe_file, write_transcript
from podcast_dl.utils.console import get_console

console = get_console()


@click.command("transcribe")
@click.argument("audio_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--model", "-m", default="large-v3", show_default=True,
    type=click.Choice(MODEL_SIZES), help="Whisper model size"
)
@click.option("--language", "-l", default=None, help="Language code (e.g. zh, en). Auto-detect if omitted.")
@click.option(
    "--format", "fmt", default="txt", show_default=True,
    type=click.Choice(["txt", "srt", "json", "all"]), help="Output format"
)
@click.option("--output", "-o", type=click.Path(), default=None, help="Output file base path (without extension)")
@click.option(
    "--compute-type", default=None,
    type=click.Choice(["int8", "int8_float16", "float16", "float32"]),
    help="Compute type (auto-detected if omitted)"
)
def transcribe(audio_file, model, language, fmt, output, compute_type):
    """Transcribe a local audio file to text."""
    base_path = Path(output) if output else audio_file.with_suffix("")

    result = transcribe_file(
        audio_file,
        model_size=model,
        language=language,
        compute_type=compute_type,
    )
    write_transcript(result, base_path, fmt)
