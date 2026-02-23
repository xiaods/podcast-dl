from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn, TimeRemainingColumn

from podcast_dl.utils.console import get_console

console = get_console()

MODEL_SIZES = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class TranscriptResult:
    language: str
    segments: list[TranscriptSegment]

    def as_text(self) -> str:
        return "\n".join(seg.text.strip() for seg in self.segments if seg.text.strip())

    def as_srt(self) -> str:
        lines = []
        for i, seg in enumerate(self.segments, 1):
            lines.append(str(i))
            lines.append(f"{_srt_time(seg.start)} --> {_srt_time(seg.end)}")
            lines.append(seg.text.strip())
            lines.append("")
        return "\n".join(lines)

    def as_json(self) -> str:
        data = [
            {"start": round(seg.start, 3), "end": round(seg.end, 3), "text": seg.text.strip()}
            for seg in self.segments
        ]
        return json.dumps(data, ensure_ascii=False, indent=2)


def transcribe_file(
    audio_path: Path,
    model_size: str = "large-v3",
    language: str | None = None,
    compute_type: str | None = None,
) -> TranscriptResult:
    """Transcribe audio using faster-whisper."""
    try:
        import ctranslate2
        from faster_whisper import WhisperModel
    except ImportError:
        raise RuntimeError(
            "faster-whisper is not installed. Run: pip install faster-whisper"
        )

    # Auto-detect device and compute type
    device = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
    if compute_type is None:
        compute_type = "int8_float16" if device == "cuda" else "int8"

    console.log(
        f"Loading Whisper [bold]{model_size}[/bold] "
        f"(device={device}, compute={compute_type})"
    )

    from podcast_dl.utils.paths import get_cache_dir

    with console.status(f"  Loading model [bold]{model_size}[/bold]..."):
        model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
            download_root=str(get_cache_dir()),
        )

    segments_iter, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
    )

    console.log(
        f"Detected language: [cyan]{info.language}[/cyan] "
        f"({info.language_probability:.0%} confidence) | "
        f"Duration: {_fmt_duration(info.duration)}"
    )

    total_secs = info.duration
    segments = []
    with Progress(
        TextColumn("  [progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Transcribing", total=total_secs)
        for seg in segments_iter:
            segments.append(TranscriptSegment(start=seg.start, end=seg.end, text=seg.text))
            progress.update(task, completed=seg.end)
    return TranscriptResult(language=info.language, segments=segments)


def write_transcript(result: TranscriptResult, base_path: Path, fmt: str) -> None:
    """Write transcript to file(s). fmt can be txt, srt, json, or all."""
    formats = ["txt", "srt", "json"] if fmt == "all" else [fmt]
    for f in formats:
        path = base_path.with_suffix(f".{f}")
        if f == "txt":
            path.write_text(result.as_text(), encoding="utf-8")
        elif f == "srt":
            path.write_text(result.as_srt(), encoding="utf-8")
        elif f == "json":
            path.write_text(result.as_json(), encoding="utf-8")
        console.print(f"  [green]Saved:[/green] {path}")


def _srt_time(secs: float) -> str:
    h = int(secs // 3600)
    m = int((secs % 3600) // 60)
    s = int(secs % 60)
    ms = int((secs - int(secs)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _fmt_duration(secs: float) -> str:
    h = int(secs // 3600)
    m = int((secs % 3600) // 60)
    s = int(secs % 60)
    if h:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"
