#!/usr/bin/env python3
"""Transcreve um arquivo de áudio longo em português com o Whisper, 100% local.

Uso:
    python transcribe.py "C:\\caminho\\para\\audio.mp3"
    python transcribe.py audio.m4a --model small

O resultado é salvo em <nome_do_audio>_transcricao.txt, na mesma pasta do áudio.
"""

import argparse
import importlib.util
import shutil
import subprocess
import sys
import time
from pathlib import Path

CUDA_INDEX_URL = "https://download.pytorch.org/whl/cu126"


# --------------------------------------------------------------------------
# Dependências
# --------------------------------------------------------------------------
def pip_install(*args: str) -> None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", *args])


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def has_nvidia_gpu() -> bool:
    if not shutil.which("nvidia-smi"):
        return False
    try:
        return subprocess.run(
            ["nvidia-smi", "-L"], capture_output=True, text=True, timeout=15
        ).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def ensure_torch() -> None:
    """Instala o PyTorch (com suporte a CUDA se houver GPU NVIDIA)."""
    use_cuda_build = has_nvidia_gpu()
    if has_module("torch"):
        import torch  # noqa: WPS433

        # A versão do pacote não identifica de forma confiável builds sem CUDA.
        if not (use_cuda_build and torch.version.cuda is None):
            return
        print("[setup] GPU NVIDIA detectada, mas o PyTorch instalado é só CPU. "
              "Instalando versão com CUDA...")
    else:
        print("[setup] Instalando PyTorch (pode demorar, são alguns GB)...")

    if use_cuda_build:
        pip_install("--upgrade", "--force-reinstall", "torch",
                    "--index-url", CUDA_INDEX_URL)
    else:
        pip_install("torch")


def ensure_ffmpeg() -> None:
    """Garante que o ffmpeg esteja no PATH, sem precisar de administrador."""
    if shutil.which("ffmpeg"):
        return
    print("[setup] ffmpeg não encontrado. Baixando uma cópia portátil "
          "(pacote 'static-ffmpeg')...")
    if not has_module("static_ffmpeg"):
        pip_install("static-ffmpeg")
    import static_ffmpeg  # noqa: WPS433

    static_ffmpeg.add_paths()  # baixa na 1ª vez e adiciona ao PATH deste processo
    if not shutil.which("ffmpeg"):
        sys.exit("ERRO: não consegui instalar o ffmpeg. Instale manualmente "
                 "(veja o README) e rode de novo.")


def ensure_dependencies() -> None:
    ensure_ffmpeg()
    ensure_torch()
    if not has_module("whisper"):
        print("[setup] Instalando openai-whisper...")
        pip_install("openai-whisper")


# --------------------------------------------------------------------------
# Transcrição
# --------------------------------------------------------------------------
def fmt_time(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def build_text(segments: list, timestamps: bool) -> str:
    lines = []
    for seg in segments:
        text = seg["text"].strip()
        if not text:
            continue
        lines.append(f"[{fmt_time(seg['start'])}] {text}" if timestamps else text)
    # Sem timestamps, junta em parágrafos de ~5 frases para ficar legível.
    if not timestamps:
        paragraphs = [" ".join(lines[i:i + 5]) for i in range(0, len(lines), 5)]
        return "\n\n".join(paragraphs)
    return "\n".join(lines)


def transcribe(audio: Path, model_name: str, timestamps: bool) -> Path:
    import torch  # noqa: WPS433
    import whisper  # noqa: WPS433

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        print("[aviso] Sem GPU CUDA: rodando na CPU. Para 1h20 de áudio isso pode "
              "levar bastante tempo; considere --model small.")
    print(f"[info] Carregando modelo '{model_name}' em {device} "
          "(o download acontece só na primeira vez)...")
    model = whisper.load_model(model_name, device=device)

    print(f"[info] Transcrevendo: {audio}")
    print("[info] A barra abaixo mostra o progresso do áudio.\n")
    start = time.time()
    result = model.transcribe(
        str(audio),
        language="pt",
        task="transcribe",
        verbose=False,                      # mostra barra de progresso
        fp16=(device == "cuda"),
        condition_on_previous_text=False,   # evita repetições em áudios longos
    )
    elapsed = time.time() - start

    output = audio.with_name(f"{audio.stem}_transcricao.txt")
    output.write_text(build_text(result["segments"], timestamps) + "\n",
                      encoding="utf-8")
    print(f"\n[ok] Transcrição concluída em {fmt_time(elapsed)}.")
    print(f"[ok] Arquivo salvo em: {output}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transcreve áudio em português com Whisper (local).")
    parser.add_argument("audio", help="caminho do arquivo (.mp3, .m4a, .wav, ...)")
    parser.add_argument("--model", choices=["small", "medium"], default="medium",
                        help="modelo Whisper (padrão: medium; use small se faltar memória)")
    parser.add_argument("--no-timestamps", action="store_true",
                        help="salva só o texto, em parágrafos, sem marcações de tempo")
    args = parser.parse_args()

    audio = Path(args.audio).expanduser().resolve()
    if not audio.is_file():
        sys.exit(f"ERRO: arquivo não encontrado: {audio}")

    ensure_dependencies()
    transcribe(audio, args.model, timestamps=not args.no_timestamps)


if __name__ == "__main__":
    main()
