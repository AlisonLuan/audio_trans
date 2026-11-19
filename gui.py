#!/usr/bin/env python3
"""Interface gráfica (Tkinter) do audio_trans / audio_trans graphical interface.

A GUI não carrega o Whisper: ela grava áudio e chama `transcribe.py` como um
processo separado, usando um Python 3.9+ instalado no computador. Assim o
executável gerado pelo `transcrever.bat --build` continua pequeno, e as
dependências pesadas (PyTorch, Whisper, ffmpeg) são instaladas pelo próprio
`transcribe.py` na primeira transcrição.
"""

import codecs
import os
import queue
import subprocess
import sys
import tempfile
import threading
import time
import wave
from pathlib import Path
from tkinter import (BooleanVar, Menu, StringVar, Text, Tk, Toplevel, filedialog,
                     messagebox)
from tkinter import ttk

from transcribe import (AUDIO_EXTENSIONS, EFFORTS, LANGUAGES, MODELS,
                        __version__)

APP_NAME = "audio_trans"
if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
else:
    APP_DIR = Path(__file__).resolve().parent
ENGINE_SCRIPT = APP_DIR / "transcribe.py"
INSTALLER_SCRIPT = APP_DIR / "install_python.ps1"
DEFAULT_RECORDING_DIR = APP_DIR / "audio"
SAMPLE_RATE = 16000  # taxa nativa do Whisper; gravação mono, 16 bits
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
IMAGE_EXTENSIONS = ("jpg", "jpeg", "png", "bmp", "gif", "tif", "tiff", "webp")
PYTHON_CHECK = "import sys; sys.exit(0 if sys.version_info[:2] >= (3, 9) else 1)"

# --------------------------------------------------------------------------
# Textos da interface (português e inglês)
# --------------------------------------------------------------------------
TEXTS = {
    "pt": {
        "language_name": "Português",
        "menu_file": "Arquivo", "menu_exit": "Sair",
        "menu_language": "Idioma", "menu_help": "Ajuda",
        "menu_about": "Sobre", "menu_version": "Versão",
        "grp_input": "Áudio de entrada",
        "btn_file": "Arquivo...", "btn_folder": "Pasta...",
        "grp_options": "Opções",
        "opt_model": "Modelo:", "opt_effort": "Esforço:",
        "opt_language": "Idioma do áudio:", "opt_timestamps": "Incluir marcações de tempo",
        "effort_fast": "Rápido", "effort_balanced": "Equilibrado (padrão)",
        "effort_accurate": "Preciso (mais lento)",
        "lang_pt": "Português", "lang_en": "Inglês", "lang_auto": "Detectar automaticamente",
        "grp_record": "Gravar áudio",
        "btn_record": "Gravar", "btn_stop": "Parar e salvar",
        "rec_idle": "Pronto para gravar.", "rec_recording": "Gravando... {time}",
        "rec_saved": "Salvo: {path}",
        "rec_auto": "Transcrever logo após gravar",
        "rec_folder": "Salvar em:", "btn_change": "Alterar...",
        "btn_transcribe": "Transcrever", "btn_cancel": "Cancelar",
        "status_idle": "Aguardando.", "status_busy": "Transcrevendo...",
        "grp_log": "Registro",
        "choose_file": "Escolha o áudio", "choose_folder": "Escolha a pasta de áudios",
        "choose_rec_folder": "Escolha a pasta das gravações",
        "filetype_audio": "Arquivos de áudio/vídeo", "filetype_all": "Todos os arquivos",
        "err_title": "Erro",
        "err_no_input": "Escolha um arquivo ou uma pasta de áudio.",
        "err_not_found": "Caminho não encontrado:\n{path}",
        "err_no_audio": "Nenhum arquivo de áudio encontrado em:\n{path}",
        "err_no_engine": "Arquivo não encontrado:\n{path}",
        "err_no_mic": "Não foi possível usar o microfone:\n{error}",
        "err_save": "Não foi possível salvar a gravação:\n{error}",
        "err_empty_rec": "Nenhum áudio foi capturado.",
        "warn_capture": ("O microfone reportou falhas durante a gravação; o áudio "
                         "salvo pode ter trechos faltando:\n{path}"),
        "err_busy": "Já existe uma transcrição em andamento.",
        "err_no_python": "Python 3.9 ou mais recente não foi encontrado.",
        "ask_overwrite": "Já existe uma transcrição:\n{path}\n\nSobrescrever?",
        "ask_install_python": ("Python 3.9 ou mais recente não foi encontrado.\n\n"
                               "Baixar e instalar o Python 3.13.17 oficial apenas para "
                               "este usuário (hash e assinatura são verificados)?"),
        "ask_quit": "Há uma operação em andamento. Sair mesmo assim?",
        "log_skipped": "[pulado] já existe: {path}",
        "log_start": "===== Transcrevendo: {path} =====",
        "log_summary": "===== Resumo: {ok} concluído(s), {skip} já existente(s), "
                       "{fail} com erro =====",
        "log_cancelled": "Cancelado pelo usuário.",
        "log_python": "Usando Python: {cmd}",
        "log_installing_python": "Instalando o Python...",
        "log_python_failed": "Falha ao instalar o Python.",
        "about_title": "Sobre o audio_trans",
        "about_text": ("audio_trans\nVersão {version}\n\n"
                       "Transcreve áudios localmente com o Whisper da OpenAI. "
                       "Nada é enviado à internet, exceto o download inicial das "
                       "dependências e do modelo.\n\n"
                       "Grave ou escolha um áudio, selecione modelo, esforço e idioma, "
                       "e o texto é salvo ao lado do áudio como "
                       "<nome>_transcricao.txt."),
        "version_title": "Versão", "version_text": "audio_trans versão {version}",
        "btn_close": "Fechar",
        "grp_pdf": "Imagens para PDF", "btn_pdf": "Escolher imagens e criar PDF...",
        "choose_images": "Escolha as imagens (serão unidas em ordem de nome)",
        "filetype_images": "Imagens", "save_pdf": "Salvar PDF como",
        "pdf_saved": "PDF criado ({count} página(s)): {path}",
        "err_no_pillow": ("Para criar PDFs, instale o Pillow:\n"
                          "python -m pip install pillow"),
        "err_pdf": "Não foi possível criar o PDF:\n{error}",
    },
    "en": {
        "language_name": "English",
        "menu_file": "File", "menu_exit": "Exit",
        "menu_language": "Language", "menu_help": "Help",
        "menu_about": "About", "menu_version": "Version",
        "grp_input": "Input audio",
        "btn_file": "File...", "btn_folder": "Folder...",
        "grp_options": "Options",
        "opt_model": "Model:", "opt_effort": "Effort:",
        "opt_language": "Audio language:", "opt_timestamps": "Include timestamps",
        "effort_fast": "Fast", "effort_balanced": "Balanced (default)",
        "effort_accurate": "Accurate (slower)",
        "lang_pt": "Portuguese", "lang_en": "English", "lang_auto": "Detect automatically",
        "grp_record": "Record audio",
        "btn_record": "Record", "btn_stop": "Stop and save",
        "rec_idle": "Ready to record.", "rec_recording": "Recording... {time}",
        "rec_saved": "Saved: {path}",
        "rec_auto": "Transcribe right after recording",
        "rec_folder": "Save to:", "btn_change": "Change...",
        "btn_transcribe": "Transcribe", "btn_cancel": "Cancel",
        "status_idle": "Idle.", "status_busy": "Transcribing...",
        "grp_log": "Log",
        "choose_file": "Choose the audio file", "choose_folder": "Choose the audio folder",
        "choose_rec_folder": "Choose the recordings folder",
        "filetype_audio": "Audio/video files", "filetype_all": "All files",
        "err_title": "Error",
        "err_no_input": "Choose an audio file or folder.",
        "err_not_found": "Path not found:\n{path}",
        "err_no_audio": "No audio files found in:\n{path}",
        "err_no_engine": "File not found:\n{path}",
        "err_no_mic": "Could not use the microphone:\n{error}",
        "err_save": "Could not save the recording:\n{error}",
        "err_empty_rec": "No audio was captured.",
        "warn_capture": ("The microphone reported problems while recording; the saved "
                         "audio may have missing parts:\n{path}"),
        "err_busy": "A transcription is already running.",
        "err_no_python": "Python 3.9 or newer was not found.",
        "ask_overwrite": "A transcript already exists:\n{path}\n\nOverwrite it?",
        "ask_install_python": ("Python 3.9 or newer was not found.\n\n"
                               "Download and install the official Python 3.13.17 for "
                               "this user only (hash and signature are verified)?"),
        "ask_quit": "An operation is in progress. Quit anyway?",
        "log_skipped": "[skipped] already exists: {path}",
        "log_start": "===== Transcribing: {path} =====",
        "log_summary": "===== Summary: {ok} done, {skip} already existing, "
                       "{fail} failed =====",
        "log_cancelled": "Cancelled by the user.",
        "log_python": "Using Python: {cmd}",
        "log_installing_python": "Installing Python...",
        "log_python_failed": "Python installation failed.",
        "about_title": "About audio_trans",
        "about_text": ("audio_trans\nVersion {version}\n\n"
                       "Transcribes audio locally with OpenAI Whisper. Nothing is "
                       "sent to the internet, except the initial download of "
                       "dependencies and the model.\n\n"
                       "Record or choose an audio file, pick model, effort and "
                       "language, and the text is saved next to the audio as "
                       "<name>_transcricao.txt."),
        "version_title": "Version", "version_text": "audio_trans version {version}",
        "btn_close": "Close",
        "grp_pdf": "Images to PDF", "btn_pdf": "Choose images and create PDF...",
        "choose_images": "Choose the images (merged in filename order)",
        "filetype_images": "Images", "save_pdf": "Save PDF as",
        "pdf_saved": "PDF created ({count} page(s)): {path}",
        "err_no_pillow": ("To create PDFs, install Pillow:\n"
                          "python -m pip install pillow"),
        "err_pdf": "Could not create the PDF:\n{error}",
    },
}


# --------------------------------------------------------------------------
# Python / transcrição
# --------------------------------------------------------------------------
def _python_works(command: list) -> bool:
    try:
        return subprocess.run(
            command + ["-c", PYTHON_CHECK], stdin=subprocess.DEVNULL,
            capture_output=True, timeout=30, creationflags=CREATE_NO_WINDOW,
        ).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def find_python():
    """Devolve o comando de um Python 3.9+ (lista) ou None.

    No executável gerado (frozen), sys.executable é a própria GUI e não é usado.
    Rodando a partir do código-fonte, o interpretador atual tem prioridade.
    """
    per_user = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python313" / "python.exe"
    candidates = [["python"], ["py", "-3"], [str(per_user)]]
    if not getattr(sys, "frozen", False) and sys.executable:
        current = Path(sys.executable)
        if current.name.lower() == "pythonw.exe" and (current.with_name("python.exe")).is_file():
            current = current.with_name("python.exe")
        candidates.insert(0, [str(current)])
    for command in candidates:
        if command[0] == str(per_user) and not per_user.is_file():
            continue
        if _python_works(command):
            return command
    return None


def output_path_for(audio: Path) -> Path:
    return audio.with_name(f"{audio.stem}_transcricao.txt")


def collect_audio_files(folder: Path) -> list:
    """Áudios diretamente dentro da pasta (sem recursão), como o transcrever.bat."""
    extensions = {"." + ext for ext in AUDIO_EXTENSIONS}
    return sorted(p for p in folder.iterdir()
                  if p.is_file() and p.suffix.lower() in extensions)


def images_to_pdf(images: list, destination: Path) -> None:
    """Une as imagens (uma por página) em um PDF; só o arquivo completo recebe o nome final."""
    from PIL import Image, ImageOps  # Pillow é opcional: só quem converte imagens precisa

    pages = []
    try:
        for path in images:
            with Image.open(path) as source:
                image = ImageOps.exif_transpose(source)  # fotos de celular vêm giradas via EXIF
                if image.mode in ("RGBA", "LA", "P"):
                    image = image.convert("RGBA")
                    flat = Image.new("RGB", image.size, "white")  # transparência -> branco
                    flat.paste(image, mask=image.getchannel("A"))
                    image = flat
                else:
                    image = image.convert("RGB")
                pages.append(image)
        # Nome único: nunca reutiliza nem apaga um .part que não seja deste processo.
        handle, name = tempfile.mkstemp(prefix=destination.name + ".", suffix=".part",
                                        dir=destination.parent)
        os.close(handle)
        partial = Path(name)
        try:
            # shortcut: todas as páginas ficam em RAM, ok para dezenas de fotos; usar img2pdf se precisar de centenas
            pages[0].save(partial, "PDF", save_all=True, append_images=pages[1:])
            os.replace(partial, destination)
        except BaseException:
            partial.unlink(missing_ok=True)
            raise
    finally:
        for page in pages:
            page.close()


# --------------------------------------------------------------------------
# Interface
# --------------------------------------------------------------------------
class App:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.lang = "pt"
        self.events: "queue.Queue" = queue.Queue()
        self.worker = None
        self.pdf_worker = None
        self.process = None
        self.cancel_requested = False

        self.input_var = StringVar()
        self.model_var = StringVar(value="medium")
        self.timestamps_var = BooleanVar(value=True)
        self.auto_transcribe_var = BooleanVar(value=True)
        self.lang_var = StringVar(value=self.lang)
        self.recording_dir = DEFAULT_RECORDING_DIR

        self.stream = None
        self.chunks = []
        self.capture_problem = False
        self.record_start = 0.0
        self.recording = False

        self._build_widgets()
        self.apply_language()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(100, self.poll_events)

    # ---- construção -------------------------------------------------------
    def _build_widgets(self) -> None:
        self.root.geometry("720x700")
        self.root.minsize(620, 620)
        pad = {"padx": 10, "pady": 5}
        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(6, weight=1)

        self.menu = Menu(self.root)
        self.file_menu = Menu(self.menu, tearoff=False)
        self.file_menu.add_command(command=self.on_close)
        self.language_menu = Menu(self.menu, tearoff=False)
        for code in TEXTS:
            self.language_menu.add_radiobutton(
                label=TEXTS[code]["language_name"], variable=self.lang_var,
                value=code, command=self.on_language_change)
        self.help_menu = Menu(self.menu, tearoff=False)
        self.help_menu.add_command(command=self.show_about)
        self.help_menu.add_command(command=self.show_version)
        self.menu.add_cascade(menu=self.file_menu)
        self.menu.add_cascade(menu=self.language_menu)
        self.menu.add_cascade(menu=self.help_menu)
        self.root.config(menu=self.menu)

        # Entrada
        self.grp_input = ttk.LabelFrame(main)
        self.grp_input.grid(row=0, column=0, sticky="ew", **pad)
        self.grp_input.columnconfigure(0, weight=1)
        ttk.Entry(self.grp_input, textvariable=self.input_var).grid(
            row=0, column=0, sticky="ew", padx=5, pady=5)
        self.btn_file = ttk.Button(self.grp_input, command=self.choose_file)
        self.btn_file.grid(row=0, column=1, padx=2)
        self.btn_folder = ttk.Button(self.grp_input, command=self.choose_folder)
        self.btn_folder.grid(row=0, column=2, padx=(2, 5))

        # Opções
        self.grp_options = ttk.LabelFrame(main)
        self.grp_options.grid(row=1, column=0, sticky="ew", **pad)
        self.lbl_model = ttk.Label(self.grp_options)
        self.lbl_model.grid(row=0, column=0, sticky="w", padx=5, pady=3)
        ttk.Combobox(self.grp_options, textvariable=self.model_var, values=MODELS,
                     state="readonly", width=12).grid(row=0, column=1, sticky="w")
        self.lbl_effort = ttk.Label(self.grp_options)
        self.lbl_effort.grid(row=0, column=2, sticky="w", padx=(15, 5))
        self.effort_combo = ttk.Combobox(self.grp_options, state="readonly", width=22)
        self.effort_combo.grid(row=0, column=3, sticky="w")
        self.lbl_audio_lang = ttk.Label(self.grp_options)
        self.lbl_audio_lang.grid(row=1, column=0, sticky="w", padx=5, pady=3)
        self.audio_lang_combo = ttk.Combobox(self.grp_options, state="readonly", width=22)
        self.audio_lang_combo.grid(row=1, column=1, columnspan=2, sticky="w")
        self.chk_timestamps = ttk.Checkbutton(self.grp_options, variable=self.timestamps_var)
        self.chk_timestamps.grid(row=1, column=3, sticky="w")
        # Valores provisórios; apply_language() troca pelos textos traduzidos.
        self.effort_combo.configure(values=EFFORTS)
        self.audio_lang_combo.configure(values=LANGUAGES)
        self.effort_combo.current(EFFORTS.index("balanced"))
        self.audio_lang_combo.current(LANGUAGES.index("pt"))

        # Gravação
        self.grp_record = ttk.LabelFrame(main)
        self.grp_record.grid(row=2, column=0, sticky="ew", **pad)
        self.grp_record.columnconfigure(3, weight=1)
        self.btn_record = ttk.Button(self.grp_record, command=self.start_recording)
        self.btn_record.grid(row=0, column=0, padx=5, pady=5)
        self.btn_stop = ttk.Button(self.grp_record, command=self.stop_recording,
                                   state="disabled")
        self.btn_stop.grid(row=0, column=1, padx=5)
        self.chk_auto = ttk.Checkbutton(self.grp_record, variable=self.auto_transcribe_var)
        self.chk_auto.grid(row=0, column=2, padx=10)
        self.rec_status = ttk.Label(self.grp_record)
        self.rec_status.grid(row=1, column=0, columnspan=4, sticky="w", padx=5)
        self.lbl_rec_folder = ttk.Label(self.grp_record)
        self.lbl_rec_folder.grid(row=2, column=0, sticky="w", padx=5, pady=3)
        self.rec_folder_label = ttk.Label(self.grp_record)
        self.rec_folder_label.grid(row=2, column=1, columnspan=2, sticky="w")
        self.btn_rec_folder = ttk.Button(self.grp_record, command=self.choose_recording_dir)
        self.btn_rec_folder.grid(row=2, column=3, sticky="e", padx=5)

        # Imagens para PDF
        self.grp_pdf = ttk.LabelFrame(main)
        self.grp_pdf.grid(row=3, column=0, sticky="ew", **pad)
        self.btn_pdf = ttk.Button(self.grp_pdf, command=self.create_pdf)
        self.btn_pdf.grid(row=0, column=0, padx=5, pady=5)

        # Ações
        actions = ttk.Frame(main)
        actions.grid(row=4, column=0, sticky="ew", **pad)
        self.btn_transcribe = ttk.Button(actions, command=self.start_transcription)
        self.btn_transcribe.pack(side="left")
        self.btn_cancel = ttk.Button(actions, command=self.cancel, state="disabled")
        self.btn_cancel.pack(side="left", padx=8)
        self.status_label = ttk.Label(actions)
        self.status_label.pack(side="left", padx=10)
        self.progress = ttk.Progressbar(main, mode="indeterminate")
        self.progress.grid(row=5, column=0, sticky="ew", padx=10)

        # Registro
        self.grp_log = ttk.LabelFrame(main)
        self.grp_log.grid(row=6, column=0, sticky="nsew", **pad)
        self.grp_log.columnconfigure(0, weight=1)
        self.grp_log.rowconfigure(1, weight=1)
        self.progress_line = ttk.Label(self.grp_log, text="")
        self.progress_line.grid(row=0, column=0, sticky="w", padx=5)
        self.log = Text(self.grp_log, height=10, wrap="word", state="disabled")
        self.log.grid(row=1, column=0, sticky="nsew", padx=(5, 0), pady=5)
        scroll = ttk.Scrollbar(self.grp_log, command=self.log.yview)
        scroll.grid(row=1, column=1, sticky="ns", pady=5, padx=(0, 5))
        self.log.configure(yscrollcommand=scroll.set)

    def apply_language(self) -> None:
        t = TEXTS[self.lang]
        self.root.title(f"{APP_NAME} {__version__}")
        self.menu.entryconfigure(0, label=t["menu_file"])
        self.menu.entryconfigure(1, label=t["menu_language"])
        self.menu.entryconfigure(2, label=t["menu_help"])
        self.file_menu.entryconfigure(0, label=t["menu_exit"])
        self.help_menu.entryconfigure(0, label=t["menu_about"])
        self.help_menu.entryconfigure(1, label=t["menu_version"])
        self.grp_input.configure(text=t["grp_input"])
        self.btn_file.configure(text=t["btn_file"])
        self.btn_folder.configure(text=t["btn_folder"])
        self.grp_options.configure(text=t["grp_options"])
        self.lbl_model.configure(text=t["opt_model"])
        self.lbl_effort.configure(text=t["opt_effort"])
        self.lbl_audio_lang.configure(text=t["opt_language"])
        self.chk_timestamps.configure(text=t["opt_timestamps"])
        effort_index = self.effort_combo.current()
        audio_index = self.audio_lang_combo.current()
        self.effort_combo.configure(values=[t[f"effort_{e}"] for e in EFFORTS])
        self.audio_lang_combo.configure(values=[t[f"lang_{c}"] for c in LANGUAGES])
        self.effort_combo.current(max(effort_index, 0))
        self.audio_lang_combo.current(max(audio_index, 0))
        self.grp_pdf.configure(text=t["grp_pdf"])
        self.btn_pdf.configure(text=t["btn_pdf"])
        self.grp_record.configure(text=t["grp_record"])
        self.btn_record.configure(text=t["btn_record"])
        self.btn_stop.configure(text=t["btn_stop"])
        self.chk_auto.configure(text=t["rec_auto"])
        self.lbl_rec_folder.configure(text=t["rec_folder"])
        self.btn_rec_folder.configure(text=t["btn_change"])
        self.rec_folder_label.configure(text=str(self.recording_dir))
        self.btn_transcribe.configure(text=t["btn_transcribe"])
        self.btn_cancel.configure(text=t["btn_cancel"])
        self.grp_log.configure(text=t["grp_log"])
        if not self.recording:
            self.rec_status.configure(text=t["rec_idle"])
        self.status_label.configure(
            text=t["status_busy"] if self.is_busy() else t["status_idle"])

    def on_language_change(self) -> None:
        self.lang = self.lang_var.get()
        self.apply_language()

    def tr(self, key: str, **kwargs) -> str:
        return TEXTS[self.lang][key].format(**kwargs)

    # ---- ajuda ------------------------------------------------------------
    def show_about(self) -> None:
        dialog = Toplevel(self.root)
        dialog.title(self.tr("about_title"))
        dialog.resizable(False, False)
        dialog.transient(self.root)
        ttk.Label(dialog, text=self.tr("about_text", version=__version__),
                  justify="left", wraplength=420).pack(padx=20, pady=15)
        ttk.Button(dialog, text=self.tr("btn_close"), command=dialog.destroy).pack(pady=(0, 15))
        dialog.grab_set()

    def show_version(self) -> None:
        messagebox.showinfo(self.tr("version_title"),
                            self.tr("version_text", version=__version__))

    # ---- entrada ----------------------------------------------------------
    def choose_file(self) -> None:
        patterns = " ".join(f"*.{ext}" for ext in AUDIO_EXTENSIONS)
        path = filedialog.askopenfilename(
            title=self.tr("choose_file"),
            filetypes=[(self.tr("filetype_audio"), patterns),
                       (self.tr("filetype_all"), "*.*")])
        if path:
            self.input_var.set(str(Path(path)))

    def choose_folder(self) -> None:
        path = filedialog.askdirectory(title=self.tr("choose_folder"))
        if path:
            self.input_var.set(str(Path(path)))

    def choose_recording_dir(self) -> None:
        path = filedialog.askdirectory(title=self.tr("choose_rec_folder"))
        if path:
            self.recording_dir = Path(path)
            self.rec_folder_label.configure(text=str(self.recording_dir))

    # ---- imagens para PDF --------------------------------------------------
    def create_pdf(self) -> None:
        try:
            from PIL import Image
        except ImportError:
            messagebox.showerror(self.tr("err_title"), self.tr("err_no_pillow"))
            return
        patterns = " ".join(f"*.{ext}" for ext in IMAGE_EXTENSIONS)
        chosen = filedialog.askopenfilenames(
            title=self.tr("choose_images"),
            filetypes=[(self.tr("filetype_images"), patterns),
                       (self.tr("filetype_all"), "*.*")])
        if not chosen:
            return
        images = sorted((Path(p) for p in chosen), key=lambda p: p.name.lower())
        destination = filedialog.asksaveasfilename(  # já pergunta antes de sobrescrever
            title=self.tr("save_pdf"), initialdir=str(images[0].parent),
            initialfile=images[0].stem + ".pdf", defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")])
        if not destination:
            return
        self.btn_pdf.configure(state="disabled")
        self.pdf_worker = threading.Thread(
            target=self.run_pdf, args=(images, Path(destination)), daemon=True)
        self.pdf_worker.start()

    def run_pdf(self, images: list, destination: Path) -> None:
        from PIL import Image
        try:
            images_to_pdf(images, destination)
            self.emit("log", self.tr("pdf_saved", count=len(images), path=destination))
        except (OSError, ValueError, MemoryError, Image.DecompressionBombError) as error:
            # ilegível/não é imagem/disco cheio/imagem gigante demais
            self.emit("error", self.tr("err_pdf", error=error or type(error).__name__))
        finally:
            self.emit("pdf_done")

    # ---- gravação ---------------------------------------------------------
    def start_recording(self) -> None:
        if self.recording:
            return
        try:
            import sounddevice  # noqa: WPS433

            self.chunks = []
            self.capture_problem = False

            def on_audio(indata, frames, time_info, status):  # noqa: ARG001
                if status:  # overflow/underflow: pode haver trechos faltando
                    self.capture_problem = True
                self.chunks.append(bytes(indata))

            self.stream = sounddevice.RawInputStream(
                samplerate=SAMPLE_RATE, channels=1, dtype="int16", callback=on_audio)
            self.stream.start()
        except Exception as error:  # noqa: BLE001 - dispositivos/driver variam muito
            self.stream = None
            messagebox.showerror(self.tr("err_title"), self.tr("err_no_mic", error=error))
            return
        self.recording = True
        self.record_start = time.time()
        self.btn_record.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.tick_recording()

    def tick_recording(self) -> None:
        if not self.recording:
            return
        elapsed = int(time.time() - self.record_start)
        clock = f"{elapsed // 60:02d}:{elapsed % 60:02d}"
        self.rec_status.configure(text=self.tr("rec_recording", time=clock))
        self.root.after(500, self.tick_recording)

    def stop_recording(self) -> None:
        if not self.recording:
            return
        self.recording = False
        try:
            self.stream.stop()
            self.stream.close()
        finally:
            self.stream = None
        self.btn_record.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        chunks = self.chunks
        if not chunks:
            self.chunks = []
            self.rec_status.configure(text=self.tr("rec_idle"))
            messagebox.showerror(self.tr("err_title"), self.tr("err_empty_rec"))
            return
        # As amostras só são descartadas depois de salvas; em caso de falha o
        # usuário pode tentar de novo (ex.: após liberar espaço em disco).
        while True:
            try:
                path = self.save_recording(chunks)
                break
            except OSError as error:
                if not messagebox.askretrycancel(
                        self.tr("err_title"), self.tr("err_save", error=error)):
                    self.chunks = []
                    self.rec_status.configure(text=self.tr("rec_idle"))
                    return
        self.chunks = []
        self.rec_status.configure(text=self.tr("rec_saved", path=path))
        if self.capture_problem:
            messagebox.showwarning(self.tr("err_title"), self.tr("warn_capture", path=path))
        self.input_var.set(str(path))
        if self.auto_transcribe_var.get():
            self.start_transcription()

    def save_recording(self, chunks: list) -> Path:
        """Grava os blocos em um .wav; só o arquivo completo recebe o nome final."""
        self.recording_dir.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d_%H%M%S")
        path = self.recording_dir / f"rec_{stamp}.wav"
        counter = 1
        while path.exists():  # nunca sobrescreve uma gravação existente
            counter += 1
            path = self.recording_dir / f"rec_{stamp}_{counter}.wav"
        partial = path.with_name(path.name + ".part")
        try:
            with wave.open(str(partial), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(SAMPLE_RATE)
                for chunk in chunks:  # sem juntar tudo em memória de novo
                    wav.writeframes(chunk)
            os.replace(partial, path)
        except OSError:
            try:
                partial.unlink()
            except OSError:
                pass
            raise
        return path

    # ---- transcrição ------------------------------------------------------
    def is_busy(self) -> bool:
        return self.worker is not None and self.worker.is_alive()

    def start_transcription(self) -> None:
        if self.is_busy():
            messagebox.showerror(self.tr("err_title"), self.tr("err_busy"))
            return
        raw = self.input_var.get().strip().strip('"')
        if not raw:
            messagebox.showerror(self.tr("err_title"), self.tr("err_no_input"))
            return
        target = Path(raw)
        if not target.exists():
            messagebox.showerror(self.tr("err_title"), self.tr("err_not_found", path=target))
            return
        if not ENGINE_SCRIPT.is_file():
            messagebox.showerror(self.tr("err_title"),
                                 self.tr("err_no_engine", path=ENGINE_SCRIPT))
            return

        if target.is_dir():
            files = collect_audio_files(target)
            if not files:
                messagebox.showerror(self.tr("err_title"), self.tr("err_no_audio", path=target))
                return
            overwrite = False
        else:
            files = [target]
            overwrite = False
            existing = output_path_for(target)
            if existing.exists():
                if not messagebox.askyesno(self.tr("err_title"),
                                           self.tr("ask_overwrite", path=existing)):
                    return
                overwrite = True

        options = [
            "--model", self.model_var.get(),
            "--effort", EFFORTS[self.effort_combo.current()],
            "--language", LANGUAGES[self.audio_lang_combo.current()],
        ]
        if not self.timestamps_var.get():
            options.append("--no-timestamps")

        python = find_python()
        if python is None:
            if not messagebox.askyesno(self.tr("err_title"), self.tr("ask_install_python")):
                return
            python = None  # será instalado dentro da thread de trabalho

        self.cancel_requested = False
        self.btn_transcribe.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.status_label.configure(text=self.tr("status_busy"))
        self.progress.start(15)
        self.worker = threading.Thread(
            target=self.run_jobs, args=(python, files, options, overwrite), daemon=True)
        self.worker.start()

    def emit(self, kind: str, payload="") -> None:
        self.events.put((kind, payload))

    def install_python(self):
        """Executa install_python.ps1 e devolve o comando do Python instalado."""
        self.emit("log", self.tr("log_installing_python"))
        if not INSTALLER_SCRIPT.is_file():
            self.emit("log", self.tr("err_no_engine", path=INSTALLER_SCRIPT))
            return None
        code = self.run_process(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                                 "-File", str(INSTALLER_SCRIPT)])
        if code != 0:
            self.emit("log", self.tr("log_python_failed"))
            return None
        return find_python()

    def run_process(self, command: list) -> int:
        environment = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
        self.process = subprocess.Popen(
            command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, bufsize=0, env=environment,
            creationflags=CREATE_NO_WINDOW)
        decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        pending = ""
        while True:
            chunk = self.process.stdout.read(4096)
            if not chunk:
                break
            pending += decoder.decode(chunk)
            while True:
                positions = [i for i in (pending.find("\r"), pending.find("\n")) if i >= 0]
                if not positions:
                    break
                cut = min(positions)
                line, terminator, pending = pending[:cut], pending[cut], pending[cut + 1:]
                if terminator == "\r" and pending.startswith("\n"):
                    terminator, pending = "\n", pending[1:]
                if line.strip():
                    self.emit("progress" if terminator == "\r" else "log", line)
        if pending.strip():
            self.emit("log", pending)
        return self.process.wait()

    def run_jobs(self, python, files: list, options: list, overwrite: bool) -> None:
        ok = skipped = failed = 0
        try:
            if python is None:
                python = self.install_python()
                if python is None:
                    self.emit("log", self.tr("err_no_python"))
                    self.emit("done", None)
                    return
            self.emit("log", self.tr("log_python", cmd=" ".join(python)))
            for audio in files:
                if self.cancel_requested:
                    break
                if output_path_for(audio).exists() and not overwrite:
                    self.emit("log", self.tr("log_skipped", path=output_path_for(audio)))
                    skipped += 1
                    continue
                self.emit("log", self.tr("log_start", path=audio))
                code = self.run_process(python + [str(ENGINE_SCRIPT), str(audio)] + options)
                if self.cancel_requested:
                    break
                if code == 0:
                    ok += 1
                else:
                    failed += 1
            if self.cancel_requested:
                self.emit("log", self.tr("log_cancelled"))
            else:
                self.emit("log", self.tr("log_summary", ok=ok, skip=skipped, fail=failed))
        except OSError as error:
            self.emit("log", f"ERRO/ERROR: {error}")
        finally:
            self.process = None
            self.emit("done", None)

    def cancel(self) -> None:
        self.cancel_requested = True
        process = self.process
        if process is not None and process.poll() is None:
            if sys.platform == "win32":
                # terminate() só atinge o processo direto; ffmpeg/pip/instalador
                # filhos continuariam rodando e segurando o pipe de saída.
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                               stdin=subprocess.DEVNULL, capture_output=True,
                               creationflags=CREATE_NO_WINDOW)
            else:
                process.terminate()

    # ---- eventos da thread de trabalho -------------------------------------
    def append_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def poll_events(self) -> None:
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "log":
                    self.progress_line.configure(text="")
                    self.append_log(payload)
                elif kind == "error":
                    messagebox.showerror(self.tr("err_title"), payload)
                elif kind == "pdf_done":
                    self.btn_pdf.configure(state="normal")
                elif kind == "progress":
                    self.progress_line.configure(text=payload)
                elif kind == "done":
                    self.progress.stop()
                    self.progress_line.configure(text="")
                    self.btn_transcribe.configure(state="normal")
                    self.btn_cancel.configure(state="disabled")
                    self.status_label.configure(text=self.tr("status_idle"))
        except queue.Empty:
            pass
        self.root.after(100, self.poll_events)

    def on_close(self) -> None:
        pdf_busy = self.pdf_worker is not None and self.pdf_worker.is_alive()
        if self.recording or self.is_busy() or pdf_busy:
            if not messagebox.askyesno(APP_NAME, self.tr("ask_quit")):
                return
            self.cancel()
            if self.recording and self.stream is not None:
                try:
                    self.stream.close()
                except Exception:  # noqa: BLE001 - saindo de qualquer forma
                    pass
        self.root.destroy()


def main() -> None:
    root = Tk()
    ttk.Style(root)
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
