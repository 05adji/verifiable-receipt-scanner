import re
from pathlib import Path
from rapidocr_onnxruntime import RapidOCR
from src.domain.schemas import ReceiptData, ReceiptItem, parse_idr_int

_ocr_engine = RapidOCR()


def _find_amount_near_keyword(lines: list[str], keywords: tuple[str, ...]) -> int | None:
    """Cari angka Rupiah di baris yang mengandung kata kunci tertentu."""
    for line in lines:
        upper = line.upper()
        if any(kw in upper for kw in keywords):
            matches = re.findall(r"\d[\d.,\s]*\d|\d+", line)
            if matches:
                try:
                    return parse_idr_int(matches[-1])
                except ValueError:
                    continue
    return None


def extract_with_baseline(image_path: str | Path) -> ReceiptData | None:
    """Ekstraksi struk sederhana: RapidOCR + pencarian kata kunci Regex."""
    result, _ = _ocr_engine(str(image_path))
    if not result:
        return None

    lines = [row[1] for row in result if row and len(row) >= 2]
    total = _find_amount_near_keyword(lines, ("GRAND TOTAL", "TOTAL", "JUMLAH"))
    subtotal = _find_amount_near_keyword(lines, ("SUBTOTAL", "SUB TOTAL"))
    tax = _find_amount_near_keyword(lines, ("PPN", "TAX", "PB1")) or 0

    # Jika kata 'TOTAL' tidak terbaca OCR, tebak pakai angka terbesar yang ditemukan
    if total is None:
        all_nums: list[int] = []
        for line in lines:
            for m in re.findall(r"\d[\d.,]*\d", line):
                try:
                    all_nums.append(parse_idr_int(m))
                except ValueError:
                    pass
        if not all_nums:
            return None
        total = max(all_nums)

    # Baseline sederhana menaruh 1 item dummy jika subtotal ada, agar bisa diuji verifier
    items = [ReceiptItem(name="item_ocr", qty=1, line_total=subtotal)] if subtotal else []
    return ReceiptData(items=items, subtotal=subtotal, tax=tax, total=total)