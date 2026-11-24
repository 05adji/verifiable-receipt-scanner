import json
from pathlib import Path
from datasets import load_dataset

OUT_IMAGES = Path("data/golden_set/images")
OUT_LABELS = Path("data/golden_set/labels.jsonl")
NUM_SAMPLES = 25

# streaming=True agar hanya mengunduh 25 struk, bukan ribuan sekaligus
dataset = load_dataset("naver-clova-ix/cord-v2", split="test", streaming=True)

with OUT_LABELS.open("w", encoding="utf-8") as f:
    for idx, row in enumerate(dataset):
        if idx >= NUM_SAMPLES:
            break

        filename = f"receipt_{idx + 1:03d}.jpg"
        row["image"].convert("RGB").save(OUT_IMAGES / filename)

        gt = json.loads(row["ground_truth"]).get("gt_parse", {})
        menu = gt.get("menu", [])
        # Kadang CORD menyimpan 1 barang sebagai dict, bukan list
        if isinstance(menu, dict):
            menu = [menu]

        record = {
            "id": f"receipt_{idx + 1:03d}",
            "image_path": f"data/golden_set/images/{filename}",
            "menu": menu,
            "sub_total": gt.get("sub_total", {}),
            "total": gt.get("total", {}),
        }
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

print(f"Selesai! {NUM_SAMPLES} struk dan labels.jsonl berhasil dibuat.")