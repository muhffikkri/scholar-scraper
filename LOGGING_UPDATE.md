# 📊 Update: Logging Per-Folder & Tab Logs di GUI

## Ringkasan Perubahan

### ✅ Yang Diimplementasikan

#### 1. **Logging Per-Folder** 📁

Setiap session scraping sekarang membuat folder tersendiri di dalam `logging/`:

**Struktur Lama:**

```
logging/
├── summary_20251025_091200.json
├── detailed_log_20251025_091200.csv
├── failed_names_20251025_091200.txt
└── captcha_blocked_20251025_091200.json
```

**Struktur Baru:**

```
logging/
├── session_20251025_091200/
│   ├── summary_20251025_091200.json
│   ├── detailed_log_20251025_091200.csv
│   ├── failed_names_20251025_091200.txt
│   └── captcha_blocked_20251025_091200.txt
├── session_20251025_101530/
│   ├── summary_20251025_101530.json
│   ├── detailed_log_20251025_101530.csv
│   └── failed_names_20251025_101530.txt
└── session_20251025_143045/
    ├── summary_20251025_143045.json
    ├── detailed_log_20251025_143045.csv
    └── failed_names_20251025_143045.txt
```

**Keuntungan:**

- ✅ Lebih terorganisir - setiap session dalam folder sendiri
- ✅ Mudah dihapus - delete satu folder untuk hapus satu session
- ✅ Mudah di-archive - zip folder untuk backup
- ✅ Tidak campur aduk dengan session lain

#### 2. **Tab Logs di GUI** 📋

Menambahkan tab ketiga "Logs" di GUI untuk melihat riwayat scraping:

**Fitur Tab Logs:**

- 📊 **Treeview** - Daftar semua session dengan informasi lengkap
- 🔄 **Refresh Button** - Update daftar session
- 📁 **Open Folder** - Buka folder logging di explorer
- 👆 **Double-click** - Lihat detail session
- 📈 **Statistics** - Total, Success, Failed, CAPTCHA count
- ⏱️ **Duration** - Waktu eksekusi per session

**Kolom Treeview:**

- Session ID
- Waktu Mulai
- Durasi
- Total Dosen
- ✅ Success
- ❌ Failed
- 🤖 CAPTCHA
- Success Rate

**Detail View:**
Saat double-click session, tampilkan:

- Session info (ID, start/end time, duration, folder)
- Statistics (total, success, failed, CAPTCHA, rate)
- ✅ Success list
- ❌ Failed list
- 🤖 CAPTCHA blocked list
- 📝 All processed names

---

## 📝 File yang Dimodifikasi

### 1. `src/core_logic/logger.py`

**Perubahan:**

- `__init__`: Membuat folder `session_{session_id}` di dalam `logging/`
- `end_session()`: Return `log_dir` untuk reference
- Added `get_all_sessions()`: Function untuk scan semua session folders

**Code:**

```python
def __init__(self, log_dir: str = "logging"):
    self.base_log_dir = log_dir
    self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create session-specific folder
    self.log_dir = os.path.join(self.base_log_dir, f"session_{self.session_id}")
    os.makedirs(self.log_dir, exist_ok=True)
```

### 2. `src/gui/app.py`

**Perubahan:**

- Added import `json`
- Added Tab 3: "📋 Logs"
- Added `_setup_logs_tab()`: Setup UI untuk logs tab
- Added `_refresh_logs()`: Load dan display sessions
- Added `_on_session_double_click()`: Handle detail view
- Added `_open_logs_folder()`: Open folder di explorer

**UI Components:**

- `sessions_tree`: Treeview untuk list sessions
- `session_details_text`: ScrolledText untuk detail
- Refresh button
- Open folder button

### 3. `.gitignore`

**Perubahan:**

```gitignore
# Old
logging/*.json
logging/*.csv
logging/*.txt
!logging/.gitkeep

# New
logging/session_*/
!logging/.gitkeep
```

### 4. `test_logger.py`

**Perubahan:**

- Display `log_dir` in summary
- Updated output messages

---

## 🎮 Cara Menggunakan

### Via GUI

1. **Jalankan GUI:**

   ```bash
   python main.py --gui
   ```

2. **Tab Logs:**

   - Klik tab "📋 Logs"
   - Akan tampil daftar semua session scraping
   - Double-click session untuk lihat detail
   - Klik "🔄 Refresh" untuk update list
   - Klik "📁 Buka Folder Logs" untuk open di explorer

3. **Detail Session:**
   - Session info (waktu, durasi, folder)
   - Statistik lengkap
   - Daftar success/failed/captcha
   - Semua nama yang diproses

### Via Code

```python
from src.core_logic.logger import get_all_sessions

# Get all sessions
sessions = get_all_sessions("logging")

for session in sessions:
    print(f"Session: {session['session_info']['session_id']}")
    print(f"Success: {session['statistics']['success_count']}")
    print(f"Folder: {session['log_folder']}")
```

---

## 📂 Struktur Folder Logging

```
logging/
├── .gitkeep                          # Keep folder in git
│
├── session_20251025_091200/          # Session 1
│   ├── summary_20251025_091200.json
│   ├── detailed_log_20251025_091200.csv
│   ├── failed_names_20251025_091200.txt
│   └── captcha_blocked_20251025_091200.txt
│
├── session_20251025_101530/          # Session 2
│   ├── summary_20251025_101530.json
│   ├── detailed_log_20251025_101530.csv
│   └── failed_names_20251025_101530.txt
│
└── session_20251025_143045/          # Session 3
    ├── summary_20251025_143045.json
    ├── detailed_log_20251025_143045.csv
    ├── failed_names_20251025_143045.txt
    └── captcha_blocked_20251025_143045.txt
```

---

## 🎯 Use Cases

### 1. Review Riwayat Scraping

```
Tab Logs → Lihat daftar session → Double-click untuk detail
```

### 2. Re-scrape Failed Names

```
Tab Logs → Double-click session → Copy failed names →
Create new input file → Re-run scraping
```

### 3. Cleanup Old Sessions

```
📁 Buka Folder Logs → Pilih session lama → Delete folder
atau
Tab Logs → Lihat session lama → Manual delete dari explorer
```

### 4. Archive Sessions

```
📁 Buka Folder Logs →
Zip folder session_YYYYMMDD_HHMMSS →
Move ke backup location
```

### 5. Monitor Success Rate

```
Tab Logs → Lihat kolom "Success Rate" →
Identify sessions dengan rate rendah →
Check detail untuk troubleshoot
```

---

## 🧪 Testing

### Test Logger Per-Folder

```bash
python test_logger.py
```

Output:

```
Testing ScraperLogger...

============================================================
LOGGING SESSION STARTED
============================================================
Session ID: 20251025_091200
Log Directory: logging\session_20251025_091200
============================================================

✅ SUCCESS: Dr. Ahmad Sutanto (15 publikasi)
...

📊 Summary saved: logging\session_20251025_091200\summary_*.json
📋 Detailed log saved: logging\session_20251025_091200\detailed_log_*.csv
...

Final Summary:
  Session ID: 20251025_091200
  Log Folder: logging\session_20251025_091200
  Total: 5
  Success: 3
  Failed: 2
  CAPTCHA: 1
```

### Test GUI Logs Tab

```bash
python main.py --gui
```

Steps:

1. Run scraping (Tab 1)
2. Go to Tab 3 "📋 Logs"
3. See session list
4. Double-click session
5. View details

---

## 💡 Tips & Best Practices

### 1. Regular Cleanup

```bash
# Delete sessions older than 30 days
# (manual atau buat script)
```

### 2. Archive Important Sessions

```bash
# Zip sessions dengan data penting
cd logging
tar -czf backup_202510.tar.gz session_202510*/
```

### 3. Quick Retry Failed

```
Tab Logs → Select session → Double-click →
Copy failed names → Paste to input/retry.txt →
Run scraping again
```

### 4. Monitor Performance

```
Tab Logs → Sort by Success Rate →
Identify problem patterns →
Adjust settings (timeout, CAPTCHA wait)
```

---

## 🔧 Troubleshooting

### Tab Logs Kosong

**Problem:** Tidak ada session di list

**Solution:**

- Run scraping minimal sekali
- Check folder `logging/` ada folder `session_*`
- Klik "🔄 Refresh"

### Error Reading Session

**Problem:** "Error reading summary"

**Solution:**

- Check file `summary_*.json` ada di folder session
- Check file valid JSON (tidak corrupt)
- Delete session folder jika corrupt

### Folder Logs Tidak Terbuka

**Problem:** "📁 Buka Folder Logs" tidak work

**Solution:**

- Check folder `logging/` exists
- Windows: Check file explorer
- Manual open: navigate to project/logging

---

## 📊 Migration dari Old Structure

Jika Anda punya log files lama (tanpa folder session):

### Manual Migration

```bash
# 1. Create session folder
mkdir logging/session_OLD_20251024

# 2. Move old files
move logging/summary_*.json logging/session_OLD_20251024/
move logging/detailed_log_*.csv logging/session_OLD_20251024/
move logging/failed_names_*.txt logging/session_OLD_20251024/
move logging/captcha_blocked_*.txt logging/session_OLD_20251024/
```

### Automatic Migration Script (Future)

```python
# Coming soon - script untuk auto-migrate old logs
```

---

## 🚀 Future Enhancements

Planned improvements:

1. **Delete Session** - Button untuk delete dari GUI
2. **Export Session** - Export ke CSV/Excel
3. **Filter Sessions** - Filter by date, success rate, etc.
4. **Compare Sessions** - Side-by-side comparison
5. **Statistics Dashboard** - Visual charts & graphs
6. **Auto-cleanup** - Delete old sessions automatically
7. **Search Functionality** - Search by nama dosen
8. **Retry from GUI** - One-click retry failed names

---

**Struktur logging sekarang lebih terorganisir dan mudah dikelola! 📊**
