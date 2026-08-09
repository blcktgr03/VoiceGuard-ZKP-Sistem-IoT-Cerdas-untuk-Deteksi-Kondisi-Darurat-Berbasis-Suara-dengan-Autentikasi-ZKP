@echo off
REM Pindah ke root proyek berdasarkan lokasi file batch ini.
cd /d "%~dp0.."
REM Jalankan notebook dengan environment tf-new dan simpan output ke folder dataset.
"%USERPROFILE%\miniconda3\envs\tf-new\python.exe" "dataset\run_full_finetune_indobert.py" >> "dataset\full_finetune_indobert_stdout.log" 2>> "dataset\full_finetune_indobert_stderr.log"
