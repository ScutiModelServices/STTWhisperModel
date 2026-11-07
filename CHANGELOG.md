# Changelog

## Unreleased

- Renamed `STTWhisperModel` to `STT_Whisper_Model`; Docker project, API image, services, load balancer and volumes now use `stt_whisper_model` names. Callers on `citadel_core` connect to `stt_whisper_model_lb` at the existing port.
- Docker volume migration: existing volumes with old names are orphaned; renaming does not move data. Stop the old stack before copying; never use `down -v`. The commands below assume the previous default Compose project name; substitute actual volume names if `-p` or `COMPOSE_PROJECT_NAME` overrode it.
  - `whisper_models` → `stt_whisper_model_models`: `docker volume inspect whisper_models && docker volume create stt_whisper_model_models && docker run --rm -v whisper_models:/from:ro -v stt_whisper_model_models:/to alpine:3.21 sh -c "cd /from && cp -a . /to/"`
  - `whisper_tokens` → `stt_whisper_model_data`: `docker volume inspect whisper_tokens && docker volume create stt_whisper_model_data && docker run --rm -v whisper_tokens:/from:ro -v stt_whisper_model_data:/to alpine:3.21 sh -c "cd /from && cp -a . /to/"`
- To retain an old volume instead, set its top-level volume definition to `external: true` and `name: <old-volume-name>` in a local Compose override. Rollback: stop the renamed stack, restore the previous checkout and folder name, and restart the old stack with its original volumes; copy back newer data first if the renamed stack accepted writes.

- `run.bat` loads `.env` from the service folder for a local run: it passes `--dotenv`, the service prints which variable names it loaded (never the values), and a real environment variable still wins. A plain `python src/app.py` and Docker never read `.env`.
- Untracked folders now start with `.` or `_`: `zip_versions/` is `_zip_versions/`. A local `voices`, `tem_code` or `zip_versions` folder from an older checkout needs renaming by hand.
- `run.bat` is now a menu (run the service, deploy, build the release ZIP) and `run.bat run|deploy|zip` skips it. `tools/deploy.bat`, `tools/make_zip.bat` and `tools/deploy.local.example.bat` are gone; the local deploy target is `tools/deploy.local.ini` (copy `tools/deploy.local.example.ini`).
- Admin page: **Connect to this service** card with the addresses other services can use (this page's address, same PC, Docker network, `host.docker.internal`) and every endpoint, each with a Copy button.
- Admin **Try it** panel: descriptor-driven public API requests, live text streams, JSON/media output, status and latency, cancellation and redacted curl. Auth choice (b): pasted public token stays in memory; normal scope, limits and caches apply. Shared `web/playground.js` is copied across all model and tool services.
- Corrected the external `faster_whisper.STT_Whisper_Model` loader name so real transcription works after the service rename.

- First version: `faster-whisper` (`base.en`, int8) served on the CPU, with the admin page, tokens (rate limit,
  expiry), metrics, Settings card, update checks, weight downloads and answer cache shared with the other model
  services. Built from STC_S1Mini_Model.
- `POST /v1/transcribe` takes 16 kHz mono s16le PCM as the body and `language`, `beam_size`, `word_timestamps` and
  `stream` as query options. `stream=true` sends one JSON line per segment, then `done`.
- Settings: `max_seconds`, `vad_filter`, `compute_type` (and the shared ones).
