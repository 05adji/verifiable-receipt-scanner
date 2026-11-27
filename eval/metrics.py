from src.domain.schemas import ReceiptData, parse_idr_int
from src.domain.verifier import verify_receipt


def get_ground_truth_total(record: dict) -> int | None:
    """Ambil total belanja yang benar dari 1 baris labels.jsonl."""
    raw_total = record.get("total", {}).get("total_price")
    if not raw_total:
        return None
    try:
        return parse_idr_int(raw_total)
    except ValueError:
        return None


def is_exact_total_match(pred: ReceiptData | None, gt_total: int | None) -> bool:
    if pred is None or gt_total is None:
        return False
    return pred.total == gt_total


def is_arithmetically_consistent(pred: ReceiptData | None) -> bool:
    if pred is None:
        return False
    return verify_receipt(pred).is_valid