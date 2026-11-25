import re
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


def parse_idr_int(value: int | str) -> int:
    """Ubah teks Rupiah ('Rp 16.000', '8. 000', '(20)') jadi integer murni."""
    if isinstance(value, int) and not isinstance(value, bool):
        return value

    text = str(value).strip()
    if not text:
        raise ValueError("Nilai harga tidak boleh kosong.")

    # Tanda kurung seperti '(20)' atau '-' berarti angka negatif
    is_negative = ("(" in text and ")" in text) or ("-" in text)

    # Buang akhiran ',00' atau '.00' supaya '16.000,00' tidak berubah jadi 1600000
    text = re.sub(r"[.,]00$", "", text)

    # Buang semua karakter selain angka 0-9 ('Rp', titik, koma, spasi nyasar)
    digits = re.sub(r"\D", "", text)
    if not digits:
        raise ValueError(f"Tidak ada angka yang valid pada: {value!r}")

    amount = int(digits)
    return -amount if is_negative else amount


class ReceiptItem(BaseModel):
    name: str = Field(..., min_length=1)
    qty: int = Field(default=1, ge=1)
    unit_price: Optional[int] = None
    line_total: int

    @field_validator("unit_price", mode="before")
    @classmethod
    def clean_optional_price(cls, v):
        if v is None or str(v).strip() == "":
            return None
        return parse_idr_int(v)

    @field_validator("line_total", mode="before")
    @classmethod
    def clean_line_total(cls, v):
        return parse_idr_int(v)


class ReceiptData(BaseModel):
    merchant: Optional[str] = None
    items: list[ReceiptItem] = Field(default_factory=list)
    subtotal: Optional[int] = None
    tax: int = 0
    tax_mode: Literal["exclusive", "inclusive", "none"] = "exclusive"
    rounding: int = 0
    total: int
    cash_paid: Optional[int] = None
    change: Optional[int] = None

    @field_validator("subtotal", "cash_paid", "change", mode="before")
    @classmethod
    def clean_optional_amounts(cls, v):
        if v is None or str(v).strip() == "":
            return None
        return parse_idr_int(v)

    @field_validator("tax", "rounding", mode="before")
    @classmethod
    def clean_zero_default_amounts(cls, v):
        if v is None or str(v).strip() == "":
            return 0
        return parse_idr_int(v)

    @field_validator("total", mode="before")
    @classmethod
    def clean_total(cls, v):
        return parse_idr_int(v)