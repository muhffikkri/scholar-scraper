# Google Scholar Scraper

Aplikasi Python untuk scraping otomatis data publikasi dosen dari Google Scholar dengan GUI dan integrasi Google Sheets.

## 🚀 Quick Start

```bash
# Clone project
git clone [repository-url]
cd scholar-scraper

# Setup & Run (Windows)
setup.bat

# Atau manual:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py --gui
```

## 📋 Requirements

- Python 3.8+
- Google Chrome
- ChromeDriver (auto-install via selenium)

## 🎯 Features

✅ **Dual Mode**: GUI & CLI  
✅ **Smart Scraping**: Auto-parse venue, citations, authors  
✅ **Multi-Format Output**: Excel, CSV, DOCX  
✅ **Google Sheets Integration**: Direct upload via Apps Script  
✅ **Batch & Single**: Scraping multiple or individual dosen  
✅ **Real-time Logging**: Monitor progress  

## 📖 Usage

### Mode 1: GUI (Recommended)

```bash
python main.py --gui
```

**Tab Scraping:**
- Batch: Upload CSV/TXT file with dosen names
- Single: Input one dosen name manually
- Config: Headless mode, timeout settings
- Output: Auto-saved to `output/` folder

**Tab Upload:**
- Select Excel file
- Enter Google Sheets URL
- One-click upload

### Mode 2: CLI

```bash
python main.py
```

Edit `main.py` untuk konfigurasi:
```python
INPUT_FILE_PATH = "input/daftar_dosen.csv"
HEADLESS_MODE = False
WAIT_TIME = 10
```

## 📁 Project Structure

```
scholar-scraper/
├── main.py                 # Entry point (GUI/CLI)
├── setup.bat               # Auto setup script
├── requirements.txt        # Dependencies
├── .env                    # Configuration (create from .env.example)
├── src/
│   ├── core_logic/         # Scraping logic
│   │   ├── scraper.py
│   │   ├── file_handler.py
│   │   └── utils.py
│   └── gui/                # GUI components
│       └── app.py
├── input/                  # Input files (CSV/TXT)
└── output/                 # Results (auto-created)
```

## ⚙️ Configuration (.env)

Copy `.env.example` to `.env`:

```env
# Apps Script URL (required for Google Sheets upload)
APPS_SCRIPT_URL=https://script.google.com/macros/s/YOUR_ID/exec

# Optional settings
DEFAULT_SHEET_NAME=Publikasi Dosen
DEFAULT_WAIT_TIME=10
DEFAULT_HEADLESS_MODE=false
OUTPUT_DIRECTORY=output
```

## 📤 Google Sheets Setup

### 1. Deploy Apps Script

1. Buka https://script.google.com
2. New Project → Copy code dari `apps-script-web-app.gs`
3. Deploy → New deployment:
   - Type: **Web app**
   - Execute as: **Me**
   - Who has access: **Anyone** ⚠️ PENTING!
4. Copy Web app URL
5. Paste ke `.env` → `APPS_SCRIPT_URL=...`

### 2. Upload Data

1. GUI → Tab Upload
2. Select Excel file (or use last scraped)
3. Enter Spreadsheet URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```
4. Enter Sheet Name (auto-created if not exists)
5. Click Upload

## 📊 Output Columns

| Column | Description |
|--------|-------------|
| Nama Dosen | Dosen name |
| Judul | Publication title |
| Penulis | Authors list |
| Journal_Name | Journal/conference name |
| Volume | Volume number |
| Issue | Issue number |
| Pages | Page range |
| Publisher | Publisher name |
| Tahun | Year |
| Sitasi | Citation count |
| Link | Google Scholar URL |

## 🔧 Advanced

### Input File Format

**CSV:**
```csv
Nama
Dr. John Doe, M.Kom
Prof. Jane Smith, Ph.D
```

**TXT:**
```
Dr. John Doe, M.Kom
Prof. Jane Smith, Ph.D
```

### Output Files

```
output/
├── publikasi_daftar_dosen_20241022_143000.xlsx
├── publikasi_daftar_dosen_20241022_143000.csv
└── publikasi_daftar_dosen_20241022_143000_summary.docx
```

Single scraping:
```
publikasi_John_Doe_20241022_143000.xlsx
```

## 🐛 Troubleshooting

### Error 403 Forbidden (Upload)

**Cause:** Apps Script permission not set to "Anyone"

**Fix:**
1. script.google.com → Your project
2. Deploy → Manage deployments → Edit
3. **Who has access** = **Anyone** (not "Anyone with Google account")
4. Deploy → Copy new URL
5. Update `.env` → Restart app

### ChromeDriver Error

```bash
pip install --upgrade selenium
```

### Log Not Visible (GUI)

- Resize window (drag borders)
- Scroll down in tab
- Check terminal for backend logs

### Slow Scraping

- Enable headless mode (checkbox in GUI)
- Reduce wait time (but may cause timeouts)
- Check internet connection

## 📦 Dependencies

```
selenium>=4.15.0          # Web automation
beautifulsoup4>=4.12.0    # HTML parsing
pandas>=2.0.0             # Data manipulation
openpyxl>=3.1.0           # Excel files
python-docx>=1.0.0        # Word documents
requests>=2.31.0          # HTTP requests
python-dotenv>=1.0.0      # Environment variables
```

## 🔒 Security

- `.env` file is git-ignored (contains sensitive URLs)
- Apps Script URL acts as API key
- Only you can access your spreadsheets
- "Anyone" permission is safe (script runs with your credentials)

## 🎨 GUI Tips

- **Batch Scraping**: Use dropdown or browse to select CSV/TXT
- **Single Scraping**: Click radio button, enter name manually
- **Quick Upload**: After scraping, click "Use Last Result" in Upload tab
- **Headless Mode**: Faster, no browser window
- **Logs**: Real-time progress with timestamps

## 🚧 Known Limitations

- Google Scholar may rate-limit heavy scraping
- Requires exact dosen name (as appears on Google Scholar)
- ChromeDriver must match Chrome version (auto-handled by selenium)
- Network timeout on slow connections

## 📝 License

For research and educational purposes. Respect Google Scholar's Terms of Service.

## 🤝 Contributing

Issues and pull requests welcome!

## 📞 Support

- Check logs in GUI for errors
- Verify `.env` configuration
- Ensure Chrome is installed
- Test with single dosen first

---

**Quick Commands:**

```bash
# GUI Mode
python main.py --gui

# CLI Mode
python main.py

# Setup Everything
setup.bat

# Check Python
python --version

# Install Dependencies
pip install -r requirements.txt
```

---

Made with ❤️ for academic research
