# Deploying STTWhisperModel

STTWhisperModel is one HTTP service (port 9230). It runs as `whisper` replicas behind an nginx load balancer,
`whisper_lb`. Callers use `http://<host>:9230`; they never reach a replica directly.

## Requirements

- Docker with Compose v2.
- About 0.5 GB of RAM **per replica** for `base.en` (each replica holds the model); `small.en` needs about 1 GB.
- Network access on the first start to download the weights (about 150 MB for `base.en`) from Hugging Face.
- CPU only (CTranslate2, int8).

## Settings

In `.env` next to `docker-compose.yml`:

| Variable | Default | Effect |
|---|---|---|
| `WHISPER_REPLICAS` | `1` | Number of `whisper` containers. Read by Compose. |
| `WHISPER_MEM_LIMIT` | `0` (no cap) | RAM cap per container, for example `1g` (`base.en` int8 uses about 0.3 GiB). An out-of-memory kill then stays in the container instead of starving the host. Read by Compose. |
| `WHISPER_PORT` | `9230` | Host port `whisper_lb` publishes. |
| `WHISPER_ADMIN_PASSWORD` | empty | Password for `/admin/`. When set, every call except `/health` must send a token as `X-Internal-Token`. Empty = no auth. |
| `WHISPER_NUM_THREAD` | CTranslate2 decides | Starting value for the CPU threads card; a value saved on `/admin/` wins. Use the number of physical cores (`lscpu`: cores x sockets), not logical CPUs; more threads than cores slows every call. Changing it reloads the model on that replica; the next call loads it again. |

On the **Settings** card of `/admin/` (saved in `settings.json` beside the tokens, shared by all replicas; a saved
value beats the environment variable named in brackets): update check hours (`WHISPER_UPDATE_CHECK_HOURS`, 6),
in-flight cap (`WHISPER_MAX_INFLIGHT`, 0 = 4), answers kept per replica (`WHISPER_CACHE_SIZE`, 256, 0 = off), longest audio per call (`WHISPER_MAX_SECONDS`, 150, at most 900), silence filter (`WHISPER_VAD_FILTER`, off), base model
(`WHISPER_MODEL`, restart; `base.en`, `small.en` or a Hugging Face repository of CTranslate2 files), number format (`WHISPER_COMPUTE_TYPE`, restart: `int8`, `int8_float32` or `float32`) and load at start (`WHISPER_WARM`, restart). Compose does not pass these; add the variable
under `environment:` of `whisper` to use one as a starting value.

## Start

```bash
docker compose up -d --build
curl http://127.0.0.1:9230/health
```

Expect `"ready": true` once a replica has loaded the model. The first start downloads the weights into the `models`
volume, so `whisper_lb` can take a few minutes to appear (the health check allows 300 s before failures count; run
`docker compose ps` and wait).

## Scaling

```bash
WHISPER_REPLICAS=3 docker compose up -d --build
docker compose restart whisper_lb
```

The restart is needed because nginx resolves replica addresses once at start.

## Updating the weights

The **Updates** card compares the downloaded revision of the Hugging Face repository with its newest one. **Download
new weights** fetches it into the models volume; every replica drops its old copy within a few seconds and loads the
new one on its next request (it needs RAM for both for a moment). The download is the repository's current `main`.
Updating the service itself: `docker compose up -d --build`, then `docker compose restart whisper_lb`.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `whisper_lb` never starts | No replica is healthy yet (first download, or out of memory). `docker compose logs whisper`. |
| Replicas restart in a loop | Out of RAM. Lower `WHISPER_REPLICAS`. |
| 401 "Invalid token" | The caller sends no token, or a revoked one. |
| 422 on `/v1/transcribe` | An empty body, an odd byte count (the body must be 16 kHz mono s16le PCM), an unknown query option, or a language other than `en` on a `.en` model. |
| 413 | The audio is longer than *Longest audio per call*. |
| 429 | Over the token's rate limit, or too many calls waiting for the model. |
| Slow answers | `base.en` runs at about 1.6x real time and `small.en` at about 0.5x on 6 cores. Use a smaller model, or set CPU threads on `/admin/` to the physical core count. |
| nginx 502 after scaling | `whisper_lb` not restarted after the replica count changed. |

## Releasing

A plain publish (`tools\deploy.bat` option 1) only updates the `live` branch. For a release set `VERSION` (and
`pyproject.toml` to the same number), commit, then run `tools\deploy.bat` option R or
`py tools\publish_live.py --release`. `tools\make_zip.bat` then builds `zip_versions\STTWhisperModel-<VERSION>.zip`.


## Verify with Try it

After deployment, open `/admin/` and use **Try it** with a public service token to exercise the deployed public route. It uses normal scope, admission/rate limits and cache behavior, so busy or unauthorized requests remain visible as HTTP errors. No new environment setting or admin-to-public auth bypass is introduced. Deploy the complete `web/` directory, including `playground.js`. See [the web UI guide](docs/guide-web-ui.md#try-it-send-a-real-request) for input formats, limits and token handling.
