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
   - `publikasi_dosen_YYYYMMDD_HHMMSS.csv` - Data dalam format CSV
   - `publikasi_dosen_YYYYMMDD_HHMMSS.xlsx` - Data dalam format Excel
   - `publikasi_dosen_YYYYMMDD_HHMMSS_summary.docx` - Ringkasan dalam Word

## 📦 Dependensi

```
selenium>=4.15.0
beautifulsoup4>=4.12.0
pandas>=2.0.0
openpyxl>=3.1.0
python-docx>=1.0.0
```

## 🔧 Fitur Utama

### 1. Pembersihan Nama Otomatis

Menghapus gelar akademis dari nama dosen secara otomatis:

- Gelar depan: Dr., Ir., Prof., Drs., Dra., H., Hj.
- Gelar belakang: S.T., M.T., Ph.D, M.Kom., dll.

### 2. Scraping Cerdas

- Navigasi otomatis ke profil Google Scholar
- Loading otomatis semua publikasi (klik "Tampilkan lainnya")
- Deteksi data tidak lengkap dan navigasi ke halaman detail
- Tracking publikasi yang sudah di-scrape untuk menghindari duplikasi

### 3. Multi-Format Output

- **CSV**: Untuk analisis data lebih lanjut
- **Excel**: Dengan formatting otomatis
- **Word**: Ringkasan terstruktur per dosen

### 4. Error Handling

- Menangani profil yang tidak ditemukan
- Retry mechanism untuk element yang tidak ditemukan
- Logging untuk debugging

## 📊 Kolom Data yang Di-scrape

| Kolom      | Deskripsi                 |
| ---------- | ------------------------- |
| Nama Dosen | Nama dosen yang di-scrape |
| Judul      | Judul publikasi           |
| Penulis    | Daftar penulis            |
| Venue      | Jurnal/konferensi         |
| Tahun      | Tahun publikasi           |
| Sitasi     | Jumlah sitasi             |
| Publisher  | Penerbit (jika ada)       |

## ⚠️ Catatan Penting

1. **Rate Limiting**: Google Scholar mungkin memblokir jika terlalu banyak request. Tambahkan jeda antar scraping jika diperlukan.

2. **Browser Driver**: Pastikan ChromeDriver kompatibel dengan versi Chrome Anda.

3. **Headless Mode**: Gunakan `HEADLESS_MODE = True` untuk scraping tanpa membuka browser (lebih cepat).

4. **Akurasi Data**: Validasi data hasil scraping, terutama untuk nama dosen yang memiliki publikasi banyak.

## 🔮 Pengembangan Future (GUI)

Placeholder GUI telah disiapkan di `src/gui/app.py` untuk pengembangan antarmuka pengguna menggunakan:

- PyQt5/PyQt6
- Tkinter
- Atau framework GUI Python lainnya

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
