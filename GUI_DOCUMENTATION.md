# Dokumentasi GUI - Google Scholar Scraper

## 🎨 Arsitektur GUI dengan Tab

### Overview

GUI menggunakan **tkinter.ttk.Notebook** untuk membuat antarmuka bertab yang memisahkan dua proses utama:

1. **Scraping** - Mengambil data dari Google Scholar
2. **Upload** - Mengirim data ke Google Sheets

### Prinsip Desain: Decoupling (Pemisahan)

```
┌─────────────────────────────────────────────────────────┐
│  Tab 1: Scraping          │  Tab 2: Upload              │
│                            │                             │
│  Input: File Dosen        │  Input: File Excel          │
│         ↓                  │         ↓                   │
│  Scraper (scraper.py)     │  Transfer (file_handler.py) │
│         ↓                  │         ↓                   │
│  Output: Excel File  ──────→  Output: Google Sheets     │
│         ↓                  │                             │
│  [Saved to disk]          │                             │
└─────────────────────────────────────────────────────────┘
```

## 📥 Tab 1: Scraping Dosen

### Layout

```
┌──────────────────────────────────────────────┐
│  📁 Pilih File Dosen                         │
│  ┌────────────────────────────────────────┐  │
│  │ File: [dropdown ▼] [🔄] [📂 Browse]   │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│  ⚙️ Pengaturan Scraping                      │
│  ☐ Headless Mode (Browser tanpa GUI)        │
│  Timeout: [10 ▲▼] detik                     │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│  [▶️ Mulai Scraping]  [⏹️ Stop]             │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│  📋 Log Scraping                             │
│  ┌────────────────────────────────────────┐  │
│  │ [12:30:45] 🚀 MEMULAI PROSES SCRAPING │  │
│  │ [12:30:46] ✅ Berhasil membaca 3 nama  │  │
│  │ [12:30:47] 🔍 Scraping: Bambang Riyant│  │
│  │ ...                                    │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

### Komponen

- **File Picker**: Combobox dengan daftar file dari folder `input/`
- **Refresh Button**: Reload daftar file
- **Browse Button**: File dialog untuk pilih file manual
- **Settings**: Checkbox headless mode, spinbox timeout
- **Control Buttons**: Start (hijau), Stop (merah)
- **Log Area**: ScrolledText untuk monitor progress

### Workflow

```
User selects file
       ↓
User clicks "Mulai Scraping"
       ↓
Button disabled, thread started
       ↓
Scraper.run_scraper() in background
       ↓
Log updates in real-time
       ↓
Excel file saved to output/
       ↓
Button enabled, process done
       ↓
Enable "Use Last File" button in Tab 2
```

## 📤 Tab 2: Upload ke Google Sheets

### Layout

```
┌──────────────────────────────────────────────┐
│  📁 Pilih File Excel untuk Diunggah          │
│  ┌────────────────────────────────────────┐  │
│  │ File Excel: [readonly_entry] [📂 Brow]│  │
│  │ [📝 Gunakan File Hasil Scraping Terak]│  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│  🎯 Target Google Spreadsheet                │
│  URL Spreadsheet: [_____________________]    │
│  Nama Sheet:      [Sheet1_______________]    │
│  Web App URL:     [_____________________]    │
│  💡 Pastikan Web App di-deploy sebagai...   │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│       [📤 Transfer Data ke Sheets]           │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│  📋 Log Upload                               │
│  ┌────────────────────────────────────────┐  │
│  │ [13:15:20] 📖 Membaca data dari Excel │  │
│  │ [13:15:21] ✅ Berhasil membaca 150 ba │  │
│  │ [13:15:22] 🚀 Mengirim data ke Sheets │  │
│  │ [13:15:25] ✅ SUKSES: Data berhasil   │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

### Komponen

- **Excel File Picker**: Entry (readonly) + Browse button
- **Quick Access Button**: Gunakan file hasil scraping terakhir
- **Target Inputs**:
  - Entry untuk URL Spreadsheet
  - Entry untuk Nama Sheet (default: "Sheet1")
  - Entry untuk Web App URL
- **Info Label**: Tips tentang deployment
- **Transfer Button**: Orange button untuk start upload
- **Log Area**: ScrolledText untuk monitor upload

### Workflow

```
User selects Excel file (or uses last scraped)
       ↓
User enters Spreadsheet URL
       ↓
User enters Sheet Name
       ↓
User enters Web App URL
       ↓
User clicks "Transfer Data ke Sheets"
       ↓
Button disabled, thread started
       ↓
transfer_data_to_sheets() in background
       ↓
Read Excel → Convert to JSON → POST to API
       ↓
Log updates in real-time
       ↓
Success/Error message shown
       ↓
Button enabled, process done
```

## 🔄 Threading Model

### Tab 1: Scraping Thread

```python
Thread 1 (GUI Main):
  - Render UI
  - Handle user input
  - Update widgets

Thread 2 (Scraping Worker):
  - read_dosen_from_file()
  - clean_dosen_name()
  - GoogleScholarScraper.run_scraper()
  - save_to_excel()
  - Callback to update log
```

### Tab 2: Upload Thread

```python
Thread 1 (GUI Main):
  - Render UI
  - Handle user input
  - Update widgets

Thread 3 (Upload Worker):
  - Read Excel file
  - Convert to JSON
  - POST to Apps Script API
  - Callback to update log
```

### Keuntungan Multi-Threading

- ✅ GUI tidak freeze saat proses berjalan
- ✅ User bisa switch tab saat scraping
- ✅ Log update real-time
- ✅ Tombol Stop berfungsi responsif

## 🎯 State Management

### Shared State

```python
self.last_scraped_file = None  # Path to last Excel file
```

### Tab 1 State

```python
self.is_scraping = False       # Flag untuk control loop
self.input_file_path           # StringVar untuk file input
self.headless_mode             # BooleanVar untuk settings
self.wait_time                 # IntVar untuk timeout
```

### Tab 2 State

```python
self.is_uploading = False      # Flag untuk control loop
self.excel_file_path           # StringVar untuk Excel file
self.spreadsheet_url           # StringVar untuk target URL
self.sheet_name                # StringVar untuk sheet name
self.web_app_url               # StringVar untuk API URL
```

## 📦 Component Hierarchy

```
Root (Tk)
├── Title Frame (bg: #2c3e50)
│   └── Title Label
│
├── Notebook (ttk.Notebook)
│   ├── Tab 1: Scraping Frame
│   │   ├── Input Section (LabelFrame)
│   │   │   ├── File Combobox
│   │   │   ├── Refresh Button
│   │   │   └── Browse Button
│   │   │
│   │   ├── Settings Section (LabelFrame)
│   │   │   ├── Headless Checkbox
│   │   │   └── Timeout Spinbox
│   │   │
│   │   ├── Control Frame
│   │   │   ├── Start Button (green)
│   │   │   └── Stop Button (red)
│   │   │
│   │   └── Log Section (LabelFrame)
│   │       └── ScrolledText
│   │
│   └── Tab 2: Upload Frame
│       ├── File Section (LabelFrame)
│       │   ├── Excel Entry
│       │   ├── Browse Button
│       │   └── Use Last Button (purple)
│       │
│       ├── Target Section (LabelFrame)
│       │   ├── URL Entry
│       │   ├── Sheet Entry
│       │   ├── WebApp Entry
│       │   └── Info Label
│       │
│       ├── Transfer Button (orange)
│       │
│       └── Log Section (LabelFrame)
│           └── ScrolledText
│
└── Status Bar (Label)
```

## 🎨 Color Scheme

```python
# Background
Background:     #f8f9fa (light gray)
Title Bar:      #2c3e50 (dark blue)
Status Bar:     #ecf0f1 (light gray)

# Buttons
Start:          #27ae60 (green)
Stop:           #e74c3c (red)
Refresh:        #3498db (blue)
Browse:         #95a5a6 (gray)
Use Last:       #9b59b6 (purple)
Transfer:       #e67e22 (orange)

# Text
Log BG:         #ffffff (white)
Log Text:       #2c3e50 (dark)
Title Text:     #ffffff (white)
```

## 📝 Log Format

### Scraping Log Example

```
[12:30:45] ============================================================
[12:30:45] 🚀 MEMULAI PROSES SCRAPING
[12:30:45] ============================================================
[12:30:46] [1/4] 📖 Membaca file: daftar_dosen.csv
[12:30:46]       ✅ Berhasil membaca 3 nama dosen
[12:30:47] [2/4] 🧹 Membersihkan nama dari gelar akademis...
[12:30:47]       1. Dr. Ir. Bambang Riyanto → Bambang Riyanto
[12:30:47]       2. Prof. Siti Nurhaliza → Siti Nurhaliza
[12:30:47]       3. Drs. Ahmad Dahlan → Ahmad Dahlan
[12:30:48] [3/4] 🔍 Memulai scraping dari Google Scholar...
[12:30:48]       Mode: Headless
[12:30:48]       Timeout: 10 detik
[12:31:05]       ✅ Scraping selesai! Total publikasi: 45
[12:31:05]       📊 Statistik per dosen:
[12:31:05]       - Bambang Riyanto: 20 publikasi
[12:31:05]       - Siti Nurhaliza: 15 publikasi
[12:31:05]       - Ahmad Dahlan: 10 publikasi
[12:31:06] [4/4] 💾 Menyimpan hasil ke Excel...
[12:31:06]       ✅ Excel: publikasi_daftar_dosen_20251022_123106.xlsx
[12:31:06] ============================================================
[12:31:06] 🎉 PROSES SELESAI!
[12:31:06] ============================================================
```

### Upload Log Example

```
[13:15:20] ============================================================
[13:15:20] 🚀 MEMULAI PROSES UPLOAD
[13:15:20] ============================================================
[13:15:20] 📖 Membaca data dari file Excel...
[13:15:21] ✅ Berhasil membaca 45 baris data
[13:15:21] 🔍 Mengekstrak Spreadsheet ID dari URL...
[13:15:21] ✅ Spreadsheet ID: 1ABC123XYZ456
[13:15:21] 📦 Menyiapkan data untuk transfer...
[13:15:21] 📊 Total kolom: 11
[13:15:21] 📊 Total baris data: 45
[13:15:22] 🚀 Mengirim data ke Google Sheets...
[13:15:22]    Target: Publikasi 2024
[13:15:25] ✅ SUKSES: Data berhasil ditulis ke Google Sheets!
[13:15:25]    Spreadsheet ID: 1ABC123XYZ456
[13:15:25]    Sheet: Publikasi 2024
[13:15:25]    Baris ditulis: 46
[13:15:25] ============================================================
[13:15:25] 🎉 UPLOAD SELESAI!
[13:15:25] ============================================================
```

## 🔐 Error Handling

### Tab 1 Errors

- File tidak ditemukan
- File format tidak valid
- Profil dosen tidak ditemukan
- ChromeDriver error
- Network timeout

### Tab 2 Errors

- Excel file tidak valid
- Spreadsheet URL tidak valid
- Web App URL tidak valid
- Network error (API unreachable)
- Permission denied (no access to spreadsheet)
- Timeout (>60 detik)

### Error Display

```python
# Console log
self._log_upload("❌ ERROR: File tidak ditemukan")

# MessageBox
messagebox.showerror("Error", "Detail error message")

# Status bar
self.status_bar.config(text="Error occurred")
```
