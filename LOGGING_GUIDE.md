# Logging System Documentation

## Gambaran Umum

Sistem logging ini dirancang untuk mencatat semua aktivitas scraping Google Scholar, termasuk keberhasilan, kegagalan, dan deteksi CAPTCHA. Semua log disimpan di folder `logging/`.

## Struktur File Log

Setiap session scraping menghasilkan 4 jenis file dengan format nama berdasarkan Session ID (`YYYYMMDD_HHMMSS`):

### 1. Summary File (JSON)

**Format:** `summary_[SessionID].json`

Berisi ringkasan lengkap session:

```json
{
  "session_info": {
    "session_id": "20251025_085313",
    "start_time": "2025-10-25 08:53:13",
    "end_time": "2025-10-25 08:53:16",
    "duration_seconds": 2.504597
  },
  "statistics": {
    "total_dosen": 5,
    "success_count": 3,
    "failed_count": 2,
    "captcha_count": 1,
    "success_rate": "60.00%"
  },
  "dosen_processed": [...],
  "success_list": [...],
  "failed_list": [...],
  "captcha_list": [...]
}
```

### 2. Detailed Log (CSV)

**Format:** `detailed_log_[SessionID].csv`

Log detail per dosen dengan kolom:

- `timestamp`: Waktu proses
- `nama_dosen`: Nama dosen yang diproses
- `status`: SUCCESS atau FAILED
- `publications_count`: Jumlah publikasi (untuk success)
- `error_type`: Tipe error (untuk failed): CAPTCHA, PROFILE_NOT_FOUND, SEARCH_FAILED, SCRAPING_ERROR
- `error_message`: Pesan error detail
- `detail`: Informasi tambahan (misal: URL profil)

### 3. Failed Names (TXT)

**Format:** `failed_names_[SessionID].txt`

Daftar nama yang gagal di-scrape dengan detail error:

```
FAILED SCRAPING - Session: 20251025_085313
Generated: 2025-10-25 08:53:16
Total Failed: 2
============================================================

1. Dr. Citra Dewi
   Error Type: CAPTCHA
   Error Message: CAPTCHA verification required

2. Prof. Eka Wijaya
   Error Type: PROFILE_NOT_FOUND
   Error Message: Profile not found in search results
```

### 4. CAPTCHA Blocked Names (TXT)

**Format:** `captcha_blocked_[SessionID].txt`

Daftar khusus nama yang terkena CAPTCHA dengan rekomendasi:

```
CAPTCHA BLOCKED - Session: 20251025_085313
Generated: 2025-10-25 08:53:16
Total CAPTCHA Blocks: 1
============================================================

REKOMENDASI:
1. Jalankan ulang scraping untuk nama-nama ini dengan delay lebih lama
2. Gunakan mode non-headless untuk manual CAPTCHA solving
3. Pertimbangkan menggunakan proxy atau VPN
============================================================

1. Dr. Citra Dewi
```

## Tipe Error yang Dideteksi

### 1. CAPTCHA

Google Scholar mendeteksi aktivitas otomatis dan meminta verifikasi CAPTCHA.

**Indikator:**

- Teks "recaptcha", "captcha", "unusual traffic" di halaman
- iframe reCAPTCHA
- Element `gs_captcha_ccl`

**Penanganan Otomatis:**

- Script akan MENDETEKSI CAPTCHA dan MENUNGGU user untuk solve secara manual
- Default timeout: 5 menit (dapat diatur di GUI atau parameter `captcha_wait_minutes`)
- Browser akan tetap terbuka (jika non-headless) untuk manual solving
- Script otomatis melanjutkan setelah CAPTCHA terselesaikan
- Jika timeout, nama akan di-skip dan dicatat di log

**Solusi:**

- **Otomatis:** Gunakan mode non-headless (`headless=False`) agar dapat solve CAPTCHA manual
- Tambah `captcha_wait_minutes` jika butuh waktu lebih lama
- Jika sering kena CAPTCHA: tambah delay antar request, kurangi batch size
- Gunakan proxy/VPN jika CAPTCHA terus muncul

### 2. PROFILE_NOT_FOUND

Profil dosen tidak ditemukan di hasil pencarian.

**Penyebab:**

- Nama salah/tidak terdaftar di Google Scholar
- Profil belum dibuat

**Solusi:**

- Cek ejaan nama
- Verifikasi nama di Google Scholar manual

### 3. SEARCH_FAILED

Gagal melakukan pencarian.

**Penyebab:**

- Koneksi timeout
- Element tidak ditemukan

**Solusi:**

- Cek koneksi internet
- Tambah wait time

### 4. SCRAPING_ERROR

Error umum saat proses scraping.

**Penyebab:**

- Koneksi terputus
- Element berubah
- Timeout

**Solusi:**

- Retry dengan delay
- Update script jika struktur HTML berubah

## Penggunaan

### Otomatis (via GUI atau run_scraper)

Logger diaktifkan otomatis saat menjalankan scraper:

```python
from src.core_logic.scraper import GoogleScholarScraper

scraper = GoogleScholarScraper(headless=True, wait_time=10)
df = scraper.run_scraper(dosen_list, years=[2020, 2021, 2022])
```

Logger akan otomatis:

1. Membuat session baru
2. Log setiap proses
3. Simpan hasil di akhir session

### Manual Testing

Untuk test logger tanpa scraping:

```bash
python test_logger.py
```

## Output Console

Saat scraping berjalan, console akan menampilkan:

```
============================================================
LOGGING SESSION STARTED
============================================================
Session ID: 20251025_085313
Start Time: 2025-10-25 08:53:13
Total Dosen: 5
Log Directory: logging
============================================================

✅ SUCCESS: Dr. Ahmad Sutanto (15 publikasi)
✅ SUCCESS: Prof. Budi Santoso (23 publikasi)
🤖 CAPTCHA: Dr. Citra Dewi - CAPTCHA verification required
✅ SUCCESS: Dr. Dedi Rahman (8 publikasi)
❌ PROFILE_NOT_FOUND: Prof. Eka Wijaya - Profile not found

============================================================
SCRAPING SUMMARY
============================================================
Total: 5 dosen
Success: 3 dosen
Failed: 2 dosen
CAPTCHA: 1 dosen
Success Rate: 60.0%
============================================================
```

## Best Practices

### 1. Monitor CAPTCHA Rate

Jika CAPTCHA rate > 20%, lakukan:

- Tambah delay antar dosen (3-5 detik)
- Kurangi jumlah dosen per batch
- Gunakan mode non-headless

### 2. Retry Failed Names

Untuk nama yang gagal (non-CAPTCHA):

- Extract dari `failed_names_*.txt`
- Buat file input baru dengan nama tersebut
- Jalankan ulang dengan wait time lebih lama

### 3. Handle CAPTCHA Manually

Untuk nama dengan CAPTCHA:

- Extract dari `captcha_blocked_*.txt`
- Jalankan dengan mode headless=False
- Solve CAPTCHA manual saat muncul

### 4. Analyze Patterns

Gunakan detailed_log CSV untuk:

- Identifikasi waktu peak CAPTCHA
- Analisis success rate per batch
- Optimize timing dan delay

## File Management

### Retention Policy

- Keep logs minimal 30 hari
- Archive logs lama ke folder terpisah
- Backup logs penting

### File Location

```
logging/
  ├── .gitkeep
  ├── summary_YYYYMMDD_HHMMSS.json
  ├── detailed_log_YYYYMMDD_HHMMSS.csv
  ├── failed_names_YYYYMMDD_HHMMSS.txt
  └── captcha_blocked_YYYYMMDD_HHMMSS.txt
```

### Git Ignore

Log files tidak di-commit ke git (lihat `.gitignore`):

```
logging/*.json
logging/*.csv
logging/*.txt
!logging/.gitkeep
```

## Troubleshooting

### Logger tidak membuat file

**Masalah:** Folder `logging/` tidak ada atau tidak writable

**Solusi:**

```bash
mkdir logging
# Atau jalankan: python -c "import os; os.makedirs('logging', exist_ok=True)"
```

### File CSV corrupt

**Masalah:** Encoding issue

**Solusi:** File disimpan dengan encoding `utf-8-sig` untuk support Excel

### JSON tidak valid

**Masalah:** Special character di nama dosen

**Solusi:** JSON disave dengan `ensure_ascii=False`

## Integration dengan GUI

GUI akan menampilkan:

- Real-time log status (success/failed/captcha)
- Summary di akhir scraping
- Link ke log files

## API Reference

### ScraperLogger Class

```python
from src.core_logic.logger import ScraperLogger

# Initialize
logger = ScraperLogger(log_dir="logging")

# Start session
logger.start_session(dosen_list)

# Log events
logger.log_success(nama_dosen, publications_count, detail_msg)
logger.log_failure(nama_dosen, error_msg, error_type)

# End session
summary = logger.end_session()

# Get summary anytime
current_summary = logger.get_summary()
```

### Error Types Enum

- `"SUCCESS"`: Scraping berhasil
- `"CAPTCHA"`: Blocked oleh CAPTCHA
- `"PROFILE_NOT_FOUND"`: Profil tidak ditemukan
- `"SEARCH_FAILED"`: Pencarian gagal
- `"SCRAPING_ERROR"`: Error umum

## Future Enhancements

Planned improvements:

1. Dashboard web untuk visualisasi logs
2. Email notification untuk CAPTCHA blocks
3. Auto-retry mechanism untuk failed scrapes
4. Export logs ke database
5. Analytics dan reporting tools
