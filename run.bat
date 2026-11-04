@echo off
REM Starts the Whisper service on port 9230 (syncs .venv with uv on each run). The first start downloads the weights (about 150 MB).
REM LABEL: Whisper Service
REM DESCRIPTION: Shared HTTP service that runs Whisper on the CPU for every project.

cd /d "%~dp0"

uv sync
if errorlevel 1 (
    echo uv sync failed. Install uv: winget install astral-sh.uv
    pause
    exit /b 1
)
call .venv\Scripts\activate

python src/app.py
pause
