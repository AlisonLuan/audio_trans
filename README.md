# audio_trans

Transcreve áudios longos em **português** usando o [Whisper](https://github.com/openai/whisper) da OpenAI, **100% local** (nada é enviado para a internet, exceto o download inicial do modelo e das dependências).

## Requisitos

- Python 3.9+ (testado no Windows 11)
- ~5 GB de VRAM para o modelo `medium` (ou use `--model small`, ~2 GB)
- GPU NVIDIA recomendada; sem GPU funciona na CPU, porém bem mais devagar

## Uso

```bash
python transcribe.py "C:\caminho\para\audio.mp3"
```

### Atalho no Windows: `transcrever.bat`

Aceita um arquivo **ou uma pasta** (transcreve todos os áudios dela, pulando os que já têm `_transcricao.txt`). Também funciona arrastando o arquivo/pasta para cima do `.bat`.

```bash
transcrever.bat "C:\caminho\para\audio.mp3"
transcrever.bat "C:\caminho\para\pasta" --model small
```

Se uma ou mais transcrições falharem, o `.bat` termina com código de
saída diferente de zero.

Opções:

| Opção | Descrição |
|---|---|
| `--model small` | modelo menor e mais rápido (padrão: `medium`) |
| `--no-timestamps` | salva só o texto, em parágrafos |

O resultado é salvo na **mesma pasta do áudio**, como `<nome_do_audio>_transcricao.txt`, e o terminal mostra uma barra de progresso e uma mensagem ao concluir.

Na primeira execução o script instala sozinho o que faltar: `torch` (com CUDA se houver GPU NVIDIA), `openai-whisper` e o `ffmpeg` (cópia portátil via `static-ffmpeg`, sem precisar de administrador).

## Instalar o FFmpeg manualmente (opcional)

```bash
# Windows (winget)
winget install Gyan.FFmpeg
# macOS
brew install ffmpeg
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg
```

## Privacidade

O `.gitignore` bloqueia áudios e arquivos `*_transcricao.txt` para que conteúdo pessoal não seja enviado ao repositório público por engano.
