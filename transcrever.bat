@echo off
setlocal EnableExtensions
set "EXIT_CODE=0"
chcp 65001 >nul

rem Uso:
rem   transcrever.bat "C:\pasta\audio.mp3"   -> transcreve um arquivo
rem   transcrever.bat "C:\pasta"             -> transcreve todos os audios da pasta
rem   (ou arraste um arquivo/pasta para cima deste .bat)
rem   transcrever.bat --gui                  -> abre a interface grafica
rem   transcrever.bat --build                -> gera o executavel e a pasta Output
rem Opcoes extras sao repassadas ao script, ex.: --model small --effort fast
rem   --language en --no-timestamps

rem Capturado antes de qualquer SHIFT: shift tambem desloca %0 (e portanto %~dp0).
set "SCRIPT_DIR=%~dp0"

set "MODE=transcribe"
if /i "%~1"=="--gui" (set "MODE=gui" & shift)
if /i "%~1"=="--build" (set "MODE=build" & shift)

rem Na pasta Output ha o executavel (sem gui.py): abre-o direto, sem exigir Python.
if "%MODE%"=="gui" if exist "%SCRIPT_DIR%audio_trans.exe" (
    start "" "%SCRIPT_DIR%audio_trans.exe"
    endlocal & exit /b 0
)

set "SCRIPT=%SCRIPT_DIR%transcribe.py"
set "EXTRA="
set /a OK=0, FAIL=0, SKIP=0
set "PYTHON_CMD="
set "PYTHON_ARGS="

if not "%MODE%"=="transcribe" goto :find_python

set "TARGET=%~1"
if not defined TARGET set /p "TARGET=Arraste ou digite o caminho do audio ou da pasta: "
if not defined TARGET (set "EXIT_CODE=1" & goto :usage)
set "TARGET=%TARGET:"=%"

rem Repassa todas as opcoes depois do caminho (--model, --effort, --language, ...)
shift
:collect_extra
if "%~1"=="" goto :extra_done
set "EXTRA=%EXTRA% %~1"
shift
goto :collect_extra
:extra_done

if not exist "%TARGET%" (echo ERRO: caminho nao encontrado: "%TARGET%" & set "EXIT_CODE=1" & goto :end)

:find_python
python -c "import sys; sys.exit(0 if sys.version_info[:2] >= (3, 9) else 1)" >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=python"
if not defined PYTHON_CMD call :check_python_launcher 3
if not defined PYTHON_CMD goto :install_python
goto :dispatch

:install_python
echo Python 3.9 ou mais recente nao foi encontrado.
echo O instalador oficial do Python 3.13.17 sera baixado e instalado apenas para este usuario.
choice /c SN /n /m "Permitir o download e a instalacao do Python? [S/N] "
if errorlevel 2 (
    echo Instalacao cancelada.
    set "EXIT_CODE=1"
    goto :end
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%install_python.ps1"
if errorlevel 1 (
    echo ERRO: nao foi possivel instalar o Python.
    set "EXIT_CODE=1"
    goto :end
)
set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not exist "%PYTHON_CMD%" (
    echo ERRO: Python nao foi encontrado apos a instalacao.
    set "EXIT_CODE=1"
    goto :end
)

:dispatch
if "%MODE%"=="gui" goto :gui
if "%MODE%"=="build" goto :build

:process
if not exist "%TARGET%" (echo ERRO: caminho nao encontrado: "%TARGET%" & set "EXIT_CODE=1" & goto :end)

rem Pasta? (o sufixo \ so existe se for diretorio)
if exist "%TARGET%\" goto :folder

call :one "%TARGET%"
goto :summary

:folder
for %%E in (mp3 m4a wav flac ogg aac wma opus mp4 mkv webm) do (
    for %%F in ("%TARGET%\*.%%E") do call :one "%%~fF"
)
if %OK%==0 if %FAIL%==0 if %SKIP%==0 echo Nenhum arquivo de audio encontrado em "%TARGET%".

:summary
echo.
echo ===== Resumo: %OK% concluido(s), %SKIP% ja existente(s), %FAIL% com erro =====
if not "%FAIL%"=="0" set "EXIT_CODE=1"
goto :end

:gui
rem Para gravar neste modo, instale o microfone: python -m pip install sounddevice
if not exist "%SCRIPT_DIR%gui.py" (echo ERRO: gui.py nao encontrado em "%SCRIPT_DIR%". & set "EXIT_CODE=1" & goto :end)
"%PYTHON_CMD%" %PYTHON_ARGS% "%SCRIPT_DIR%gui.py"
if errorlevel 1 set "EXIT_CODE=1"
goto :end

:build
rem Gera build\dist\audio_trans (PyInstaller, em um venv local) e monta a pasta Output.
rem Nao ha PyTorch/Whisper no executavel: transcribe.py os instala na 1a transcricao.
set "ROOT=%SCRIPT_DIR%."
if not exist "%ROOT%\gui.py" (echo ERRO: --build precisa do codigo-fonte ^(gui.py^) em "%ROOT%". & set "EXIT_CODE=1" & goto :end)
set "BUILD_DIR=%ROOT%\build"
set "VENV=%BUILD_DIR%\venv"
set "OUTPUT=%ROOT%\Output"
echo Gerando o executavel (requer internet para baixar PyInstaller, sounddevice e pillow)...
if not exist "%VENV%\Scripts\python.exe" (
    "%PYTHON_CMD%" %PYTHON_ARGS% -m venv "%VENV%"
    if errorlevel 1 (echo ERRO: nao foi possivel criar o ambiente virtual. & set "EXIT_CODE=1" & goto :end)
)
"%VENV%\Scripts\python.exe" -m pip install --upgrade pyinstaller sounddevice pillow
if errorlevel 1 (echo ERRO: nao foi possivel instalar PyInstaller/sounddevice/pillow. & set "EXIT_CODE=1" & goto :end)
"%VENV%\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onedir --windowed --name audio_trans --distpath "%BUILD_DIR%\dist" --workpath "%BUILD_DIR%\work" --specpath "%BUILD_DIR%" --paths "%ROOT%" --collect-all sounddevice "%ROOT%\gui.py"
if errorlevel 1 (echo ERRO: o PyInstaller falhou. & set "EXIT_CODE=1" & goto :end)

rem Remove apenas o que este build gera; gravacoes em Output\audio sao preservadas.
if exist "%OUTPUT%\_internal" rmdir /s /q "%OUTPUT%\_internal"
if exist "%OUTPUT%\audio_trans.exe" del /q "%OUTPUT%\audio_trans.exe"
if exist "%OUTPUT%\_internal" (echo ERRO: nao foi possivel remover "%OUTPUT%\_internal" ^(arquivo em uso?^). & set "EXIT_CODE=1" & goto :end)
if exist "%OUTPUT%\audio_trans.exe" (echo ERRO: nao foi possivel remover "%OUTPUT%\audio_trans.exe" ^(em uso?^). & set "EXIT_CODE=1" & goto :end)
if not exist "%OUTPUT%" mkdir "%OUTPUT%"
if not exist "%OUTPUT%" (echo ERRO: nao foi possivel criar "%OUTPUT%". & set "EXIT_CODE=1" & goto :end)
xcopy "%BUILD_DIR%\dist\audio_trans" "%OUTPUT%" /e /y /q /i >nul
if errorlevel 1 (echo ERRO: nao foi possivel copiar o executavel para Output. & set "EXIT_CODE=1" & goto :end)
for %%F in (transcribe.py install_python.ps1 transcrever.bat README.md) do (
    copy /y "%ROOT%\%%F" "%OUTPUT%\" >nul
    if errorlevel 1 (echo ERRO: nao foi possivel copiar %%F para Output. & set "EXIT_CODE=1" & goto :end)
)
if not exist "%OUTPUT%\audio" mkdir "%OUTPUT%\audio"
if not exist "%OUTPUT%\audio" (echo ERRO: nao foi possivel criar "%OUTPUT%\audio". & set "EXIT_CODE=1" & goto :end)
echo.
echo Pronto: "%OUTPUT%\audio_trans.exe"
goto :end

:one
set "AUDIO=%~1"
set "OUT=%~dpn1_transcricao.txt"
if exist "%OUT%" (
    echo [pulado] ja existe: "%OUT%"
    set /a SKIP+=1
    exit /b 0
)
echo.
echo ===== Transcrevendo: "%AUDIO%" =====
"%PYTHON_CMD%" %PYTHON_ARGS% "%SCRIPT%" "%AUDIO%" %EXTRA%
if errorlevel 1 (set /a FAIL+=1) else (set /a OK+=1)
exit /b 0

:check_python_launcher
py -%~1 -c "import sys; sys.exit(0 if sys.version_info[:2] >= (3, 9) else 1)" >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=py"
    set "PYTHON_ARGS=-%~1"
)
exit /b 0

:usage
echo Uso: transcrever.bat "caminho\do\audio_ou_pasta" [--model small] [--effort fast^|balanced^|accurate] [--language pt^|en^|auto] [--no-timestamps]
echo      transcrever.bat --gui      (interface grafica)
echo      transcrever.bat --build    (gera o executavel na pasta Output)

:end
echo.
pause
endlocal & exit /b %EXIT_CODE%
