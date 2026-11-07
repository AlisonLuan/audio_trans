@echo off
setlocal EnableExtensions
chcp 65001 >nul

rem Uso:
rem   transcrever.bat "C:\pasta\audio.mp3"   -> transcreve um arquivo
rem   transcrever.bat "C:\pasta"             -> transcreve todos os audios da pasta
rem   (ou arraste um arquivo/pasta para cima deste .bat)
rem Opcoes extras sao repassadas ao script, ex.: --model small

set "TARGET=%~1"
if not defined TARGET set /p "TARGET=Arraste ou digite o caminho do audio ou da pasta: "
if not defined TARGET goto :usage
set "TARGET=%TARGET:"=%"

set "SCRIPT=%~dp0transcribe.py"
set "EXTRA=%~2 %~3 %~4"
set /a OK=0, FAIL=0, SKIP=0

where python >nul 2>nul || (echo ERRO: Python nao encontrado no PATH. & goto :end)

if not exist "%TARGET%" (echo ERRO: caminho nao encontrado: "%TARGET%" & goto :end)

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
python "%SCRIPT%" "%AUDIO%" %EXTRA%
if errorlevel 1 (set /a FAIL+=1) else (set /a OK+=1)
exit /b 0

:usage
echo Uso: transcrever.bat "caminho\do\audio_ou_pasta" [--model small] [--no-timestamps]

:end
echo.
pause
endlocal
