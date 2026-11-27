import json
import time
from pathlib import Path
from eval.metrics import (
    get_ground_truth_total,
    is_arithmetically_consistent,
    is_exact_total_match,
)
from src.extractors.baseline_regex import extract_with_baseline

LABELS_PATH = Path("data/golden_set/labels.jsonl")


def main():
    records = [
        json.loads(line)
        for line in LABELS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    exact_hits = 0
    valid_math = 0
    total_time = 0.0

    for rec in records:
        start = time.perf_counter()
        pred = extract_with_baseline(rec["image_path"])
        total_time += time.perf_counter() - start

        gt_total = get_ground_truth_total(rec)
        if is_exact_total_match(pred, gt_total):
            exact_hits += 1
        if is_arithmetically_consistent(pred):
            valid_math += 1

    n = len(records)
    print(f"Total struk diuji          : {n}")
    print(f"Exact Match (Total)        : {exact_hits}/{n} ({exact_hits / n:.1%})")
    print(f"Arithmetic Consistency     : {valid_math}/{n} ({valid_math / n:.1%})")
    print(f"Rata-rata Latensi / Struk  : {total_time / n:.2f} detik")


if __name__ == "__main__":
    main()