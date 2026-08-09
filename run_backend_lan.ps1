# Jalankan selalu dari root proyek agar seluruh path relatif tetap valid.
Set-Location -LiteralPath $PSScriptRoot

if ($env:VOICEGUARD_PYTHON) {
    $pythonExe = $env:VOICEGUARD_PYTHON
} elseif (Test-Path -LiteralPath "$env:USERPROFILE\miniconda3\envs\tf-new\python.exe") {
    # Pertahankan environment pengembangan lokal yang sudah digunakan proyek.
    $pythonExe = "$env:USERPROFILE\miniconda3\envs\tf-new\python.exe"
} elseif (Test-Path -LiteralPath "$PSScriptRoot\.venv\Scripts\python.exe") {
    $pythonExe = "$PSScriptRoot\.venv\Scripts\python.exe"
} else {
    $pythonExe = "python"
}

& $pythonExe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
