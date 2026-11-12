# audio_trans

Versão / Version **0.3.0**

**PT** — Transcreve áudios longos usando o [Whisper](https://github.com/openai/whisper) da OpenAI, **100% local** (nada é enviado para a internet, exceto o download inicial do modelo e das dependências). Padrão: português; inglês e detecção automática também estão disponíveis.

**EN** — Transcribes long audio with OpenAI's [Whisper](https://github.com/openai/whisper), **fully local** (nothing is sent to the internet except the initial download of the model and dependencies). Default: Portuguese; English and automatic detection are also available.

## Download

**PT** — Baixe `audio_trans-0.3.0-windows.zip` na página de [Releases](https://github.com/AlisonLuan/audio_trans/releases/latest), extraia e execute `audio_trans.exe`. Não precisa de instalação, mas o Python 3.9+ é necessário para transcrever (a interface oferece instalar o Python oficial, apenas para o seu usuário).

**EN** — Download `audio_trans-0.3.0-windows.zip` from the [Releases](https://github.com/AlisonLuan/audio_trans/releases/latest) page, extract it and run `audio_trans.exe`. No installer is needed, but Python 3.9+ is required to transcribe (the app offers to install the official Python for the current user only). The executable is not signed, so Windows SmartScreen may warn on first run. The zip is not stored in the Git tree; it is attached to each release.

## Requisitos / Requirements

- Windows 64-bit. `transcrever.bat` uses Python 3.9+ if available; otherwise it asks before downloading and installing Python 3.13.17 (current user only, system PATH untouched).
- To run `python transcribe.py` directly, install Python 3.9+ first.
- ~5 GB VRAM for the `medium` model (use `--model small`, ~2 GB, if short on memory). NVIDIA GPU recommended; CPU works but is much slower.
- Recording from the microphone needs the `sounddevice` package. It is bundled in the executable built by `--build`; if you run `python gui.py` from source, run `python -m pip install sounddevice` first.

## Interface gráfica / Graphical interface

Duas formas / Two ways:

```bash
transcrever.bat --gui              # run from source (needs Python 3.9+)
transcrever.bat --build            # build the executable into Output\
```

`--build` creates a local virtual environment in `build\`, installs PyInstaller and sounddevice into it (internet required), builds the GUI and assembles the **`Output\`** folder:

| Item | Purpose |
|---|---|
| `audio_trans.exe` (+ `_internal\`) | graphical interface (Tkinter), ~30 MB |
| `transcribe.py` | transcription engine, launched by the GUI |
| `install_python.ps1` | verified per-user Python installer (offered by the GUI if Python is missing) |
| `transcrever.bat`, `README.md` | command-line shortcut and docs |
| `audio\` | default folder for recordings |

The executable does **not** contain PyTorch, Whisper or the model. It needs a Python 3.9+ on the machine and, on the first transcription, `transcribe.py` installs `torch`, `openai-whisper` and `ffmpeg` and downloads the model (internet required; PyTorch can take several GB). Rebuilding replaces only `audio_trans.exe` and `_internal\`; recordings in `Output\audio\` are kept. Inside `Output\`, `transcrever.bat --gui` opens `audio_trans.exe`; `--build` works only from the source folder (it needs `gui.py`).

### Recursos / Features

- **Idioma da interface / UI language:** Português or English (menu *Idioma / Language*). This only changes the GUI; messages printed by the engine in the log stay in Portuguese.
- **Input:** one file or a folder (non-recursive; existing transcripts in a folder are skipped, a single file asks before overwriting).
- **Model:** `tiny`, `base`, `small`, `medium` (default), `large`.
- **Effort:** *Fast*, *Balanced* (default, identical to versions 0.2.x) or *Accurate* (see below).
- **Audio language:** Portuguese (default), English or automatic detection. Independent from the UI language.
- **Timestamps:** on/off.
- **Record audio:** *Record* / *Stop and save* writes a mono 16 kHz WAV named `rec_YYYYMMDD_HHMMSS.wav` to `audio\` next to the app (changeable; existing files are never overwritten). Optionally transcribes right after saving. A recording is kept in memory until it is saved: if saving fails you can retry, and the audio is written through a temporary `.part` file so an incomplete WAV never looks finished. A warning is shown if the microphone reported dropped audio. Everything is held in RAM while recording (about 115 MB per hour).
- **Cancel:** stops the transcription and its child processes (ffmpeg, pip, the Python installer). Transcripts are written through a temporary `.part` file, so a cancelled run does not leave a partial `.txt`.
- **Help → About / Version.**

## Linha de comando / Command line

```bash
python transcribe.py "C:\path\to\audio.mp3"
transcrever.bat "C:\path\to\audio.mp3"
transcrever.bat "C:\path\to\folder" --model small --effort fast
```

`transcrever.bat` accepts a file **or a folder** (skips files that already have `_transcricao.txt`); dragging a file/folder onto it also works. If any transcription fails, it exits with a non-zero code. All options after the path are forwarded to the script.

| Option | Description |
|---|---|
| `--model {tiny,base,small,medium,large}` | Whisper model (default: `medium`) |
| `--language {pt,en,auto}` | spoken language (default: `pt`; `auto` detects it) |
| `--effort {fast,balanced,accurate}` | decoding effort (default: `balanced`) |
| `--no-timestamps` | save plain text in paragraphs |
| `--version` | print the version |

Effort is not a literal "thinking" setting; it maps to Whisper decoding options: `fast` = greedy decoding, temperature 0 with no retry fallback; `balanced` = Whisper's defaults (unchanged behavior); `accurate` = beam search with beam size 5 (and `best_of` 5 on temperature-fallback retries), slower. Larger models and `accurate` need more time and memory. Not benchmarked here.

The result is saved **beside the audio** as `<audio_name>_transcricao.txt` (UTF-8). Running the Python script directly overwrites an existing transcript; the `.bat` and the GUI skip or ask first.

On first run the script installs whatever is missing: `torch` (with CUDA if an NVIDIA GPU is present), `openai-whisper` and `ffmpeg` (portable copy via `static-ffmpeg`, no administrator needed). Internet is required for Python (if needed), dependencies and the model.

## Instalar o FFmpeg manualmente (opcional) / Manual FFmpeg install (optional)

```bash
# Windows (winget)
winget install Gyan.FFmpeg
# macOS
brew install ffmpeg
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg
```

## Privacidade / Privacy

`.gitignore` blocks audio files, `*_transcricao.txt`, the `audio\` folder, `Output\` and `build\`, so personal content is not committed by mistake. Recording and transcription stay on your machine.
