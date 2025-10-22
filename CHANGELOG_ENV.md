# 🎉 Update: Environment Configuration (.env) Support

## ✨ Perubahan Terbaru

Aplikasi Google Scholar Scraper sekarang mendukung **file konfigurasi `.env`** untuk menyimpan pengaturan penting seperti:

- ✅ URL Apps Script Web App
- ✅ Nama sheet default Google Sheets
- ✅ Pengaturan default scraper (timeout, headless mode, dll)
- ✅ Folder output

---

## 📁 File Baru

### 1. `.env.example` (Template)

File template yang berisi contoh konfigurasi. Gunakan sebagai referensi.

### 2. `.env` (File Konfigurasi Aktual)

File konfigurasi yang akan dibaca oleh aplikasi. **File ini tidak akan di-commit ke Git** untuk keamanan.

### 3. `ENV_CONFIGURATION.md`

Dokumentasi lengkap tentang cara menggunakan file `.env`, termasuk:

- Daftar semua konfigurasi yang tersedia
- Cara mendapatkan URL Apps Script
- Troubleshooting umum
- Best practices keamanan

---

## 🚀 Cara Menggunakan

### Langkah 1: Setup File .env

```bash
# Copy template
cp .env.example .env

# Edit file .env
nano .env  # atau text editor favorit Anda
```

### Langkah 2: Isi Konfigurasi Wajib

Buka file `.env` dan isi minimal:

```env
APPS_SCRIPT_URL=https://script.google.com/macros/s/YOUR_ACTUAL_SCRIPT_ID/exec
```

> 📖 Lihat [APPS_SCRIPT_SETUP.md](APPS_SCRIPT_SETUP.md) untuk cara mendapatkan URL Apps Script.

### Langkah 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Package baru yang ditambahkan: **`python-dotenv>=1.0.0`**

### Langkah 4: Jalankan Aplikasi

```bash
python run_gui.py
```

---

## 🎯 Keuntungan

### 1. **Keamanan** 🔒

- Credentials tidak hardcoded di source code
- File `.env` tidak akan ter-commit ke Git (sudah ada di `.gitignore`)
- URL Apps Script tersimpan dengan aman

### 2. **Konfigurasi Fleksibel** ⚙️

- Ubah pengaturan tanpa edit source code
- Konfigurasi per environment (development, production)
- Default values untuk semua settings

### 3. **User-Friendly** 🎨

- GUI menampilkan status konfigurasi
- Warning jika `.env` belum disetup
- Indikator visual: ✅ Configured atau ❌ Not Configured

---

## 📋 Konfigurasi yang Tersedia

| Konfigurasi             | Wajib?   | Default           | Deskripsi                    |
| ----------------------- | -------- | ----------------- | ---------------------------- |
| `APPS_SCRIPT_URL`       | ✅ Ya    | -                 | URL Web App Apps Script      |
| `DEFAULT_SHEET_NAME`    | ❌ Tidak | "Publikasi Dosen" | Nama sheet di Google Sheets  |
| `DEFAULT_WAIT_TIME`     | ❌ Tidak | 10                | Timeout loading page (detik) |
| `DEFAULT_HEADLESS_MODE` | ❌ Tidak | false             | Mode headless Chrome         |
| `OUTPUT_DIRECTORY`      | ❌ Tidak | output            | Folder output file           |
| `HTTP_TIMEOUT`          | ❌ Tidak | 30                | Timeout HTTP request (detik) |

---

## 🖥️ Tampilan GUI Baru

Aplikasi GUI sekarang menampilkan:

### Status Konfigurasi

```
📋 Konfigurasi: Apps Script URL = ✅ Configured | Sheet Name = Publikasi Dosen | Output Dir = output
```

### Warning (jika belum dikonfigurasi)

```
⚠️ File .env tidak ditemukan. Gunakan .env.example sebagai template.
```

atau

```
⚠️ APPS_SCRIPT_URL belum dikonfigurasi di file .env
```

---

## 🔧 Perubahan Teknis

### File yang Dimodifikasi:

1. **`requirements.txt`**

   - Tambah: `python-dotenv>=1.0.0`

2. **`.gitignore`**

   - Tambah: `.env` dan `.env.local`

3. **`src/core_logic/file_handler.py`**

   - Import `load_dotenv()` dan `os.getenv()`
   - Fungsi baru: `get_config(key, default)`
   - Update `transfer_data_to_sheets()`: parameter `web_app_url` dan `sheet_name` sekarang optional
   - Otomatis membaca dari `.env` jika parameter tidak diberikan

4. **`src/gui/app.py`**

   - Import `load_dotenv()`
   - Method baru: `_load_config()` untuk membaca konfigurasi dari `.env`
   - Tampilan status konfigurasi di GUI
   - Warning banner jika `.env` belum disetup

5. **`README.md`**
   - Tambah step instalasi untuk setup `.env`
   - Update dokumentasi dengan link ke `ENV_CONFIGURATION.md`

### File Baru:

1. **`.env.example`** - Template konfigurasi
2. **`.env`** - File konfigurasi (sudah dibuat, perlu diisi)
3. **`ENV_CONFIGURATION.md`** - Dokumentasi lengkap konfigurasi

---

## 📖 Dokumentasi

Untuk informasi lebih detail, lihat:

- **[ENV_CONFIGURATION.md](ENV_CONFIGURATION.md)** - Panduan lengkap konfigurasi .env
- **[APPS_SCRIPT_SETUP.md](APPS_SCRIPT_SETUP.md)** - Cara deploy Apps Script dan dapatkan URL
- **[README.md](README.md)** - Dokumentasi utama aplikasi

---

## ⚠️ Important Notes

1. **File `.env` tidak akan ter-commit ke Git** untuk keamanan
2. **Jangan share file `.env`** atau `APPS_SCRIPT_URL` ke public
3. **Gunakan `.env.example`** sebagai template untuk sharing
4. **Restart aplikasi** setelah mengubah `.env`

---

## 🐛 Troubleshooting

### Error: "APPS_SCRIPT_URL tidak ditemukan"

**Solusi**:

1. Pastikan file `.env` ada di root project
2. Pastikan `APPS_SCRIPT_URL` sudah diisi dengan URL yang benar
3. Restart aplikasi

### Warning: "File .env tidak ditemukan"

**Solusi**:

```bash
cp .env.example .env
```

Kemudian edit file `.env` dan isi konfigurasi yang diperlukan.

---

## 🎊 Selamat Menggunakan!

Aplikasi sekarang lebih aman dan mudah dikonfigurasi dengan sistem `.env`! 🚀
