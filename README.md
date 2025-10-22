# Google Scholar Scraper - Aplikasi Scraping Publikasi Dosen

Aplikasi Python untuk scraping otomatis data publikasi dosen dari Google Scholar dengan arsitektur modular dan GUI berbasis tab.

## 📚 Dokumentasi Lengkap

- **[README.md](README.md)** (file ini) - Panduan umum penggunaan aplikasi
- **[ENV_CONFIGURATION.md](ENV_CONFIGURATION.md)** - 🆕 Panduan lengkap konfigurasi file .env
- **[APPS_SCRIPT_SETUP.md](APPS_SCRIPT_SETUP.md)** - Panduan setup Google Apps Script untuk upload data
- **[GUI_DOCUMENTATION.md](GUI_DOCUMENTATION.md)** - Dokumentasi teknis arsitektur GUI dan komponen

## 🏗️ Struktur Proyek

```
google-scholar-scraper/
├── src/
│   ├── core_logic/
│   │   ├── __init__.py
│   │   ├── scraper.py         # Logika utama Selenium & BS4
│   │   ├── file_handler.py    # Fungsi membaca/menyimpan file
│   │   └── utils.py           # Fungsi bantuan
│   │
│   └── gui/
│       ├── __init__.py
│       └── app.py             # Placeholder untuk GUI
│
├── input/                     # Folder untuk file input (buat manual)
│   └── daftar_dosen.csv       # File input contoh
│
├── output/                    # Folder output (dibuat otomatis)
│
├── main.py                    # Entry point aplikasi
├── README.md                  # Dokumentasi ini
└── requirements.txt           # Dependensi Python
```

## 📋 Prasyarat

- Python 3.8 atau lebih baru
- Google Chrome browser
- ChromeDriver (akan diinstal otomatis dengan selenium)

## 🚀 Instalasi

1. **Clone atau download proyek ini**

2. **Install dependensi:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Setup file konfigurasi (.env):**

   ```bash
   # Copy template .env
   cp .env.example .env
   ```

   Kemudian edit file `.env` dan isi dengan konfigurasi Anda:

   ```env
   # WAJIB: URL Web App dari Google Apps Script
   APPS_SCRIPT_URL=https://script.google.com/macros/s/YOUR_SCRIPT_ID_HERE/exec

   # OPSIONAL: Konfigurasi default
   DEFAULT_SHEET_NAME=Publikasi Dosen
   DEFAULT_WAIT_TIME=10
   DEFAULT_HEADLESS_MODE=false
   OUTPUT_DIRECTORY=output
   ```

   > **⚠️ PENTING**: File `.env` berisi informasi sensitif (URL Apps Script) dan tidak akan di-commit ke Git.
   > Lihat panduan lengkap di [APPS_SCRIPT_SETUP.md](APPS_SCRIPT_SETUP.md) untuk mendapatkan URL Apps Script.

4. **Buat folder input dan file daftar dosen:**

   Buat folder `input/` dan file `daftar_dosen.csv` atau `daftar_dosen.txt`:

   **Format CSV:**

   ```csv
   Nama
   Dr. Ir. John Doe, M.Kom., Ph.D
   Prof. Jane Smith, S.T., M.T.
   Drs. Ahmad Abdullah, M.Si.
   ```

   **Format TXT:**

   ```
   Dr. Ir. John Doe, M.Kom., Ph.D
   Prof. Jane Smith, S.T., M.T.
   Drs. Ahmad Abdullah, M.Si.
   ```

## 🎯 Cara Menggunakan

### Opsi 1: Menggunakan GUI (Recommended) 🖥️

1. **Jalankan aplikasi GUI:**

   ```bash
   python run_gui.py
   ```

   Atau double-click: `START_GUI.bat` (Windows)

2. **GUI memiliki 2 Tab Terpisah:**

#### Tab 1: 📥 Scraping Dosen

Untuk melakukan scraping data publikasi dari Google Scholar:

- **Pilih File Dosen**: Dropdown atau Browse untuk memilih file input (CSV/TXT)
- **Pengaturan Scraping**:
  - ☑️ Headless Mode: Browser tanpa GUI (lebih cepat)
  - ⏱️ Timeout: 5-30 detik (default: 10)
- **▶️ Mulai Scraping**: Jalankan proses scraping
- **Log Real-time**: Monitor progress scraping
- **Output**: File Excel akan tersimpan di folder `output/`

#### Tab 2: 📤 Upload ke Google Sheets (Baru!)

Untuk mengunggah data dari Excel ke Google Spreadsheet:

**Section 1: Pilih File Excel**

- **Browse**: Pilih file `.xlsx` secara manual dari folder output
- **Gunakan Hasil Terakhir**: Otomatis menggunakan file hasil scraping terakhir ⚡

**Section 2: Konfigurasi Google Sheets**

- **Spreadsheet URL**: Paste URL Google Spreadsheet tujuan
  - Format: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
- **Nama Sheet**: Nama sheet yang akan dibuat/diupdate
  - Default: "Publikasi Dosen" (dari .env)
  - Sheet akan dibuat otomatis jika belum ada

**Section 3: Upload**

- **📤 Upload ke Google Sheets**: Tombol hijau untuk memulai upload

**Section 4: Log Upload**

- Log real-time dengan progress detail
- Success/error messages

**Workflow Recommended:**

1. ✅ Scraping di Tab 1 → Simpan ke Excel
2. ✅ Pindah ke Tab 2 → Klik "Gunakan Hasil Terakhir"
3. ✅ Isi URL Spreadsheet → Upload!

**Keuntungan Arsitektur Tab:**

- ✅ Proses scraping dan upload **independen**
- ✅ Bisa scraping dulu, upload nanti (atau sebaliknya)
- ✅ Bisa upload file Excel dari sumber lain
- ✅ Tidak perlu scraping ulang untuk upload ke sheet berbeda
- ✅ Apps Script URL tersimpan aman di `.env`

### Opsi 2: Menggunakan Command Line 💻

1. **Konfigurasi di `main.py`:**

   ```python
   INPUT_FILE_PATH = "input/daftar_dosen.csv"  # Path file input
   OUTPUT_DIR = "output"                        # Folder output
   HEADLESS_MODE = False                        # True = tanpa GUI browser
   WAIT_TIME = 10                               # Timeout dalam detik
   ```

2. **Jalankan aplikasi:**

   ```bash
   python main.py
   ```

3. **Output yang dihasilkan:**

   Nama file output akan mengikuti nama file input. Contoh:

   - Input: `daftar_dosen.csv`

     - Output: `publikasi_daftar_dosen_YYYYMMDD_HHMMSS.csv`
     - Output: `publikasi_daftar_dosen_YYYYMMDD_HHMMSS.xlsx`
     - Output: `publikasi_daftar_dosen_YYYYMMDD_HHMMSS_summary.docx`

   - Input: `daftar_dosen_manajemen.csv`
     - Output: `publikasi_daftar_dosen_manajemen_YYYYMMDD_HHMMSS.csv`
     - Output: `publikasi_daftar_dosen_manajemen_YYYYMMDD_HHMMSS.xlsx`
     - Output: `publikasi_daftar_dosen_manajemen_YYYYMMDD_HHMMSS_summary.docx`

   Format nama: `publikasi_[nama_file_input]_[timestamp].[ekstensi]`

## 📦 Dependensi

```
selenium>=4.15.0
beautifulsoup4>=4.12.0
pandas>=2.0.0
openpyxl>=3.1.0
python-docx>=1.0.0
```

## 🔧 Fitur Utama

### 1. Antarmuka GUI Berbasis Tab 🖥️

**Arsitektur Terpisah (Decoupled):**

- **Tab Scraping**: Fokus pada proses scraping Google Scholar → Excel
- **Tab Upload**: Fokus pada transfer Excel → Google Sheets
- **Pemisahan Proses**: Kedua tab bekerja independen, dihubungkan oleh file Excel
- **Multi-threading**: Setiap tab menggunakan thread terpisah
- **Log Terpisah**: Setiap tab memiliki log aktivitas sendiri

**Fitur Tab Scraping:**

- Pemilihan file input dari dropdown atau browse
- Pengaturan headless mode dan timeout
- Progress monitoring real-time
- Output: File Excel di folder `output/`

**Fitur Tab Upload:**

- Browse file Excel atau quick access ke hasil scraping terakhir
- Input URL Google Spreadsheet dan nama sheet
- Integrasi dengan Apps Script Web API
- Progress upload real-time
- Error handling yang informatif

### 2. Pembersihan Nama Otomatis

Menghapus gelar akademis dari nama dosen secara otomatis:

- Gelar depan: Dr., Ir., Prof., Drs., Dra., H., Hj.
- Gelar belakang: S.T., M.T., Ph.D, M.Kom., dll.

### 3. Scraping Cerdas

- Navigasi otomatis ke profil Google Scholar
- Loading otomatis semua publikasi (klik "Tampilkan lainnya")
- Deteksi data tidak lengkap dan navigasi ke halaman detail
- Tracking publikasi yang sudah di-scrape untuk menghindari duplikasi

### 4. Multi-Format Output

- **CSV**: Untuk analisis data lebih lanjut
- **Excel**: Dengan formatting otomatis
- **Word**: Ringkasan terstruktur per dosen

### 5. Error Handling

- Menangani profil yang tidak ditemukan
- Retry mechanism untuk element yang tidak ditemukan
- Logging untuk debugging

## 📊 Kolom Data yang Di-scrape

| Kolom        | Deskripsi                                       |
| ------------ | ----------------------------------------------- |
| Nama Dosen   | Nama dosen yang di-scrape                       |
| Judul        | Judul publikasi                                 |
| Penulis      | Daftar penulis                                  |
| Journal_Name | Nama jurnal/konferensi/buku                     |
| Volume       | Volume jurnal (untuk artikel jurnal)            |
| Issue        | Terbitan/Issue (untuk artikel jurnal)           |
| Pages        | Halaman (untuk artikel jurnal)                  |
| Publisher    | Nama penerbit (untuk buku/lainnya)              |
| Tahun        | Tahun publikasi                                 |
| Sitasi       | Jumlah sitasi                                   |
| Link         | URL ke halaman detail artikel di Google Scholar |

### Parsing Venue Otomatis

Aplikasi akan secara otomatis memecah informasi venue menjadi kolom-kolom detail:

**Untuk Artikel Jurnal:**

- Pola: `Nama Jurnal Volume (Terbitan), Halaman`
- Contoh: `IEEE Transactions on AI 15 (3), 45-60`
- Hasil:
  - `Journal_Name`: "IEEE Transactions on AI"
  - `Volume`: "15"
  - `Issue`: "3"
  - `Pages`: "45-60"

**Untuk Buku atau Lainnya:**

- Pola: `Nama Penerbit`
- Contoh: `Springer Nature, 2020`
- Hasil:
  - `Publisher`: "Springer Nature"
  - `Tahun`: "2020"

## 🖼️ Screenshot GUI

GUI menyediakan antarmuka yang intuitif dengan fitur:

- 📁 **File Picker**: Pilih file dari folder input dengan mudah
- 💾 **Format Selector**: Pilih CSV, Excel, atau keduanya
- ⚙️ **Settings**: Headless mode dan timeout kustomisasi
- 📋 **Live Log**: Monitor progress real-time
- ▶️ **Control Buttons**: Start/Stop scraping dengan mudah

## ⚠️ Catatan Penting

### Scraping:

1. **Rate Limiting**: Google Scholar mungkin memblokir jika terlalu banyak request. Tambahkan jeda antar scraping jika diperlukan.

2. **Browser Driver**: Pastikan ChromeDriver kompatibel dengan versi Chrome Anda.

3. **Headless Mode**: Gunakan headless mode untuk scraping lebih cepat tanpa membuka browser.

4. **Akurasi Data**: Validasi data hasil scraping, terutama untuk nama dosen yang memiliki publikasi banyak.

### Upload ke Google Sheets:

1. **Web App URL**: Pastikan Apps Script sudah di-deploy dengan akses "Anyone"

2. **Spreadsheet Access**: Account yang deploy Apps Script harus punya akses Editor ke spreadsheet

3. **Sheet Name**: Jika sheet tidak ada, akan dibuat otomatis. Jika sudah ada, data lama akan dihapus

4. **Data Format**: File Excel harus dalam format `.xlsx` dengan struktur tabel yang valid

## 🎨 Mode Penggunaan

Aplikasi ini mendukung dua mode:

1. **GUI Mode** (Recommended untuk pengguna umum)

   ```bash
   python run_gui.py
   ```

   - Interface visual yang mudah
   - Tidak perlu edit kode
   - Progress monitoring real-time

2. **CLI Mode** (Untuk automation/scripting)
   ```bash
   python main.py
   ```
   - Cocok untuk batch processing
   - Dapat diintegrasikan dengan script lain
   - Konfigurasi via file main.py

## 🔮 Pengembangan Future

GUI telah diimplementasikan menggunakan Tkinter dengan fitur lengkap! Pengembangan selanjutnya:

- ✅ GUI dengan Tkinter - Tab Scraping (Sudah Selesai)
- ✅ GUI Tab Upload ke Google Sheets (Sudah Selesai)
- ✅ Apps Script Integration (Sudah Selesai)
- ⬜ Export ke format tambahan (JSON, XML)
- ⬜ Visualisasi data publikasi
- ⬜ Filter dan pencarian lanjutan
- ⬜ Scheduled scraping
- ⬜ Database integration
- ⬜ Batch upload multiple files

## 🐛 Troubleshooting

### Error: ChromeDriver not found

```bash
pip install --upgrade selenium
```

### Error: File input tidak ditemukan

Pastikan path di `INPUT_FILE_PATH` benar dan file ada.

### Scraping terlalu lambat

- Set `HEADLESS_MODE = True`
- Kurangi `WAIT_TIME` (hati-hati dengan timeout)
- Pastikan koneksi internet stabil

### Profil tidak ditemukan

- Periksa ejaan nama dosen
- Pastikan dosen memiliki profil Google Scholar
- Coba gunakan nama yang lebih spesifik

## 📝 Lisensi

Proyek ini untuk keperluan riset dan edukasi. Gunakan dengan bijak dan patuhi Terms of Service Google Scholar.

## 👨‍💻 Kontributor

Dikembangkan untuk keperluan riset NLP dan scraping data akademik.
