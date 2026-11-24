from pathlib import Path
import cv2

SRC_DIR = Path("data/golden_set/images")
OUT_DIR = Path("data/golden_set/corrupted")

images = sorted(SRC_DIR.glob("*.jpg"))[:6]

for i, img_path in enumerate(images):
    img = cv2.imread(str(img_path))
    if img is None:
        continue

    if i < 3:
        # 3 foto pertama dibuat sangat buram (ujian deteksi blur)
        blurred = cv2.GaussianBlur(img, (31, 31), 0)
        out_name = f"blur_{img_path.name}"
        cv2.imwrite(str(OUT_DIR / out_name), blurred)
    else:
        # 3 foto berikutnya dimiringkan 25 derajat + agak buram
        h, w = img.shape[:2]
        matrix = cv2.getRotationMatrix2D((w / 2, h / 2), 25, 1.0)
        tilted = cv2.warpAffine(img, matrix, (w, h))
        tilted_blur = cv2.GaussianBlur(tilted, (15, 15), 0)
        out_name = f"tilted_{img_path.name}"
        cv2.imwrite(str(OUT_DIR / out_name), tilted_blur)

print("Selesai! 6 foto struk rusak (3 buram, 3 miring) berhasil dibuat.")