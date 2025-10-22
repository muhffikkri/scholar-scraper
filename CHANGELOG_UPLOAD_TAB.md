# 🎉 Update: Tab Upload ke Google Sheets

## ✨ Fitur Baru

GUI aplikasi sekarang memiliki **2 Tab terpisah** untuk memisahkan proses scraping dan upload:

### Tab 1: 📥 Scraping Dosen

Tab untuk scraping data publikasi dari Google Scholar (fitur yang sudah ada).

### Tab 2: 📤 Upload ke Sheets (BARU!)

Tab baru untuk mengupload file Excel hasil scraping ke Google Spreadsheet.

---

## 🖥️ Tampilan Tab Upload ke Sheets

Tab ini terdiri dari 4 section:

### 1. 📁 Pilih File Excel

- **Entry field + Browse button**: Pilih file Excel (.xlsx) secara manual dari folder output
- **Button "Gunakan Hasil Terakhir"**: Otomatis menggunakan file hasil scraping terakhir
- Info helper yang menjelaskan tujuan section

### 2. 📊 Konfigurasi Google Sheets

- **Spreadsheet URL**: Input URL Google Spreadsheet tujuan
  - Format: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
- **Nama Sheet**: Input nama sheet di spreadsheet
  - Default: "Publikasi Dosen" (dari .env)
  - Catatan: "akan dibuat jika belum ada"

### 3. 🚀 Upload

- **Button "Upload ke Google Sheets"**: Tombol besar hijau untuk memulai upload
- Button akan disabled saat proses upload berjalan

### 4. 📋 Log Upload

- ScrolledText area untuk menampilkan progress upload real-time
- Timestamp untuk setiap log entry
- Error dan success messages

---

## 🔄 Workflow

### Cara 1: Upload dari Scraping (Recommended)

1. **Tab Scraping**: Jalankan scraping terlebih dahulu
2. Setelah selesai, akan muncul pesan:
   ```
   💡 Tip: Gunakan tab 'Upload ke Sheets' untuk mengunggah hasil ke Google Sheets
   ```
3. **Pindah ke Tab Upload**: Klik tab "📤 Upload ke Sheets"
4. **Klik "Gunakan Hasil Terakhir"**: File Excel otomatis terisi
5. **Isi URL Spreadsheet**: Paste URL Google Sheets tujuan
6. **Isi Nama Sheet**: Atau gunakan default "Publikasi Dosen"
7. **Klik "Upload ke Google Sheets"**: Mulai upload

### Cara 2: Upload File Existing

1. **Tab Upload**: Langsung ke tab "📤 Upload ke Sheets"
2. **Browse File**: Klik "📂 Browse" dan pilih file .xlsx
3. **Isi URL Spreadsheet**: Paste URL Google Sheets tujuan
4. **Isi Nama Sheet**: Nama sheet yang diinginkan
5. **Klik "Upload ke Google Sheets"**: Mulai upload

---

## ✅ Validasi

Aplikasi akan memvalidasi sebelum upload:

- ✅ File Excel harus dipilih
- ✅ File Excel harus ada di disk
- ✅ URL Spreadsheet harus diisi
- ✅ Nama Sheet harus diisi
- ✅ APPS_SCRIPT_URL harus dikonfigurasi di .env

Jika validasi gagal, akan muncul error dialog dengan instruksi yang jelas.

---

## 📋 Log Upload

Log akan menampilkan:

```
[14:30:15] ============================================================
[14:30:15] 🚀 MEMULAI UPLOAD KE GOOGLE SHEETS
[14:30:15] ============================================================
[14:30:15] 📂 File: publikasi_daftar_dosen_20251022_143000.xlsx
[14:30:15] 📊 Target Sheet: Publikasi Dosen
[14:30:15]
[14:30:16] 📖 Membaca data dari file Excel...
[14:30:16] ✅ Berhasil membaca 150 baris data
[14:30:16] 🔍 Mengekstrak Spreadsheet ID dari URL...
[14:30:16] ✅ Spreadsheet ID: 1ABC...XYZ
[14:30:16] 📦 Menyiapkan data untuk transfer...
[14:30:16] 📊 Total kolom: 12
[14:30:16] 📊 Total baris data: 150
[14:30:16] 🚀 Mengirim data ke Google Sheets...
[14:30:16]    Target: Publikasi Dosen
[14:30:20] ✅ SUKSES: Data berhasil ditulis ke Google Sheets!
[14:30:20]    Spreadsheet ID: 1ABC...XYZ
[14:30:20]    Sheet: Publikasi Dosen
[14:30:20]    Baris ditulis: 151
[14:30:20]
[14:30:20] ============================================================
[14:30:20] 🎉 UPLOAD SELESAI!
[14:30:20] ============================================================
```

---

## 🔧 Perubahan Teknis

### Variabel Baru

```python
# Variables for Upload Tab
self.excel_file_path = tk.StringVar()
self.spreadsheet_url = tk.StringVar()
self.sheet_name = tk.StringVar()
self.is_uploading = False
self.last_scraped_file = None  # Track last scraped Excel file
```

### Method Baru

1. **`_setup_upload_tab()`**

   - Setup UI untuk tab upload
   - 4 sections: File, Config, Upload, Log

2. **`upload_log(message)`**

   - Log khusus untuk tab upload
   - Sama seperti `log()` tapi ke `upload_log_text`

3. **`_browse_excel_file()`**

   - File dialog untuk pilih Excel
   - Filter: .xlsx only
   - Initial dir: output folder

4. **`_use_last_scraped_file()`**

   - Gunakan file dari `self.last_scraped_file`
   - Validasi file exists
   - Warning jika tidak ada

5. **`_start_upload()`**

   - Validasi input lengkap
   - Check Apps Script URL configured
   - Start thread untuk upload

6. **`_run_upload()`**
   - Logic upload dalam thread terpisah
   - Call `transfer_data_to_sheets()`
   - Handle error dan success

### Modifikasi Method Existing

**`_run_scraping()`:**

- Set `self.last_scraped_file` setelah save Excel
- Tampilkan tip untuk upload

**Window Size:**

- Dari: 800x700, non-resizable
- Ke: 900x750, resizable

**Default Output Format:**

- Dari: CSV
- Ke: Excel (untuk kemudahan upload)

---

## 🎨 UI Improvements

### Warna & Style

- **Browse button**: Blue (#3498db)
- **Use Last button**: Gray (#95a5a6)
- **Upload button**: Green (#27ae60) - lebih besar dan bold
- **Log area**: Light gray background (#f8f9fa)

### Layout

- Notebook (ttk.Notebook) untuk tabs
- Consistent padding: 15px untuk semua sections
- LabelFrame untuk grouping
- ScrolledText untuk log area

---

## 🔐 Security

- Validasi Apps Script URL sebelum upload
- Error message jelas jika .env belum dikonfigurasi
- File .env tidak ter-commit (sudah di .gitignore)

---

## 📖 Dokumentasi Terkait

- **[ENV_CONFIGURATION.md](ENV_CONFIGURATION.md)** - Setup APPS_SCRIPT_URL
- **[APPS_SCRIPT_SETUP.md](APPS_SCRIPT_SETUP.md)** - Deploy Apps Script
- **[README.md](README.md)** - Dokumentasi utama

---

## 🐛 Error Handling

### Error: "Pilih file Excel terlebih dahulu!"

**Solusi**: Klik Browse atau "Gunakan Hasil Terakhir"

### Error: "Masukkan URL Google Spreadsheet!"

**Solusi**: Paste URL spreadsheet di field Spreadsheet URL

### Error: "Masukkan nama sheet!"

**Solusi**: Isi nama sheet (default: "Publikasi Dosen")

### Error: "APPS_SCRIPT_URL belum dikonfigurasi!"

**Solusi**:

1. Edit file `.env`
2. Isi `APPS_SCRIPT_URL` dengan URL Apps Script Anda
3. Restart aplikasi
4. Lihat [APPS_SCRIPT_SETUP.md](APPS_SCRIPT_SETUP.md)

### Error saat Upload

**Penyebab**: Berbagai (network, permissions, invalid URL, dll)
**Solusi**: Lihat log upload untuk detail error

---

## 💡 Tips

1. **Gunakan "Hasil Terakhir"** untuk workflow cepat setelah scraping
2. **Sheet akan dibuat otomatis** jika belum ada di spreadsheet
3. **Data akan replace** jika sheet sudah ada (clear + write)
4. **Format URL Spreadsheet**:
   ```
   https://docs.google.com/spreadsheets/d/1ABC...XYZ/edit
   ```
   Cukup copy dari address bar browser

---

## 🎊 Selamat!

Fitur upload ke Google Sheets sekarang terintegrasi penuh dengan GUI! 🚀
