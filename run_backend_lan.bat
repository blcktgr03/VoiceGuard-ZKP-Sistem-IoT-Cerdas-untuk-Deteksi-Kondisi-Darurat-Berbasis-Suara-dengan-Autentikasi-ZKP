@echo off
REM Pastikan working directory berada di root proyek.
cd /d "%~dp0"

if defined VOICEGUARD_PYTHON (
    set "PYTHON_EXE=%VOICEGUARD_PYTHON%"
) else if exist "%USERPROFILE%\miniconda3\envs\tf-new\python.exe" (
    REM Pertahankan environment pengembangan lokal yang sudah digunakan proyek.
    set "PYTHON_EXE=%USERPROFILE%\miniconda3\envs\tf-new\python.exe"
) else if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
