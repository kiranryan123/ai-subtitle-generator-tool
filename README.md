# AI字幕生成工具 / AI Subtitle Generator Tool

Windows real-time AI subtitle MVP for Chinese and English audio.

This prototype shows live captions in a transparent always-on-top overlay. By default it listens to Windows system playback audio through loopback capture, so it is aimed at subtitles for browser tabs, media players, meetings, games, and other apps. Microphone capture is available as a fallback.

## Features

- Chinese and English speech recognition
- Always-on-top transparent subtitle overlay
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

The first run downloads the selected Whisper model. For a small and fast first test, keep `model_size = "small"` in `config.toml`.

For normal use, run:

```powershell
cd D:\ai-subtitle-win
.\run.ps1
```

`run.ps1` installs missing dependencies, creates `.env` if needed, asks for `DEEPSEEK_API_KEY` when it is missing, starts the subtitle app through `pythonw.exe`, and then lets the PowerShell window close.

## Controls

- `Esc`: quit
- `Ctrl+L`: list audio devices in the terminal
- `Ctrl+M`: toggle mute/pause listening
- Drag the subtitle window by holding the left mouse button

## Config

Edit `config.toml`:

- `source = "loopback"` captions app, webpage, meeting, video, and game audio played by the computer. If that does not work on your device, use `source = "microphone"`.
- `language = "auto"` detects Chinese or English automatically.
- `model_size = "small"` is a good MVP choice. Use `medium` or `large-v3` for better accuracy if your computer can handle it.
- `device_name` can be left empty. Set it to part of a device name if you want a specific microphone or loopback device.

Edit `.env`:

```env
TRANSLATION_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
TARGET_LANGUAGE=zh
SHOW_ORIGINAL=true
```

The display format is:

```text
EN: I think this is useful.
中: 我觉得这个很有用。
```

## Packaging Later

After the MVP is stable:

```powershell
pip install pyinstaller
pyinstaller --noconsole --name AISubtitleWin --add-data "config.toml;." --add-data ".env;." ai_subtitle_win\__main__.py
```

The packaged app will appear in `dist\AISubtitleWin`.

## Notes

- Loopback capture depends on Windows audio drivers. Some machines expose loopback devices clearly; others need microphone capture or stereo mix enabled.
- Real-time quality depends on CPU/GPU speed. NVIDIA GPUs can be used by installing the CUDA-enabled dependencies supported by `faster-whisper`.
- DeepSeek translation requires an API key because the model runs in DeepSeek's cloud. Set `TRANSLATION_PROVIDER=none` to display only Whisper transcription without online translation.
