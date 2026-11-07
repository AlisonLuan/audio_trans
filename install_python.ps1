$ErrorActionPreference = 'Stop'

$version = '3.13.17'
$installerUrl = "https://www.python.org/ftp/python/$version/python-$version-amd64.exe"
$expectedHash = '5DA012101BA2E17113A9A1CD901E9CE1441086F2B7ECB5DE06EC94163899A190'
$installDirectory = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313'
$installerPath = Join-Path ([IO.Path]::GetTempPath()) "python-$version-$([guid]::NewGuid().ToString('N')).exe"

try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Write-Host "Baixando Python $version do python.org..."
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing

    $actualHash = (Get-FileHash -LiteralPath $installerPath -Algorithm SHA256).Hash
    if ($actualHash -ne $expectedHash) {
        throw 'O hash do instalador baixado nao corresponde ao hash oficial.'
    }

    $signature = Get-AuthenticodeSignature -FilePath $installerPath
    if ($signature.Status -ne 'Valid' -or
        $signature.SignerCertificate.Subject -notmatch 'Python Software Foundation') {
        throw 'A assinatura digital do instalador Python nao e valida.'
    }

    Write-Host 'Instalando Python para este usuario...'
    $process = Start-Process -FilePath $installerPath -ArgumentList @(
        '/passive',
        'InstallAllUsers=0',
        "TargetDir=`"$installDirectory`"",
        'PrependPath=0',
        'Include_launcher=0',
        'Include_test=0',
        'Include_pip=1'
    ) -Wait -PassThru

    if ($process.ExitCode -ne 0) {
        throw "O instalador Python terminou com codigo $($process.ExitCode)."
    }

    $pythonPath = Join-Path $installDirectory 'python.exe'
    if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
        throw 'O Python nao foi encontrado no diretorio de instalacao.'
    }
    & $pythonPath -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 13) else 1)"
    if ($LASTEXITCODE -ne 0) {
        throw 'A versao instalada do Python nao e a esperada.'
    }
}
finally {
    if (Test-Path -LiteralPath $installerPath) {
        Remove-Item -LiteralPath $installerPath -Force
    }
}
