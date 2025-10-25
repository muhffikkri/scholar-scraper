# CAPTCHA Handling Guide

## Overview

Sistem scraper dilengkapi dengan fitur **CAPTCHA Manual Solving** yang memungkinkan user untuk menyelesaikan CAPTCHA secara manual tanpa perlu restart script.

## Cara Kerja

### 1. Deteksi Otomatis

Script akan otomatis mendeteksi CAPTCHA saat:

- Setelah melakukan pencarian nama dosen
- Setelah mengklik profil dosen
- Saat membuka halaman detail publikasi

### 2. Penanganan CAPTCHA

Ketika CAPTCHA terdeteksi:

```
============================================================
⚠️  CAPTCHA TERDETEKSI!
============================================================
Silakan selesaikan CAPTCHA secara manual di browser.
Waktu tunggu maksimal: 5 menit
Script akan otomatis melanjutkan setelah CAPTCHA terselesaikan.
============================================================

⏳ Menunggu CAPTCHA diselesaikan... (04:58)
```

### 3. Alur Proses

1. **CAPTCHA Muncul** → Script pause dan tampilkan notifikasi
2. **User Solve CAPTCHA** → Selesaikan verifikasi di browser
3. **Script Monitoring** → Cek setiap 5 detik apakah CAPTCHA sudah selesai
4. **Auto Continue** → Script otomatis lanjut scraping
5. **Timeout Handling** → Jika tidak diselesaikan dalam waktu yang ditentukan, skip nama tersebut

## Konfigurasi

### Via GUI

Di bagian Settings:

- **CAPTCHA Timeout (menit)**: 1-15 menit (default: 5 menit)
- **Mode**: Gunakan "Browser Visible" (non-headless) untuk melihat CAPTCHA

### Via Code

```python
from src.core_logic.scraper import GoogleScholarScraper

scraper = GoogleScholarScraper(
    headless=False,  # Browser visible
    wait_time=10,
    captcha_wait_minutes=10  # 10 menit untuk solve CAPTCHA
)

df = scraper.run_scraper(dosen_names)
```

### Via main.py CLI

```bash
# Belum diimplementasikan - coming soon
python main.py --captcha-wait 10
```

## Best Practices

### 1. Gunakan Mode Non-Headless

```python
scraper = GoogleScholarScraper(headless=False)
```

Dengan mode ini, browser terlihat dan Anda bisa solve CAPTCHA langsung.

### 2. Sesuaikan Timeout

Untuk koneksi lambat atau CAPTCHA kompleks:

```python
scraper = GoogleScholarScraper(captcha_wait_minutes=10)
```

### 3. Monitor Log

Check file logging untuk melihat berapa banyak CAPTCHA yang muncul:

```bash
# Lihat summary
cat logging/summary_YYYYMMDD_HHMMSS.json

# Lihat daftar CAPTCHA blocks
cat logging/captcha_blocked_YYYYMMDD_HHMMSS.txt
```

### 4. Strategi Avoid CAPTCHA

**Jika CAPTCHA sering muncul:**

1. **Tambah Delay Antar Dosen**

   - Default: 2 detik
   - Recommended: 5-10 detik

2. **Kurangi Batch Size**

   - Scrape 5-10 dosen per session
   - Jeda 30-60 menit antar batch

3. **Gunakan Proxy/VPN**

   - Rotate IP address
   - Gunakan residential proxy

4. **Scrape di Jam Low Traffic**
   - Hindari jam 9-17 (working hours)
   - Preferensi: malam atau weekend

## Troubleshooting

### CAPTCHA Tidak Muncul di Browser

**Problem:** Headless mode aktif

**Solution:**

```python
scraper = GoogleScholarScraper(headless=False)
```

### Timeout Terlalu Cepat

**Problem:** CAPTCHA kompleks butuh waktu > 5 menit

**Solution:**

```python
scraper = GoogleScholarScraper(captcha_wait_minutes=15)
```

### CAPTCHA Terus Muncul

**Problem:** Google mendeteksi bot activity

**Solutions:**

1. Tambah delay antar request
2. Kurangi volume scraping
3. Gunakan proxy
4. Wait 24 jam sebelum retry

### Script Hang di CAPTCHA

**Problem:** Detection loop gagal

**Solution:**

- Ctrl+C untuk cancel
- Check internet connection
- Restart script dengan timeout lebih pendek

## Testing

### Test Manual CAPTCHA Handling

```bash
python test_captcha_handling.py
```

Script ini akan:

1. Open browser (non-headless)
2. Scrape satu nama dosen
3. Jika CAPTCHA muncul, beri waktu untuk solve
4. Tampilkan hasil

### Test dengan Mock CAPTCHA

```python
# Coming soon - unit test untuk CAPTCHA detection
```

## Logging

### CAPTCHA Events Logged

Semua event CAPTCHA dicatat di:

1. **Summary JSON** (`logging/summary_*.json`)

   ```json
   {
     "statistics": {
       "captcha_count": 3
     },
     "captcha_list": ["Dr. Ahmad", "Prof. Budi", "Dr. Citra"]
   }
   ```

2. **Detailed Log CSV** (`logging/detailed_log_*.csv`)

   - Error Type: CAPTCHA
   - Error Message: "CAPTCHA not solved within timeout"

3. **CAPTCHA Blocked File** (`logging/captcha_blocked_*.txt`)
   - List nama yang kena CAPTCHA
   - Rekomendasi untuk retry

## Integration dengan Workflow

### Workflow Normal (No CAPTCHA)

```
Search → Find Profile → Scrape Publications → Success
```

### Workflow dengan CAPTCHA

```
Search → CAPTCHA Detected → Wait for Manual Solve →
  → CAPTCHA Solved → Continue Scraping → Success
  → Timeout → Skip → Log Failed → Continue Next
```

## API Reference

### Method: `_check_for_captcha()`

Deteksi CAPTCHA di halaman current.

**Returns:** `bool` - True if CAPTCHA detected

### Method: `_wait_for_captcha_solve(max_wait_minutes)`

Tunggu user solve CAPTCHA.

**Parameters:**

- `max_wait_minutes` (int): Timeout dalam menit (default: from `self.captcha_wait_minutes`)

**Returns:** `bool` - True if solved, False if timeout

**Behavior:**

- Check setiap 5 detik
- Display countdown timer
- Auto continue when solved

## Future Enhancements

Planned improvements:

1. **Audio Alert** - Beep when CAPTCHA appears
2. **Email/SMS Notification** - Alert ke phone saat CAPTCHA
3. **Auto-Retry** - Retry failed CAPTCHA setelah delay
4. **CAPTCHA Solver API** - Integration dengan 2captcha/anti-captcha
5. **Smart Delay** - Dynamic delay based on CAPTCHA frequency
6. **Session Persistence** - Save session untuk resume setelah CAPTCHA

## Support

Jika mengalami masalah dengan CAPTCHA handling:

1. Check dokumentasi ini
2. Review log files di `logging/`
3. Test dengan `test_captcha_handling.py`
4. Adjust timeout settings
5. Consider proxy/VPN solution
