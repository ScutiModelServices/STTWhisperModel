"""The options the admin page can change. Each can still start from its environment variable; a saved value wins."""

from engine import COMPUTE_TYPES, DEFAULT_MODEL
from settings import Setting

SETTINGS = [
    Setting("update_check_hours", "Check for updates every (hours)", "float", 6.0, "WHISPER_UPDATE_CHECK_HOURS", 0, 720,
            help="0 = only when you press Check now"),
    Setting("max_inflight", "Calls allowed to wait for the model", "int", 0, "WHISPER_MAX_INFLIGHT", 0, 10000,
            help="Per replica; more get 429. 0 = 4"),
    Setting("cache_size", "Answers kept per replica", "int", 256, "WHISPER_CACHE_SIZE", 0, 100000,
            help="The last answers for the same audio and options, sent again without transcribing. Decoding is deterministic, so every request is kept. 0 = off"),
    Setting("max_seconds", "Longest audio per call (seconds)", "int", 150, "WHISPER_MAX_SECONDS", 1, 900,
            help="Longer audio gets 413. Keep it under what the caller's own timeout allows at the model's speed"),
    Setting("vad_filter", "Skip silence before decoding", "bool", False, "WHISPER_VAD_FILTER",
            help="Voice activity filter. Off matches the old in-process Scribe"),
    Setting("model", "Base model", "text", DEFAULT_MODEL, "WHISPER_MODEL", restart=True, blank=False,
            help="A faster-whisper name such as base.en or small.en, or a Hugging Face repository of CTranslate2 files. After a restart, download it from the Updates card"),
    Setting("compute_type", "Number format", "text", "int8", "WHISPER_COMPUTE_TYPE", restart=True, blank=False,
            help=f"One of {', '.join(COMPUTE_TYPES)}. int8 is the fastest on a CPU; float32 uses about four times the memory"),
    Setting("warm", "Load the model at start", "bool", True, "WHISPER_WARM", restart=True),
]
