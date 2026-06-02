# AI字幕生成工具 / AI Subtitle Generator Tool

Windows real-time subtitle tool for Chinese and English audio.

The app listens to system playback audio through Windows loopback capture, recognizes speech locally with `faster-whisper`, and shows one-line subtitles in an always-on-top overlay. It does not call DeepSeek or any online translation service in the current build.

## Features

- Local Chinese and English speech recognition with `faster-whisper`
- Default system-audio loopback capture for apps, browser tabs, videos, meetings, and games
- Microphone capture as an optional fallback
- One-line always-on-top subtitle overlay
- Simplified Chinese output for Chinese speech
- Desktop control panel for pause, overlay visibility, config, logs, and UI language
- Draggable subtitle window that keeps the user's chosen position

## Quick Start

```powershell
cd D:\ai-subtitle-win
.\run.ps1
```

The first run installs Python dependencies and may download the selected Whisper model. After startup, the PowerShell window closes and the desktop control panel stays open.

For the default real-time test, keep this setting in `config.toml`:

```toml
[speech]
model_size = "base"
beam_size = 1
compute_type = "int8"
cpu_threads = 4
allowed_languages = "zh,en"
min_language_probability = 0.45
no_speech_threshold = 0.6
```

Use `model_size = "tiny"` if speed matters most and the tiny model has downloaded successfully. The app records audio continuously in the background and keeps only the newest chunks, so it prefers staying close to real time over processing every old chunk.

## Controls

- `Esc`: quit
- `Ctrl+L`: list audio devices in the terminal
- `Ctrl+M`: pause or resume listening
- Drag the subtitle window with the left mouse button

## Config

Edit `config.toml`:

- `source = "loopback"` captures audio currently played by the computer.
- `source = "microphone"` captures microphone audio.
- `chunk_seconds = 0.6` controls recognition batch length. Lower values can feel faster but may reduce accuracy.
- `silence_rms = 0.02` filters background noise before recognition.
- `language = "auto"` detects Chinese or English automatically. Set `zh` or `en` if you know the source language.
- `model_size = "base"` is the default balance. Use `tiny` for speed if the model downloads successfully.
- `allowed_languages = "zh,en"` suppresses accidental non-Chinese/non-English output from background noise.
- `cpu_threads = 4` controls CPU decoding threads.

Edit `.env` only for UI language:

```env
UI_LANGUAGE=bilingual
```

Supported values are `zh`, `en`, and `bilingual`.

## Notes

- Whisper does not need a VPN after the model is already downloaded. The first model download uses Hugging Face and may depend on your network environment.
- No API key is required in the current build.
- Real-time speed depends heavily on CPU/GPU performance and selected Whisper model size.
- Runtime logs are written to `logs\app.log`.

---

# 中文说明

这是一个 Windows 实时 AI 字幕生成工具。它默认监听电脑正在播放的声音，比如网页视频、播放器、会议软件、游戏或其他应用的声音，然后用本地 `faster-whisper` 把音频识别成字幕，显示在屏幕置顶字幕窗口中。

当前版本只做字幕识别，不做翻译，不需要 DeepSeek API Key。

## 主要功能

- 支持中文和英文语音识别
- 默认监听电脑系统播放声音，不是麦克风
- 支持麦克风作为备用输入
- 使用 `faster-whisper` 本地识别
- 中文结果强制转为简体中文
- 单行字幕显示，避免遮挡屏幕
- 字幕窗口可以拖动，拖动后不会自动回到居中位置
- 控制面板支持暂停、隐藏字幕、打开配置、查看日志、切换界面语言

## 快速开始

```powershell
cd D:\ai-subtitle-win
.\run.ps1
```

第一次运行会自动安装依赖，也可能会下载 Whisper 模型。启动后 PowerShell 窗口会自动关闭，只保留软件控制面板。

## 如何调速度和准确度

打开 `config.toml`：

```toml
[speech]
model_size = "base"
language = "auto"
beam_size = 1
compute_type = "int8"
cpu_threads = 4
allowed_languages = "zh,en"
min_language_probability = 0.45
no_speech_threshold = 0.6
```

- 当前默认是可用性和准确度优先：`model_size = "base"`。
- 想更快：可以把 `model_size` 改成 `"tiny"`，但第一次需要下载 tiny 模型。
- 想更准：把 `model_size` 改成 `"base"` 或 `"small"`，但加载和识别会更慢。
- 明确只有中文：把 `language` 改成 `"zh"`。
- 明确只有英文：把 `language` 改成 `"en"`。
- 防止噪声乱出其他语言：保持 `allowed_languages = "zh,en"`。

## 常用快捷键

- `Esc`：退出字幕工具
- `Ctrl+L`：在终端里列出可用音频设备
- `Ctrl+M`：暂停或继续监听
- 鼠标左键拖动字幕窗口：移动字幕位置

## 常见问题

### API Key 是必须的吗？

不是。当前版本不做翻译，只用本地 Whisper 识别字幕，所以不需要 API Key。

### Whisper 需要 VPN 吗？

运行识别本身不需要 VPN。第一次使用某个 Whisper 模型时，程序可能需要从 Hugging Face 下载模型；这一步是否顺畅取决于当前网络。模型下载好之后，后续就可以本地加载。

### 为什么默认抓系统声音？

这个工具主要用于给网页、视频、会议、游戏或其他应用生成实时字幕，所以默认使用 Windows loopback 捕获电脑正在播放的声音。如果你的设备不支持 loopback，可以在 `config.toml` 里把 `source` 改成 `microphone`。
