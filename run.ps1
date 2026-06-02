$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

function Get-EnvValue {
    param(
        [string]$Path,
        [string]$Name
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return ""
    }

    $line = Get-Content -LiteralPath $Path |
        Where-Object { $_ -match "^\s*$([regex]::Escape($Name))\s*=" } |
        Select-Object -First 1

    if (-not $line) {
        return ""
    }

    return (($line -split "=", 2)[1]).Trim()
}

function Set-EnvValue {
    param(
        [string]$Path,
        [string]$Name,
        [string]$Value
    )

    $escapedName = [regex]::Escape($Name)
    $newLine = "$Name=$Value"

    if (Test-Path -LiteralPath $Path) {
        $lines = Get-Content -LiteralPath $Path
    } else {
        $lines = @()
    }

    $found = $false
    $updated = foreach ($line in $lines) {
        if ($line -match "^\s*$escapedName\s*=") {
            $found = $true
            $newLine
        } else {
            $line
        }
    }

    if (-not $found) {
        $updated += $newLine
    }

    Set-Content -LiteralPath $Path -Value $updated -Encoding UTF8
}

if (-not (Test-Path -LiteralPath ".\.venv\Scripts\python.exe")) {
    python -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

$currentPid = $PID
Get-CimInstance Win32_Process -Filter "Name = 'pythonw.exe' OR Name = 'python.exe'" |
    Where-Object {
        $_.ProcessId -ne $currentPid -and
        $_.CommandLine -and
        $_.CommandLine.Contains("ai_subtitle_win") -and
        $_.CommandLine.Contains($PSScriptRoot)
    } |
    ForEach-Object {
        Stop-Process -Id $_.ProcessId -Force
    }

$envPath = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path -LiteralPath $envPath)) {
    Copy-Item -LiteralPath ".\.env.example" -Destination $envPath
}

$provider = Get-EnvValue -Path $envPath -Name "TRANSLATION_PROVIDER"
if (-not $provider) {
    $provider = "deepseek"
    Set-EnvValue -Path $envPath -Name "TRANSLATION_PROVIDER" -Value $provider
}

$apiKey = Get-EnvValue -Path $envPath -Name "DEEPSEEK_API_KEY"
$needsDeepSeekKey = $provider.Trim().ToLowerInvariant() -eq "deepseek"
$hasPlaceholderKey = (-not $apiKey) -or $apiKey.Contains("deepseek_api_key") -or $apiKey.Contains("你的")

if ($needsDeepSeekKey -and $hasPlaceholderKey) {
    Write-Host ""
    Write-Host "需要填写 DeepSeek API Key，才能使用在线 AI 字幕翻译。"
    Write-Host "DeepSeek API Key is required for online AI subtitle translation."
    Write-Host ""
    Write-Host "你可以在这里获取 / Get one here:"
    Write-Host "https://platform.deepseek.com"
    Write-Host ""
    $secureKey = Read-Host "请粘贴你的 DeepSeek API Key / Please paste your DeepSeek API Key" -AsSecureString
    $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    )

    if (-not $plainKey) {
        throw "未输入 DEEPSEEK_API_KEY，启动已取消。 / DEEPSEEK_API_KEY was not entered. Startup canceled."
    }

    Set-EnvValue -Path $envPath -Name "DEEPSEEK_API_KEY" -Value $plainKey
}

$pythonw = Join-Path $PSScriptRoot ".venv\Scripts\pythonw.exe"
if (-not (Test-Path -LiteralPath $pythonw)) {
    $pythonw = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
}

Start-Process -FilePath $pythonw -ArgumentList "-m", "ai_subtitle_win" -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
