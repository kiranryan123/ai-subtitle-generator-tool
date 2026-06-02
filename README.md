# AI字幕生成工具 / AI Subtitle Generator Tool

Windows real-time AI subtitle MVP for Chinese and English audio.

This prototype shows live captions in a transparent always-on-top overlay. By default it listens to Windows system playback audio through loopback capture, so it is aimed at subtitles for browser tabs, media players, meetings, games, and other apps. Microphone capture is available as a fallback.

## Features

- Chinese and English speech recognition
- Always-on-top transparent subtitle overlay
- Desktop control panel for status, pause, overlay visibility, config, logs, and API key editing
- System-audio loopback input by default
- Microphone fallback input
- DeepSeek V4 Flash subtitle translation
- Simple keyboard controls
- Local transcription through `faster-whisper`

## Quick Start

```powershell
cd D:\ai-subtitle-win
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and fill DEEPSEEK_API_KEY
python -m ai_subtitle_win
```

The first run downloads the selected Whisper model. For a small and fast first test, keep `model_size = "base"` in `config.toml`.

For normal use, run:

```powershell
cd D:\ai-subtitle-win
.\run.ps1
```

`run.ps1` installs missing dependencies, creates `.env` if needed, asks for `DEEPSEEK_API_KEY` when it is missing, starts the subtitle app through `pythonw.exe`, and then lets the PowerShell window close.

After startup, the app opens a desktop control panel. The subtitle overlay stays on top of the screen, while the control panel lets you pause listening, hide/show subtitles, open `config.toml`, view `logs\app.log`, and edit `.env`.

To replace an existing DeepSeek API key:

```powershell
cd D:\ai-subtitle-win
.\run.ps1 -UpdateApiKey
```

## Controls

- `Esc`: quit
- `Ctrl+L`: list audio devices in the terminal
- `Ctrl+M`: toggle mute/pause listening
- Drag the subtitle window by holding the left mouse button

## Config

Edit `config.toml`:

- `source = "loopback"` captions app, webpage, meeting, video, and game audio played by the computer. It will not silently fall back to the microphone. If you want microphone captions, set `source = "microphone"`.
- `chunk_seconds = 1.0` controls responsiveness. Lower values feel faster but increase CPU usage and translation calls.
- `language = "auto"` detects Chinese or English automatically.
- `model_size = "base"` is a good MVP choice. Use `tiny` for speed or `small` for better accuracy if your computer can handle it.
- `device_name` can be left empty. Set it to part of a device name if you want a specific microphone or loopback device.

Edit `.env`:

```env
TRANSLATION_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
TARGET_LANGUAGE=zh-cn
SHOW_ORIGINAL=true
UI_LANGUAGE=bilingual
```

The display format is:

```text
EN: I think this is useful.
中: 我觉得这个很有用。
```

If Whisper detects Chinese speech, the app translates it into English for the `EN:` line and keeps simplified Chinese text on the `中:` line. If it detects English speech, it keeps English on `EN:` and translates to simplified Chinese on `中:`.

For responsiveness, the app displays the recognized text immediately with `翻译中... / Translating...`, then updates the same subtitle item when DeepSeek returns. Translation runs in the background and does not block the next audio chunk.

## Packaging Later

After the MVP is stable:

```powershell
pip install pyinstaller
pyinstaller --noconsole --name AISubtitleWin --add-data "config.toml;." --add-data ".env;." ai_subtitle_win\__main__.py
```

The packaged app will appear in `dist\AISubtitleWin`.

## Notes

- Loopback capture depends on Windows audio drivers. Some machines expose loopback devices clearly; others need microphone capture or stereo mix enabled.
- If captions appear when nothing is playing, check `config.toml`: microphone mode or a virtual microphone can feed noise into Whisper. Loopback mode now avoids falling back to the microphone automatically.
- Real-time quality depends on CPU/GPU speed.
- DeepSeek translation requires an API key because the model runs in DeepSeek's cloud. Set `TRANSLATION_PROVIDER=none` to display only Whisper transcription without online translation.
- Runtime logs are written to `logs\app.log`. If the app says it is loading the speech model for a long time, it is usually downloading or initializing the Whisper model before any DeepSeek API call happens.

---

# 中文说明

这是一个 Windows 实时 AI 字幕生成工具。它可以自动监听电脑正在播放的声音，比如网页视频、播放器、会议软件、游戏或其他应用的声音，然后把音频识别成文字，并通过 DeepSeek 大模型翻译后显示在屏幕字幕窗口中。

默认流程：

```text
系统/app/网页音频
 -> faster-whisper 识别原文
 -> DeepSeek V4 Flash 翻译
 -> 屏幕置顶字幕显示
```

## 主要功能

- 支持中文和英文语音识别
- 默认监听电脑系统播放声音，不是麦克风
- 支持麦克风作为备用输入
- 使用 `faster-whisper` 在本地进行语音识别
- 使用 DeepSeek V4 Flash 进行字幕翻译
- 屏幕上显示原文和译文两行
- 透明置顶字幕窗口
- 启动脚本会自动检查 API Key，没填时会提示输入
- 启动后 PowerShell 窗口会自动隐藏/退出

## 快速开始

```powershell
cd D:\ai-subtitle-win
.\run.ps1
```

第一次运行时，脚本会自动安装依赖。如果没有填写 DeepSeek API Key，会出现中英双语提示，让你输入 Key。输入后会自动保存到 `.env` 文件。

第一次使用 Whisper 模型时，程序可能会下载模型文件，需要等待一会儿。

## 配置 DeepSeek

复制 `.env.example` 为 `.env`，或直接运行 `run.ps1` 自动创建。

`.env` 示例：

```env
TRANSLATION_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
TARGET_LANGUAGE=zh-cn
SHOW_ORIGINAL=true
UI_LANGUAGE=bilingual
```

如果你只想显示 Whisper 识别出来的原文，不想调用在线大模型翻译，可以设置：

```env
TRANSLATION_PROVIDER=none
```

## 字幕显示格式

```text
EN: I think this is useful.
中: 我觉得这个很有用。
```

## 常用快捷键

- `Esc`：退出字幕工具
- `Ctrl+L`：在终端里列出可用音频设备
- `Ctrl+M`：暂停或继续监听
- 鼠标左键拖动字幕窗口：移动字幕位置

## 常见问题

### API Key 是必须的吗？

如果使用 DeepSeek、OpenAI、Gemini、Groq 这类云端大模型翻译，就需要 API Key。API Key 用来识别账号、计费和限制请求频率。

如果不想使用 API Key，有几个选择：

- 设置 `TRANSLATION_PROVIDER=none`，只显示本地 Whisper 识别原文
- 后续接入 Ollama 等本地大模型，在本机离线翻译
- 自建翻译服务，比如 LibreTranslate 或本地翻译模型

当前版本推荐先使用 DeepSeek API Key，因为成本低、中文翻译效果好、接入简单。

### 为什么默认抓系统声音？

这个工具主要用于给网页、视频、会议、游戏或其他应用生成实时字幕，所以默认使用 Windows loopback 捕获电脑正在播放的声音。如果你的设备不支持 loopback，可以在 `config.toml` 里把 `source` 改成 `microphone`。

### 可以打包成 exe 吗？

可以。MVP 稳定后可以使用 PyInstaller 打包：

```powershell
pip install pyinstaller
pyinstaller --noconsole --name AISubtitleWin --add-data "config.toml;." --add-data ".env;." ai_subtitle_win\__main__.py
```

生成结果会在 `dist\AISubtitleWin` 目录中。
