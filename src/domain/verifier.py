from pydantic import BaseModel, Field
from src.domain.schemas import ReceiptData


class VerificationResult(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)


def verify_receipt(receipt: ReceiptData) -> VerificationResult:
    """Cek 4 aturan matematika dasar pada data struk."""
    errors: list[str] = []

    # Aturan 1: Cek harga satuan x jumlah per baris barang
    for idx, item in enumerate(receipt.items, start=1):
        if item.unit_price is not None:
            expected_line = item.unit_price * item.qty
            if expected_line != item.line_total:
                errors.append(
                    f"Baris {idx} ({item.name}): {item.unit_price} x {item.qty} = "
                    f"{expected_line}, tetapi tertulis {item.line_total}."
                )

    # Aturan 2: Cek jumlah seluruh barang harus sama dengan subtotal
    items_sum = sum(item.line_total for item in receipt.items)
    if receipt.items and receipt.subtotal is not None:
        if items_sum != receipt.subtotal:
            errors.append(
                f"Subtotal tidak cocok: jumlah barang = {items_sum}, "
                f"tetapi subtotal tertulis {receipt.subtotal}."
            )


# Aturan 3: Cek Grand Total sesuai mode pajak (exclusive/inclusive/none) + pembulatan
    base_amount = receipt.subtotal if receipt.subtotal is not None else (
        items_sum if receipt.items else None
    )
    if base_amount is not None:
        if receipt.tax_mode == "exclusive":
            expected_total = base_amount + receipt.tax + receipt.rounding
        else:
            # Untuk 'inclusive' dan 'none', pajak tidak ditambahkan lagi ke base_amount
            expected_total = base_amount + receipt.rounding

        if expected_total != receipt.total:
            errors.append(
                f"Grand total tidak cocok (mode {receipt.tax_mode}): "
                f"hitungan benar = {expected_total}, tetapi tertulis {receipt.total}."
            )

    # Aturan 4: Cek silang tunai - total = kembalian
    if receipt.cash_paid is not None and receipt.change is not None:
        expected_change = receipt.cash_paid - receipt.total
        if expected_change != receipt.change:
            errors.append(
                f"Kembalian tidak cocok: {receipt.cash_paid} - {receipt.total} = "
                f"{expected_change}, tetapi tertulis {receipt.change}."
            )

    return VerificationResult(is_valid=len(errors) == 0, errors=errors)