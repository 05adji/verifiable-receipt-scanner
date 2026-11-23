# Architecture RFC: Verifiable Receipt Scanner

## 1. Masalah yang Diselesaikan
AI pembaca gambar sering salah baca atau mengarang angka saat membaca struk belanja.
Contoh kasus nyata pada struk:
- Air Mineral: `8. 000 x 2 = 16.000` (ada spasi di tengah angka)
- PPN 12%: `1.920`
- Pembulatan: `(20)` (tanda kurung berarti minus `-20`)
- Total seharusnya: `16.000 + 1.920 - 20 = 17.900`

Jika AI salah membaca total menjadi `17.920` atau `16.000`, sistem tidak boleh langsung percaya begitu saja.

## 2. Alur Inti Sistem
Foto Struk -> Cek Buram (OpenCV) -> Disk Cache (SHA-256) -> Ekstraktor (Baseline RapidOCR+Regex vs Free Vision API, plus opsi Lokal 4 GB VRAM) -> Pembersih Rupiah & Pydantic v2 -> Deterministic Math Verifier -> Maksimal 1x Retry jika selisih -> Status `VERIFIED` atau `NEEDS_HUMAN_REVIEW` -> Backend FastAPI -> UI Streamlit.

## 3. Metrik Sukses (Target Evaluasi)
1. **Exact Match**: Persentase struk yang seluruh angka utamanya cocok persis dengan jawaban benar (`labels.jsonl`).
2. **Arithmetic Consistency Rate**: Persentase struk yang lolos 4 aturan cek matematika Python (harga x qty, subtotal, pajak+pembulatan, dan tunai - kembali).
3. **Abstention Precision (Foto Buram)**: Kemampuan menolak foto buram/miring sejak awal sebelum membakar kuota AI.
4. **Latensi**: Waktu proses rata-rata per struk (detik).