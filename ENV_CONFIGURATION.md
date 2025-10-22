# Panduan Konfigurasi Environment (.env)

## 📋 Daftar Isi

1. [Pengenalan](#pengenalan)
2. [Setup File .env](#setup-file-env)
3. [Konfigurasi Wajib](#konfigurasi-wajib)
4. [Konfigurasi Opsional](#konfigurasi-opsional)
5. [Troubleshooting](#troubleshooting)

---

## Pengenalan

File `.env` digunakan untuk menyimpan konfigurasi penting aplikasi seperti:

- **URL Apps Script** untuk upload data ke Google Sheets
- **Pengaturan default** aplikasi (timeout, mode headless, dll)
- **Konfigurasi output** (folder, format, dll)

File ini **TIDAK** akan di-commit ke Git repository untuk keamanan.

---

## Setup File .env

### 1. Copy Template

Gunakan file `.env.example` sebagai template:

```bash
cp .env.example .env
```

Atau di Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 2. Edit Konfigurasi

Buka file `.env` dengan text editor favorit Anda dan isi nilai konfigurasi yang diperlukan.

---

## Konfigurasi Wajib

### `APPS_SCRIPT_URL`

**Deskripsi**: URL Web App dari Google Apps Script untuk upload data ke Google Sheets.

**Format**:

```
APPS_SCRIPT_URL=https://script.google.com/macros/s/XXXXXXXXXXXXXXXXXXXXXXXX/exec
```

**Cara Mendapatkan**:

1. Buka [Google Apps Script](https://script.google.com)
2. Buat project baru atau gunakan existing project
3. Copy kode dari file `apps-script-web-app.gs` di project ini
4. Klik **Deploy** → **New Deployment**
5. Pilih:
   - **Type**: Web app
   - **Execute as**: Me
   - **Who has access**: Anyone
6. Klik **Deploy**
7. Copy **Web app URL** yang diberikan
8. Paste ke `.env` file

**Contoh**:

```env
APPS_SCRIPT_URL=https://script.google.com/macros/s/AKfycbx1234567890abcdefghijklmnop/exec
```

> ⚠️ **PENTING**: Jangan share URL ini ke orang lain! Simpan dengan aman.

---

## Konfigurasi Opsional

### `DEFAULT_SHEET_NAME`

**Deskripsi**: Nama sheet default di Google Spreadsheet untuk upload data.

**Default**: `Publikasi Dosen`

**Contoh**:

```env
DEFAULT_SHEET_NAME=Data Publikasi
```

---

### `DEFAULT_WAIT_TIME`

**Deskripsi**: Waktu tunggu default untuk loading halaman web (dalam detik).

**Default**: `10`

**Range**: 5 - 30 detik

**Contoh**:

```env
DEFAULT_WAIT_TIME=15
```

**Tips**:

- Koneksi lambat: gunakan 15-20 detik
- Koneksi cepat: gunakan 5-10 detik

---

### `DEFAULT_HEADLESS_MODE`

**Deskripsi**: Mode headless untuk Chrome browser.

**Values**:

- `true`: Browser berjalan di background (tanpa GUI)
- `false`: Browser ditampilkan (untuk debugging)

**Default**: `false`

**Contoh**:

```env
DEFAULT_HEADLESS_MODE=true
```

**Tips**:

- Development/debugging: gunakan `false`
- Production/automation: gunakan `true`

---

### `OUTPUT_DIRECTORY`

**Deskripsi**: Folder output untuk menyimpan hasil scraping.

**Default**: `output`

**Contoh**:

```env
OUTPUT_DIRECTORY=hasil_scraping
```

---

### `HTTP_TIMEOUT`

**Deskripsi**: Timeout untuk HTTP request ke Apps Script API (dalam detik).

**Default**: `30`

**Contoh**:

```env
HTTP_TIMEOUT=60
```

---

## Troubleshooting

### ❌ Error: "APPS_SCRIPT_URL tidak ditemukan atau belum dikonfigurasi"

**Penyebab**: File `.env` tidak ada atau `APPS_SCRIPT_URL` belum diisi.

**Solusi**:

1. Pastikan file `.env` sudah dibuat: `ls .env` atau `dir .env`
2. Buka file `.env` dan pastikan `APPS_SCRIPT_URL` terisi dengan benar
3. Restart aplikasi GUI

---

### ⚠️ Warning: "File .env tidak ditemukan"

**Penyebab**: File `.env` belum dibuat.

**Solusi**:

```bash
cp .env.example .env
```

Kemudian edit file `.env` dan isi konfigurasi yang diperlukan.

---

### ⚠️ Warning: "APPS_SCRIPT_URL belum dikonfigurasi"

**Penyebab**: Nilai `APPS_SCRIPT_URL` masih menggunakan placeholder `YOUR_SCRIPT_ID_HERE`.

**Solusi**:

1. Deploy Google Apps Script (lihat [APPS_SCRIPT_SETUP.md](APPS_SCRIPT_SETUP.md))
2. Copy URL yang didapat
3. Edit `.env` dan ganti `YOUR_SCRIPT_ID_HERE` dengan URL asli
4. Restart aplikasi

---

### 🔄 Reload Konfigurasi

Jika Anda mengubah file `.env` saat aplikasi berjalan:

1. **GUI**: Tutup dan jalankan ulang aplikasi
2. **CLI**: Jalankan ulang command

Aplikasi hanya membaca `.env` saat startup.

---

## Contoh File .env Lengkap

```env
# ============================================================
# GOOGLE SCHOLAR SCRAPER - CONFIGURATION FILE
# ============================================================

# Apps Script Web App URL (WAJIB)
APPS_SCRIPT_URL=https://script.google.com/macros/s/AKfycbxABCDEFG1234567890/exec

# Default Settings
DEFAULT_SHEET_NAME=Publikasi Dosen
DEFAULT_WAIT_TIME=10
DEFAULT_HEADLESS_MODE=false
OUTPUT_DIRECTORY=output

# Advanced
HTTP_TIMEOUT=30
```

---

## Security Best Practices

✅ **DO**:

- Simpan file `.env` dengan aman
- Jangan share file `.env` ke orang lain
- Gunakan `.env.example` sebagai template untuk sharing
- Backup `.env` di tempat aman (tidak di Git)

❌ **DON'T**:

- Jangan commit `.env` ke Git repository
- Jangan share `APPS_SCRIPT_URL` di public
- Jangan hardcode credentials di source code

---

## Referensi

- [python-dotenv Documentation](https://pypi.org/project/python-dotenv/)
- [12-Factor App: Config](https://12factor.net/config)
- [APPS_SCRIPT_SETUP.md](APPS_SCRIPT_SETUP.md) - Setup Google Apps Script
- [README.md](README.md) - Dokumentasi utama aplikasi
