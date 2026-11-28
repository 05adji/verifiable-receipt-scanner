import io
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageOps
from pydantic import BaseModel


class GateResult(BaseModel):
    accepted: bool
    blur_score: float
    reason: str
    image_bytes: bytes = b""


def check_and_prepare_image(
    image_path: str | Path,
    max_side: int = 1280,
    blur_threshold: float = 60.0,
) -> GateResult:
    """Auto-rotasi, kecilkan maks 1280px, lalu tolak jika terlalu buram."""
    with Image.open(image_path) as img:
        # 1. Auto-rotasi sesuai data EXIF HP & ubah ke RGB standar
        img = ImageOps.exif_transpose(img).convert("RGB")

        # 2. Resize jika sisi terpanjang lebih dari 1280px
        w, h = img.size
        if max(w, h) > max_side:
            scale = max_side / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

        # Simpan ke bytes JPEG agar siap dikirim ke API & di-hash
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        clean_bytes = buf.getvalue()

    # 3. Ubah ke format OpenCV hitam-putih untuk mengukur ketajaman (Laplacian)
    np_arr = np.frombuffer(clean_bytes, dtype=np.uint8)
    cv_img = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)
    blur_score = float(cv2.Laplacian(cv_img, cv2.CV_64F).var())

    if blur_score < blur_threshold:
        return GateResult(
            accepted=False,
            blur_score=round(blur_score, 2),
            reason=f"Foto terlalu buram (skor {blur_score:.1f} < {blur_threshold}).",
        )

    return GateResult(
        accepted=True,
        blur_score=round(blur_score, 2),
        reason="OK",
        image_bytes=clean_bytes,
    )