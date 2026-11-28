import hashlib
import json
import time
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")
CACHE_DIR = Path(".cache")


def get_image_sha256(image_bytes: bytes) -> str:
    """Buat sidik jari unik (64 huruf/angka) dari isi gambar."""
    return hashlib.sha256(image_bytes).hexdigest()


def load_from_cache(cache_key: str) -> dict | None:
    """Ambil hasil JSON dari folder .cache jika sudah pernah diproses."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if not cache_file.exists():
        return None
    return json.loads(cache_file.read_text(encoding="utf-8"))


def save_to_cache(cache_key: str, data: dict) -> None:
    """Simpan hasil JSON ke folder .cache dengan nama file sidik jari SHA-256."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    cache_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def call_with_backoff(
    fn: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 2.0,
) -> T:
    """Jalankan fungsi API; jika kena limit 429, tunggu bertahap (2s, 4s, 8s)."""
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception as exc:
            msg = str(exc).lower()
            is_rate_limit = "429" in msg or "rate limit" in msg or "quota" in msg
            if not is_rate_limit or attempt == max_retries:
                raise
            wait_seconds = base_delay * (2 ** attempt)
            print(f"[Limit API 429] Menunggu {wait_seconds:.0f} detik sebelum coba lagi...")
            time.sleep(wait_seconds)