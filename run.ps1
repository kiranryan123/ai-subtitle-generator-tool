$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

if (-not (Test-Path -LiteralPath ".\.venv\Scripts\python.exe")) {
    python -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

$currentPid = $PID
Get-CimInstance Win32_Process -Filter "Name = 'pythonw.exe' OR Name = 'python.exe'" |
    Where-Object {
        $_.ProcessId -ne $currentPid -and
        $_.CommandLine -and
        $_.CommandLine.Contains("ai_subtitle_win")
    } |
    ForEach-Object {
        Stop-Process -Id $_.ProcessId -Force
    }

$envPath = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path -LiteralPath $envPath)) {
    Copy-Item -LiteralPath ".\.env.example" -Destination $envPath
}

$pythonw = Join-Path $PSScriptRoot ".venv\Scripts\pythonw.exe"
if (-not (Test-Path -LiteralPath $pythonw)) {
    $pythonw = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
}

Start-Process -FilePath $pythonw -ArgumentList "-m", "ai_subtitle_win" -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
