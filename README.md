# Google Scholar Scraper - Aplikasi Scraping Publikasi Dosen

Aplikasi Python untuk scraping otomatis data publikasi dosen dari Google Scholar dengan arsitektur modular.

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

3. **Buat folder input dan file daftar dosen:**

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

2. **Langkah-langkah di GUI:**
   - Pilih file input dari dropdown atau klik **Browse** untuk memilih file
   - Pilih format output: **CSV**, **Excel**, atau **Keduanya**
   - Atur pengaturan lanjutan (opsional):
     - Centang **Headless Mode** untuk scraping lebih cepat tanpa browser GUI
     - Atur **Timeout** sesuai kecepatan internet Anda
   - Klik **▶️ Mulai Scraping**
   - Monitor progress di log aktivitas
   - File hasil akan tersimpan di folder `output/`

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

### 1. Antarmuka GUI yang User-Friendly 🖥️

- **Pemilihan File Mudah**: Dropdown untuk memilih file dari folder input atau browse manual
- **Pilihan Format Output**: CSV, Excel, atau keduanya sekaligus
- **Pengaturan Lanjutan**: Headless mode dan timeout yang dapat dikustomisasi
- **Log Real-time**: Monitor progress scraping secara langsung
- **Status Bar**: Indikator status proses yang jelas
- **Multi-threading**: GUI tetap responsif selama scraping berjalan

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

1. **Rate Limiting**: Google Scholar mungkin memblokir jika terlalu banyak request. Tambahkan jeda antar scraping jika diperlukan.

2. **Browser Driver**: Pastikan ChromeDriver kompatibel dengan versi Chrome Anda.

3. **Headless Mode**: Gunakan `HEADLESS_MODE = True` untuk scraping tanpa membuka browser (lebih cepat).

4. **Akurasi Data**: Validasi data hasil scraping, terutama untuk nama dosen yang memiliki publikasi banyak.

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

- ✅ GUI dengan Tkinter (Sudah Selesai)
- ⬜ Export ke format tambahan (JSON, XML)
- ⬜ Visualisasi data publikasi
- ⬜ Filter dan pencarian lanjutan
- ⬜ Scheduled scraping
- ⬜ Database integration

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
