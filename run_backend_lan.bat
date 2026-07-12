@echo off
cd /d "%~dp0"
"C:\Users\L E N O V O\miniconda3\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
