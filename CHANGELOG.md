# Changelog

## Unreleased

- First version: `faster-whisper` (`base.en`, int8) served on the CPU, with the admin page, tokens (rate limit,
  expiry), metrics, Settings card, update checks, weight downloads and answer cache shared with the other model
  services. Built from S1MiniModel.
- `POST /v1/transcribe` takes 16 kHz mono s16le PCM as the body and `language`, `beam_size`, `word_timestamps` and
  `stream` as query options. `stream=true` sends one JSON line per segment, then `done`.
- Settings: `max_seconds`, `vad_filter`, `compute_type` (and the shared ones).
