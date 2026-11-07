@echo off
setlocal EnableExtensions
set "EXIT_CODE=0"
chcp 65001 >nul

rem Uso:
rem   transcrever.bat "C:\pasta\audio.mp3"   -> transcreve um arquivo
rem   transcrever.bat "C:\pasta"             -> transcreve todos os audios da pasta
rem   (ou arraste um arquivo/pasta para cima deste .bat)
rem Opcoes extras sao repassadas ao script, ex.: --model small

set "TARGET=%~1"
if not defined TARGET set /p "TARGET=Arraste ou digite o caminho do audio ou da pasta: "
if not defined TARGET (set "EXIT_CODE=1" & goto :usage)
set "TARGET=%TARGET:"=%"

set "SCRIPT=%~dp0transcribe.py"
set "EXTRA=%~2 %~3 %~4"
set /a OK=0, FAIL=0, SKIP=0

if not exist "%TARGET%" (echo ERRO: caminho nao encontrado: "%TARGET%" & set "EXIT_CODE=1" & goto :end)

set "PYTHON_CMD="
set "PYTHON_ARGS="
python -c "import sys; sys.exit(0 if sys.version_info[:2] >= (3, 9) else 1)" >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=python"
if not defined PYTHON_CMD call :check_python_launcher 3
if not defined PYTHON_CMD goto :install_python

if not exist "%TARGET%" (echo ERRO: caminho nao encontrado: "%TARGET%" & set "EXIT_CODE=1" & goto :end)

goto :process

:install_python
echo Python 3.9 ou mais recente nao foi encontrado.
echo O instalador oficial do Python 3.13.17 sera baixado e instalado apenas para este usuario.
choice /c SN /n /m "Permitir o download e a instalacao do Python? [S/N] "
if errorlevel 2 (
    echo Instalacao cancelada.
    set "EXIT_CODE=1"
    goto :end
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_python.ps1"
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
echo Uso: transcrever.bat "caminho\do\audio_ou_pasta" [--model small] [--no-timestamps]

:end
echo.
pause
endlocal & exit /b %EXIT_CODE%
