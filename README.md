# podcast-dl

一个命令行工具，自动下载 Podcast 音频并转录为文字（支持中文）。

基于 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 实现语音识别，支持 RSS 订阅源批量下载，输出 TXT / SRT / JSON 多种格式。

## 功能特性

- 从 RSS 订阅源或直链 URL 下载 Podcast 音频
- 使用 Whisper 模型将语音转录为文字，原生支持中文
- 自动检测语言，无需手动指定
- VAD 静音过滤，自动跳过片头音乐、广告和静音段
- 流式下载，带实时进度条
- 支持断点续传（已下载文件不重复下载）
- 输出格式：TXT（纯文本）、SRT（字幕）、JSON（含时间戳）
- CPU / GPU 自动适配，M 系列 Mac 可直接运行

## 安装

推荐使用 [uv](https://github.com/astral-sh/uv) 管理隔离的 Python 环境，体验类似 `npx`，无需手动创建虚拟环境。

> **注意**：`faster-whisper` 依赖的 `onnxruntime` 在 macOS x86_64 上目前仅支持 Python ≤ 3.12，安装时需指定 Python 版本。

### 方式一：全局工具安装（推荐）

安装到独立隔离环境，全局可用：

```bash
uv tool install --python 3.11 .
```

卸载：

```bash
uv tool uninstall podcast-dl
```

### 方式二：临时运行（无需安装）

类似 `npx`，用完即走，不污染环境：

```bash
uvx --python 3.11 --from . podcast-dl run https://feeds.example.com/podcast.rss
```

### 方式三：项目虚拟环境（开发用）

```bash
uv sync --python 3.11
uv run podcast-dl --help
```

### 传统方式（pip + Python 3.11）

```bash
pip install -e .
```

> 首次转录时会自动下载 Whisper 模型文件（模型缓存在 `~/.cache/podcast-dl/`）。

## 使用方法

### 下载并转录（最常用）

```bash
# 下载 RSS 最新一集并转录
podcast-dl run https://feeds.example.com/podcast.rss

# 下载最新 3 集，指定中文，输出 SRT 字幕
podcast-dl run https://feeds.example.com/podcast.rss --latest 3 --language zh --format srt

# 使用较小的模型（速度更快）
podcast-dl run https://feeds.example.com/podcast.rss --model medium

# 直接下载音频 URL（非 RSS）
podcast-dl run https://example.com/episode.mp3 --direct

# 指定输出目录
podcast-dl run https://feeds.example.com/podcast.rss --output ~/podcasts/
```

### 仅下载音频

```bash
# 下载全部集数
podcast-dl download https://feeds.example.com/podcast.rss

# 仅下载最新 5 集
podcast-dl download https://feeds.example.com/podcast.rss --latest 5

# 列出所有集数（不下载）
podcast-dl download https://feeds.example.com/podcast.rss --list

# 按关键词过滤集数
podcast-dl download https://feeds.example.com/podcast.rss --filter "AI"

# 下载直链音频
podcast-dl download https://example.com/episode.mp3 --direct
```

### 转录本地音频文件

```bash
# 转录本地文件（自动检测语言）
podcast-dl transcribe episode.mp3

# 指定中文，输出 SRT 字幕
podcast-dl transcribe episode.mp3 --language zh --format srt

# 输出所有格式（txt + srt + json）
podcast-dl transcribe episode.mp3 --format all

# 使用大模型获得更高精度
podcast-dl transcribe episode.mp3 --model large-v3
```

## 选项说明

### `podcast-dl run`

| 选项 | 默认值 | 说明 |
|---|---|---|
| `--latest N` | `1` | 处理最新 N 集（0 = 全部） |
| `--direct` | - | 将 URL 视为直链音频而非 RSS |
| `-o, --output PATH` | `~/Downloads/podcast-dl/` | 输出目录 |
| `-m, --model` | `large-v3` | Whisper 模型大小 |
| `-l, --language` | 自动检测 | 语言代码，如 `zh`、`en` |
| `--format` | `txt` | 输出格式：`txt` / `srt` / `json` / `all` |
| `--compute-type` | 自动 | 计算精度：`int8` / `float16` 等 |
| `--skip-existing` | 开启 | 跳过已存在的文件 |

### 模型选择参考

| 模型 | 磁盘大小 | 速度 | 精度 |
|---|---|---|---|
| `tiny` | ~75 MB | 最快 | 较低 |
| `base` | ~145 MB | 很快 | 一般 |
| `small` | ~465 MB | 快 | 较好 |
| `medium` | ~1.5 GB | 中等 | 好 |
| `large-v2` | ~3 GB | 慢 | 很好 |
| `large-v3` | ~3 GB | 慢 | 最好（默认） |

> CPU 用户建议使用 `medium` 模型以平衡速度和精度。

## 输出文件

转录结果默认保存在 `~/Downloads/podcast-dl/` 目录，文件名根据集数标题自动生成：

```
~/Downloads/podcast-dl/
├── My Podcast Episode 42.mp3      # 音频文件
├── My Podcast Episode 42.txt      # 纯文本转录
├── My Podcast Episode 42.srt      # SRT 字幕文件
└── My Podcast Episode 42.json     # 带时间戳的 JSON
```

## 依赖

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — 语音转文字引擎
- [feedparser](https://github.com/kurtmckee/feedparser) — RSS 订阅解析
- [httpx](https://github.com/encode/httpx) — 音频流式下载
- [click](https://github.com/pallets/click) — 命令行框架
- [rich](https://github.com/Textualize/rich) — 终端美化输出
- [platformdirs](https://github.com/platformdirs/platformdirs) — 跨平台路径管理

## 许可证

MIT License. 详见 [LICENSE](LICENSE) 文件。
