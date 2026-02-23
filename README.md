# podcast-dl

A CLI tool to download podcast episodes from RSS feeds and transcribe them to text using [faster-whisper](https://github.com/SYSTRAN/faster-whisper). Supports Chinese and 90+ other languages.

[中文文档](README_CN.md)

## Features

- Download podcast audio from RSS feeds or direct URLs
- Transcribe speech to text with automatic language detection
- VAD filtering — silently skips music, ads, and silence
- Streaming download with real-time progress bar
- Resume-safe: skips already-downloaded files
- Output formats: `txt`, `srt`, `json`, or all at once
- CPU / GPU auto-detection, works on Apple Silicon and x86 Macs

## Installation

Requires Python 3.10–3.12. Recommended to use [uv](https://github.com/astral-sh/uv) for isolated environments (like `npx` for Python).

> **Note**: `onnxruntime` (a `faster-whisper` dependency) does not yet have wheels for Python 3.13 on macOS x86_64. Specify `--python 3.11` to avoid resolution errors.

### Option 1: Global tool install (recommended)

Installs into an isolated environment, available system-wide:

```bash
uv tool install --python 3.11 .
```

Uninstall:

```bash
uv tool uninstall podcast-dl
```

### Option 2: Run without installing (like npx)

```bash
uvx --python 3.11 --from . podcast-dl run https://feeds.example.com/podcast.rss
```

### Option 3: Project virtual environment (for development)

```bash
uv sync --python 3.11
uv run podcast-dl --help
```

### Option 4: pip

```bash
pip install -e .
```

> Whisper model weights are downloaded automatically on first use and cached in `~/Library/Caches/podcast-dl/` (macOS) or `~/.cache/podcast-dl/` (Linux).

## Usage

### Download + transcribe (most common)

```bash
# Download and transcribe the latest episode
podcast-dl run https://feeds.example.com/podcast.rss

# Latest 3 episodes, Chinese, SRT output
podcast-dl run https://feeds.example.com/podcast.rss --latest 3 --language zh --format srt

# Use a smaller model (faster)
podcast-dl run https://feeds.example.com/podcast.rss --model medium

# Direct audio URL (not RSS)
podcast-dl run https://example.com/episode.mp3 --direct

# Custom output directory
podcast-dl run https://feeds.example.com/podcast.rss --output ~/podcasts/
```

### Download only

```bash
# Download all episodes
podcast-dl download https://feeds.example.com/podcast.rss

# Latest 5 episodes only
podcast-dl download https://feeds.example.com/podcast.rss --latest 5

# List episodes without downloading
podcast-dl download https://feeds.example.com/podcast.rss --list

# Filter by keyword
podcast-dl download https://feeds.example.com/podcast.rss --filter "AI"
```

### Transcribe a local file

```bash
# Auto-detect language
podcast-dl transcribe episode.mp3

# Force Chinese, SRT output
podcast-dl transcribe episode.mp3 --language zh --format srt

# All output formats at once
podcast-dl transcribe episode.mp3 --format all

# Best accuracy
podcast-dl transcribe episode.mp3 --model large-v3
```

## Options

### `podcast-dl run`

| Option | Default | Description |
|---|---|---|
| `--latest N` | `1` | Number of latest episodes to process (0 = all) |
| `--direct` | — | Treat URL as a direct audio link, not RSS |
| `-o, --output PATH` | `~/Downloads/podcast-dl/` | Output directory |
| `-m, --model` | `large-v3` | Whisper model size |
| `-l, --language` | auto-detect | Language code, e.g. `zh`, `en`, `ja` |
| `--format` | `txt` | Output format: `txt` / `srt` / `json` / `all` |
| `--compute-type` | auto | Precision: `int8`, `float16`, etc. |
| `--skip-existing` | on | Skip files that already exist |

### Model reference

| Model | Size | Speed | Accuracy |
|---|---|---|---|
| `tiny` | ~75 MB | Fastest | Low |
| `base` | ~145 MB | Very fast | Fair |
| `small` | ~465 MB | Fast | Good |
| `medium` | ~1.5 GB | Moderate | Better |
| `large-v2` | ~3 GB | Slow | Great |
| `large-v3` | ~3 GB | Slow | Best (default) |

> On CPU-only machines, `medium` offers the best balance of speed and accuracy.

## Output

Files are saved to `~/Downloads/podcast-dl/` by default, named after the episode title:

```
~/Downloads/podcast-dl/
├── My Podcast Episode 42.mp3      # audio
├── My Podcast Episode 42.txt      # plain text transcript
├── My Podcast Episode 42.srt      # subtitle file
└── My Podcast Episode 42.json     # transcript with timestamps
```

## Dependencies

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — speech-to-text engine
- [feedparser](https://github.com/kurtmckee/feedparser) — RSS feed parsing
- [httpx](https://github.com/encode/httpx) — streaming audio download
- [click](https://github.com/pallets/click) — CLI framework
- [rich](https://github.com/Textualize/rich) — terminal output
- [platformdirs](https://github.com/platformdirs/platformdirs) — cross-platform cache paths

## License

MIT License. See [LICENSE](LICENSE).
