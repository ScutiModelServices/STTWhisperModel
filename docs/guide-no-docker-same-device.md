# STTWhisperModel: without Docker, on Windows

Run Whisper on the CPU directly with Python: one process, no load balancer, listening on `127.0.0.1:9230`.

## Requirements
- Windows with Python 3.11 or newer and uv (`winget install astral-sh.uv`).
- Internet on the first start (about 150 MB of weights).
- RAM for the model (one copy).

## Start
Double-click `run.bat`, or run it in a terminal from `STTWhisperModel\`. It runs `uv sync` to create or update `.venv`, then starts
`python src/app.py`. The first start downloads about 150 MB of weights.

Linux or macOS:
```bash
cd STTWhisperModel
uv sync
uv run python src/app.py
```

## Settings
`run.bat` and `app.py` read the real environment, **not** `.env`. Set variables before starting:

| Variable | Default | Effect |
|---|---|---|
| `WHISPER_HOST` | `127.0.0.1` | Bind address. Use `0.0.0.0` only if other devices must reach it. |
| `WHISPER_PORT` | `9230` | Port. |
| `WHISPER_ADMIN_PASSWORD` | empty | Unlocks `/admin/` and requires tokens on every call but `/health`. Empty = no auth. |
| `WHISPER_WARM` | `1` | Load the model at start; with `0` the first request pays the load time. |
| `WHISPER_NUM_THREAD` | the library decides | CPU threads. Set it to the number of **physical** cores. |

PowerShell: `$env:WHISPER_ADMIN_PASSWORD = "secret"; .\run.bat`
Bash: `WHISPER_ADMIN_PASSWORD=secret uv run python src/app.py`

## Check
```bash
curl http://127.0.0.1:9230/health
```
`ready` is `false` until the model has loaded. Then open `http://127.0.0.1:9230/admin/` (see [guide-web-ui.md](guide-web-ui.md)),
make a token, and try a call:
```bash
ffmpeg -v error -i speech.wav -f s16le -ar 16000 -ac 1 - | curl -X POST http://127.0.0.1:9230/v1/transcribe -H "X-Internal-Token: whisper_..." --data-binary @-
```

## Stop
Ctrl+C in the terminal. Do not run this and the Docker stack together: both use port 9230.

## Tests
`uv run pytest`.
