"""
GUI Application for Google Scholar Scraper
Menggunakan Tkinter dengan tab untuk memisahkan fungsionalitas scraping dan upload.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import json
import threading
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core_logic.file_handler import (
    read_dosen_from_file,
    save_to_csv,
    save_to_excel,
    generate_summary_docx,
    ensure_output_directory,
    transfer_data_to_sheets,
    get_config
)
from src.core_logic.utils import clean_dosen_name
from src.core_logic.scraper import GoogleScholarScraper


class GoogleScholarScraperGUI:
    """
    Main GUI class for Google Scholar Scraper application.
    """
    
    def __init__(self, root):
        """
        Initialize the GUI application.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Google Scholar Scraper")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Variables for Scraping Tab
        self.input_file_path = tk.StringVar()
        self.single_dosen_name = tk.StringVar()  # NEW: for single scraping
        self.scraping_mode = tk.StringVar(value="batch")  # NEW: batch or single
        self.output_format = tk.StringVar(value="excel")  # Default: Excel
        self.headless_mode = tk.BooleanVar(value=False)
        self.wait_time = tk.IntVar(value=10)
        self.captcha_wait_time = tk.IntVar(value=5)  # CAPTCHA wait time in minutes
        # Year selection for per-year cited_by counts
        self.current_year = datetime.now().year
        self.year_from = tk.IntVar(value=self.current_year - 3)
        self.year_to = tk.IntVar(value=self.current_year)
        self.is_running = False
        self.last_scraped_file = None  # Track last scraped Excel file
        
        # Variables for Upload Tab
        self.excel_file_path = tk.StringVar()
        self.spreadsheet_url = tk.StringVar()
        self.sheet_name = tk.StringVar()
        self.is_uploading = False
        
        # Load configuration from .env
        self._load_config()
        
        # Setup GUI components
        self._setup_ui()
        
        # Load available input files
        self._load_input_files()
        
        # Initialize input mode (show batch by default)
        self._toggle_input_mode()
    
    def _load_config(self):
        """
        Load configuration from .env file and check if properly configured.
        """
        self.config = {
            'apps_script_url': get_config('APPS_SCRIPT_URL', ''),
            'default_sheet_name': get_config('DEFAULT_SHEET_NAME', 'Publikasi Dosen'),
            'default_wait_time': int(get_config('DEFAULT_WAIT_TIME', '10')),
            'default_headless': get_config('DEFAULT_HEADLESS_MODE', 'false').lower() == 'true',
            'output_directory': get_config('OUTPUT_DIRECTORY', 'output')
        }
        
        # Update default values based on config
        self.wait_time.set(self.config['default_wait_time'])
        self.headless_mode.set(self.config['default_headless'])
        
        # Check if .env file exists
        if not os.path.exists('.env'):
            self.config_warning = "⚠️ File .env tidak ditemukan. Gunakan .env.example sebagai template."
        elif not self.config['apps_script_url'] or 'YOUR_SCRIPT_ID_HERE' in self.config['apps_script_url']:
            self.config_warning = "⚠️ APPS_SCRIPT_URL belum dikonfigurasi di file .env"
        else:
            self.config_warning = None
    
    def _setup_ui(self):
        """
        Setup all UI components.
        """
        # Title Frame - More compact
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🎓 Google Scholar Scraper",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title_label.pack(pady=10)
        
        # Configuration Warning (if any) - More compact
        if self.config_warning:
            warning_frame = tk.Frame(self.root, bg="#fff3cd", relief=tk.FLAT, borderwidth=1)
            warning_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
            
            warning_label = tk.Label(
                warning_frame,
                text=self.config_warning,
                font=("Arial", 8),
                fg="#856404",
                bg="#fff3cd"
            )
            warning_label.pack(padx=8, pady=4)
        
        # Create Notebook (Tabs) - Remove config info frame to save space
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tab 1: Scraping
        self.scraping_tab = tk.Frame(self.notebook)
        self.notebook.add(self.scraping_tab, text="📥 Scraping Dosen")
        
        # Tab 2: Real-time Log
        self.realtime_log_tab = tk.Frame(self.notebook)
        self.notebook.add(self.realtime_log_tab, text="📝 Log Aktivitas")
        
        # Tab 3: Upload to Sheets
        self.upload_tab = tk.Frame(self.notebook)
        self.notebook.add(self.upload_tab, text="📤 Upload ke Sheets")
        
        # Tab 4: Logs History
        self.logs_tab = tk.Frame(self.notebook)
        self.notebook.add(self.logs_tab, text="📋 Riwayat")
        
        # Setup tabs
        self._setup_scraping_tab()
        self._setup_realtime_log_tab()
        self._setup_upload_tab()
        self._setup_logs_tab()
    
    def _setup_scraping_tab(self):
        """
        Setup UI for Scraping tab.
        """
        # Main Content Frame
        main_frame = tk.Frame(self.scraping_tab, padx=20, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== Section 1: Input Mode & File =====
        input_section = tk.LabelFrame(
            main_frame,
            text="📁 Mode Scraping",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        input_section.pack(fill=tk.X, pady=(0, 10))
        
        # Mode selection (Batch vs Single)
        mode_frame = tk.Frame(input_section)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            mode_frame,
            text="Pilih Mode:",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        batch_rb = tk.Radiobutton(
            mode_frame,
            text="📋 Batch (dari file)",
            variable=self.scraping_mode,
            value="batch",
            font=("Arial", 10),
            cursor="hand2",
            command=self._toggle_input_mode
        )
        batch_rb.pack(side=tk.LEFT, padx=(0, 15))
        
        single_rb = tk.Radiobutton(
            mode_frame,
            text="👤 Perorangan (input manual)",
            variable=self.scraping_mode,
            value="single",
            font=("Arial", 10),
            cursor="hand2",
            command=self._toggle_input_mode
        )
        single_rb.pack(side=tk.LEFT)
        
        # Batch mode file selection
        self.batch_frame = tk.Frame(input_section)
        self.batch_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            self.batch_frame,
            text="File Dosen:",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.file_combo = ttk.Combobox(
            self.batch_frame,
            textvariable=self.input_file_path,
            state="readonly",
            width=35,
            font=("Arial", 10)
        )
        self.file_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_btn = tk.Button(
            self.batch_frame,
            text="🔄",
            command=self._load_input_files,
            bg="#3498db",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            relief=tk.FLAT,
            width=3
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        browse_btn = tk.Button(
            self.batch_frame,
            text="📂 Browse",
            command=self._browse_file,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            relief=tk.FLAT,
            padx=10
        )
        browse_btn.pack(side=tk.LEFT)
        
        # Single mode name input
        self.single_frame = tk.Frame(input_section)
        # Don't pack yet - will be shown/hidden by toggle
        
        tk.Label(
            self.single_frame,
            text="Nama Dosen:",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.single_entry = tk.Entry(
            self.single_frame,
            textvariable=self.single_dosen_name,
            font=("Arial", 10),
            width=50
        )
        self.single_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            self.single_frame,
            text="(Contoh: Dr. John Doe, M.Kom)",
            font=("Arial", 8),
            fg="#666666"
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # ===== Section 2: Output Format =====
        output_section = tk.LabelFrame(
            main_frame,
            text="💾 Format Output",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        output_section.pack(fill=tk.X, pady=(0, 10))
        
        format_frame = tk.Frame(output_section)
        format_frame.pack(fill=tk.X)
        
        tk.Label(
            format_frame,
            text="Pilih format hasil scraping:",
            font=("Arial", 10)
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Radio buttons for format
        formats = [
            ("CSV (.csv)", "csv"),
            ("Excel (.xlsx)", "excel"),
            ("Keduanya (CSV + Excel)", "both")
        ]
        
        for text, value in formats:
            rb = tk.Radiobutton(
                format_frame,
                text=text,
                variable=self.output_format,
                value=value,
                font=("Arial", 10),
                cursor="hand2"
            )
            rb.pack(anchor=tk.W, pady=2)
        
        # ===== Section 3: Advanced Settings =====
        settings_section = tk.LabelFrame(
            main_frame,
            text="⚙️ Pengaturan Lanjutan",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        settings_section.pack(fill=tk.X, pady=(0, 10))
        
        # Headless mode
        headless_check = tk.Checkbutton(
            settings_section,
            text="Headless Mode (Browser tanpa GUI - Lebih cepat)",
            variable=self.headless_mode,
            font=("Arial", 10),
            cursor="hand2"
        )
        headless_check.pack(anchor=tk.W, pady=5)
        
        # Wait time
        wait_frame = tk.Frame(settings_section)
        wait_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            wait_frame,
            text="Timeout (detik):",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        wait_spinbox = tk.Spinbox(
            wait_frame,
            from_=5,
            to=30,
            textvariable=self.wait_time,
            width=10,
            font=("Arial", 10)
        )
        wait_spinbox.pack(side=tk.LEFT)
        
        # CAPTCHA wait time
        captcha_wait_frame = tk.Frame(settings_section)
        captcha_wait_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            captcha_wait_frame,
            text="CAPTCHA Timeout (menit):",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        captcha_wait_spinbox = tk.Spinbox(
            captcha_wait_frame,
            from_=1,
            to=15,
            textvariable=self.captcha_wait_time,
            width=10,
            font=("Arial", 10)
        )
        captcha_wait_spinbox.pack(side=tk.LEFT)
        
        tk.Label(
            captcha_wait_frame,
            text="(Waktu tunggu untuk solve CAPTCHA manual)",
            font=("Arial", 9),
            fg="gray"
        ).pack(side=tk.LEFT, padx=10)
        
        # Year range selection for cited_by per year
        year_frame = tk.Frame(settings_section)
        year_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            year_frame,
            text="Cited-by per tahun (From - To):",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))

        year_from_spin = tk.Spinbox(
            year_frame,
            from_=1900,
            to=self.current_year,
            textvariable=self.year_from,
            width=8,
            font=("Arial", 10)
        )
        year_from_spin.pack(side=tk.LEFT)

        tk.Label(year_frame, text=" - ", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

        year_to_spin = tk.Spinbox(
            year_frame,
            from_=1900,
            to=self.current_year,
            textvariable=self.year_to,
            width=8,
            font=("Arial", 10)
        )
        year_to_spin.pack(side=tk.LEFT)
        
        # ===== Section 4: Control Buttons =====
        button_frame = tk.Frame(main_frame, pady=10)
        button_frame.pack(fill=tk.X)
        
        self.start_btn = tk.Button(
            button_frame,
            text="▶️ Mulai Scraping",
            command=self._start_scraping,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹️ Stop",
            command=self._stop_scraping,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
    
    def _setup_realtime_log_tab(self):
        """
        Setup UI for Real-time Log tab.
        """
        # Main Content Frame
        main_frame = tk.Frame(self.realtime_log_tab, padx=20, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Info Section
        info_frame = tk.Frame(main_frame, bg="#d1ecf1", relief=tk.FLAT, borderwidth=1)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_label = tk.Label(
            info_frame,
            text="📝 Log aktivitas scraping real-time. Tab ini akan otomatis terbuka saat scraping dimulai.",
            font=("Arial", 9),
            fg="#0c5460",
            bg="#d1ecf1",
            anchor=tk.W,
            padx=10,
            pady=8
        )
        info_label.pack(fill=tk.X)
        
        # Toolbar
        toolbar = tk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        clear_btn = tk.Button(
            toolbar,
            text="🗑️ Clear Log",
            command=self._clear_log,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            relief=tk.FLAT,
            padx=15
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Log Text Area
        log_section = tk.LabelFrame(
            main_frame,
            text="📋 Log Output",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        log_section.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_section,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status Bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#ecf0f1",
            font=("Arial", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _setup_upload_tab(self):
        """
        Setup UI for Upload to Google Sheets tab.
        """
        # Main Content Frame
        main_frame = tk.Frame(self.upload_tab, padx=20, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== Section 1: Excel File Selection =====
        file_section = tk.LabelFrame(
            main_frame,
            text="📁 Pilih File Excel",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        file_section.pack(fill=tk.X, pady=(0, 10))
        
        # Info label
        info_label = tk.Label(
            file_section,
            text="Pilih file Excel (.xlsx) hasil scraping yang akan diupload ke Google Sheets",
            font=("Arial", 9),
            fg="#555555",
            anchor=tk.W
        )
        info_label.pack(fill=tk.X, pady=(0, 10))
        
        # File selection frame
        file_frame = tk.Frame(file_section)
        file_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            file_frame,
            text="File Excel:",
            font=("Arial", 10),
            width=12,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.excel_entry = tk.Entry(
            file_frame,
            textvariable=self.excel_file_path,
            font=("Arial", 10),
            width=40,
            state="readonly"
        )
        self.excel_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        browse_excel_btn = tk.Button(
            file_frame,
            text="📂 Browse",
            command=self._browse_excel_file,
            bg="#3498db",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            relief=tk.FLAT,
            padx=15
        )
        browse_excel_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Use last scraped button
        use_last_btn = tk.Button(
            file_frame,
            text="⬅️ Gunakan Hasil Terakhir",
            command=self._use_last_scraped_file,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            relief=tk.FLAT,
            padx=10
        )
        use_last_btn.pack(side=tk.LEFT)
        
        # ===== Section 2: Google Sheets Configuration =====
        sheets_section = tk.LabelFrame(
            main_frame,
            text="📊 Konfigurasi Google Sheets",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        sheets_section.pack(fill=tk.X, pady=(0, 10))
        
        # Spreadsheet URL
        url_frame = tk.Frame(sheets_section)
        url_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            url_frame,
            text="Spreadsheet URL:",
            font=("Arial", 10),
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.spreadsheet_entry = tk.Entry(
            url_frame,
            textvariable=self.spreadsheet_url,
            font=("Arial", 10),
            width=50
        )
        self.spreadsheet_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Sheet Name
        sheet_frame = tk.Frame(sheets_section)
        sheet_frame.pack(fill=tk.X, pady=(10, 5))
        
        tk.Label(
            sheet_frame,
            text="Nama Sheet:",
            font=("Arial", 10),
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.sheet_entry = tk.Entry(
            sheet_frame,
            textvariable=self.sheet_name,
            font=("Arial", 10),
            width=30
        )
        self.sheet_entry.pack(side=tk.LEFT)
        self.sheet_name.set(self.config['default_sheet_name'])  # Set default
        
        tk.Label(
            sheet_frame,
            text="(akan dibuat jika belum ada)",
            font=("Arial", 8),
            fg="#666666"
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # ===== Section 3: Upload Actions =====
        action_section = tk.LabelFrame(
            main_frame,
            text="🚀 Upload",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        action_section.pack(fill=tk.X, pady=(0, 10))
        
        # Upload button
        button_frame = tk.Frame(action_section)
        button_frame.pack(pady=10)
        
        self.upload_btn = tk.Button(
            button_frame,
            text="📤 Upload ke Google Sheets",
            command=self._start_upload,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=30,
            pady=10,
            width=25
        )
        self.upload_btn.pack()
        
        # ===== Section 4: Upload Log =====
        log_section = tk.LabelFrame(
            main_frame,
            text="📋 Log Upload",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        log_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.upload_log_text = scrolledtext.ScrolledText(
            log_section,
            wrap=tk.WORD,
            height=12,
            font=("Consolas", 9),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        self.upload_log_text.pack(fill=tk.BOTH, expand=True)
    
    def _setup_logs_tab(self):
        """
        Setup UI for Logs tab.
        """
        # Main Content Frame
        main_frame = tk.Frame(self.logs_tab, padx=20, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== Section 1: Session List =====
        sessions_section = tk.LabelFrame(
            main_frame,
            text="📂 Riwayat Scraping Sessions",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        sessions_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Toolbar
        toolbar = tk.Frame(sessions_section)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        refresh_btn = tk.Button(
            toolbar,
            text="🔄 Refresh",
            command=self._refresh_logs,
            bg="#3498db",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            relief=tk.FLAT,
            padx=15
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        open_folder_btn = tk.Button(
            toolbar,
            text="📁 Buka Folder Logs",
            command=self._open_logs_folder,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            relief=tk.FLAT,
            padx=15
        )
        open_folder_btn.pack(side=tk.LEFT)
        
        # Create Treeview for sessions
        tree_frame = tk.Frame(sessions_section)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        tree_scroll_y = tk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.sessions_tree = ttk.Treeview(
            tree_frame,
            columns=("session_id", "start_time", "duration", "total", "success", "failed", "captcha", "rate"),
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            height=15
        )
        
        tree_scroll_y.config(command=self.sessions_tree.yview)
        tree_scroll_x.config(command=self.sessions_tree.xview)
        
        # Define columns
        self.sessions_tree.heading("session_id", text="Session ID")
        self.sessions_tree.heading("start_time", text="Waktu Mulai")
        self.sessions_tree.heading("duration", text="Durasi")
        self.sessions_tree.heading("total", text="Total")
        self.sessions_tree.heading("success", text="✅ Success")
        self.sessions_tree.heading("failed", text="❌ Failed")
        self.sessions_tree.heading("captcha", text="🤖 CAPTCHA")
        self.sessions_tree.heading("rate", text="Success Rate")
        
        self.sessions_tree.column("session_id", width=150)
        self.sessions_tree.column("start_time", width=150)
        self.sessions_tree.column("duration", width=100)
        self.sessions_tree.column("total", width=60)
        self.sessions_tree.column("success", width=80)
        self.sessions_tree.column("failed", width=80)
        self.sessions_tree.column("captcha", width=80)
        self.sessions_tree.column("rate", width=100)
        
        self.sessions_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click event
        self.sessions_tree.bind("<Double-1>", self._on_session_double_click)
        
        # ===== Section 2: Session Details =====
        details_section = tk.LabelFrame(
            main_frame,
            text="📋 Detail Session",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        details_section.pack(fill=tk.X, pady=(0, 10))
        
        self.session_details_text = scrolledtext.ScrolledText(
            details_section,
            wrap=tk.WORD,
            height=8,
            font=("Consolas", 9),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        self.session_details_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial load
        self._refresh_logs()
    
    def _load_input_files(self):
        """
        Load available CSV and TXT files from the input folder.
        """
        input_dir = "input"
        
        if not os.path.exists(input_dir):
            os.makedirs(input_dir)
            self.log("⚠️ Folder 'input' tidak ditemukan. Folder baru telah dibuat.")
            self.file_combo['values'] = []
            return
        
        # Find all CSV and TXT files
        files = []
        for file in os.listdir(input_dir):
            if file.endswith(('.csv', '.txt')):
                files.append(os.path.join(input_dir, file))
        
        if files:
            self.file_combo['values'] = files
            self.file_combo.current(0)
            self.log(f"✅ Ditemukan {len(files)} file input")
        else:
            self.file_combo['values'] = []
            self.log("⚠️ Tidak ada file CSV/TXT di folder 'input'")
    
    def _toggle_input_mode(self):
        """
        Toggle between batch and single scraping mode.
        Show/hide appropriate input fields.
        """
        mode = self.scraping_mode.get()
        
        if mode == "batch":
            # Show batch frame, hide single frame
            self.single_frame.pack_forget()
            self.batch_frame.pack(fill=tk.X, pady=5)
        else:  # single
            # Hide batch frame, show single frame
            self.batch_frame.pack_forget()
            self.single_frame.pack(fill=tk.X, pady=5)
            self.single_entry.focus()  # Auto focus ke entry
    
    def _browse_file(self):
        """
        Open file browser to select input file.
        """
        filename = filedialog.askopenfilename(
            title="Pilih File Daftar Dosen",
            initialdir="input",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            self.input_file_path.set(filename)
            self.log(f"📁 File dipilih: {filename}")
    
    def log(self, message):
        """
        Add message to log text area (Real-time Log tab).
        
        Args:
            message (str): Message to log
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.update()  # Force update immediately
        self.root.update()  # Force window update
    
    def _clear_log(self):
        """
        Clear the real-time log text area.
        """
        self.log_text.delete(1.0, tk.END)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] 🗑️ Log cleared\n")
    
    def upload_log(self, message):
        """
        Add message to upload log text area (Upload tab).
        
        Args:
            message (str): Message to log
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.upload_log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.upload_log_text.see(tk.END)
        self.upload_log_text.update()  # Force update immediately
        self.root.update()  # Force window update
    
    def _update_status(self, message):
        """
        Update status bar.
        
        Args:
            message (str): Status message
        """
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def _browse_excel_file(self):
        """
        Open file browser to select Excel file for upload.
        """
        filename = filedialog.askopenfilename(
            title="Pilih File Excel",
            initialdir=self.config['output_directory'],
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            self.excel_file_path.set(filename)
            self.upload_log(f"📁 File dipilih: {os.path.basename(filename)}")
    
    def _use_last_scraped_file(self):
        """
        Use the last scraped Excel file.
        """
        if self.last_scraped_file and os.path.exists(self.last_scraped_file):
            self.excel_file_path.set(self.last_scraped_file)
            self.upload_log(f"✅ Menggunakan file terakhir: {os.path.basename(self.last_scraped_file)}")
        else:
            messagebox.showwarning(
                "Peringatan",
                "Tidak ada file hasil scraping terakhir.\n"
                "Silakan scraping terlebih dahulu atau pilih file secara manual."
            )
            self.upload_log("⚠️ Tidak ada file hasil scraping terakhir")
    
    def _refresh_logs(self):
        """
        Refresh the logs list from logging folder.
        """
        from src.core_logic.logger import get_all_sessions
        
        # Clear existing items
        for item in self.sessions_tree.get_children():
            self.sessions_tree.delete(item)
        
        # Get all sessions
        sessions = get_all_sessions("logging")
        
        if not sessions:
            self.session_details_text.delete(1.0, tk.END)
            self.session_details_text.insert(1.0, "Tidak ada riwayat scraping.\n\nSilakan jalankan scraping untuk membuat log.")
            return
        
        # Populate tree
        for session in sessions:
            session_info = session.get('session_info', {})
            stats = session.get('statistics', {})
            
            session_id = session_info.get('session_id', 'N/A')
            start_time = session_info.get('start_time', 'N/A')
            duration = f"{session_info.get('duration_seconds', 0):.1f}s"
            total = stats.get('total_dosen', 0)
            success = stats.get('success_count', 0)
            failed = stats.get('failed_count', 0)
            captcha = stats.get('captcha_count', 0)
            success_rate = stats.get('success_rate', '0%')
            
            self.sessions_tree.insert("", tk.END, values=(
                session_id, start_time, duration, total, success, failed, captcha, success_rate
            ), tags=(session.get('log_folder', ''),))
        
        self.session_details_text.delete(1.0, tk.END)
        self.session_details_text.insert(1.0, f"📊 Total {len(sessions)} session(s) ditemukan.\n\nDouble-click pada session untuk melihat detail.")
    
    def _on_session_double_click(self, event):
        """
        Handle double-click on session item.
        """
        selection = self.sessions_tree.selection()
        if not selection:
            return
        
        # Get log folder from tags
        item = selection[0]
        tags = self.sessions_tree.item(item, "tags")
        if not tags:
            return
        
        log_folder = tags[0]
        
        # Read summary file
        summary_file = None
        if os.path.exists(log_folder):
            for file in os.listdir(log_folder):
                if file.startswith("summary_") and file.endswith(".json"):
                    summary_file = os.path.join(log_folder, file)
                    break
        
        if not summary_file or not os.path.exists(summary_file):
            self.session_details_text.delete(1.0, tk.END)
            self.session_details_text.insert(1.0, "❌ File summary tidak ditemukan.")
            return
        
        # Load and display summary
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Format details
            details = f"{'='*60}\n"
            details += f"SESSION DETAILS\n"
            details += f"{'='*60}\n\n"
            
            session_info = data.get('session_info', {})
            details += f"📌 Session ID: {session_info.get('session_id', 'N/A')}\n"
            details += f"🕐 Start: {session_info.get('start_time', 'N/A')}\n"
            details += f"🕑 End: {session_info.get('end_time', 'N/A')}\n"
            details += f"⏱️  Duration: {session_info.get('duration_seconds', 0):.2f} seconds\n"
            details += f"📁 Folder: {log_folder}\n\n"
            
            stats = data.get('statistics', {})
            details += f"{'='*60}\n"
            details += f"STATISTICS\n"
            details += f"{'='*60}\n\n"
            details += f"Total Dosen: {stats.get('total_dosen', 0)}\n"
            details += f"✅ Success: {stats.get('success_count', 0)}\n"
            details += f"❌ Failed: {stats.get('failed_count', 0)}\n"
            details += f"🤖 CAPTCHA: {stats.get('captcha_count', 0)}\n"
            details += f"📊 Success Rate: {stats.get('success_rate', '0%')}\n\n"
            
            # Success list
            success_list = data.get('success_list', [])
            if success_list:
                details += f"{'='*60}\n"
                details += f"✅ SUCCESS LIST ({len(success_list)})\n"
                details += f"{'='*60}\n"
                for idx, name in enumerate(success_list, 1):
                    details += f"{idx}. {name}\n"
                details += "\n"
            
            # Failed list
            failed_list = data.get('failed_list', [])
            if failed_list:
                details += f"{'='*60}\n"
                details += f"❌ FAILED LIST ({len(failed_list)})\n"
                details += f"{'='*60}\n"
                for idx, name in enumerate(failed_list, 1):
                    details += f"{idx}. {name}\n"
                details += "\n"
            
            # CAPTCHA list
            captcha_list = data.get('captcha_list', [])
            if captcha_list:
                details += f"{'='*60}\n"
                details += f"🤖 CAPTCHA BLOCKED ({len(captcha_list)})\n"
                details += f"{'='*60}\n"
                for idx, name in enumerate(captcha_list, 1):
                    details += f"{idx}. {name}\n"
                details += "\n"
            
            # Processed list
            processed_list = data.get('dosen_processed', [])
            if processed_list:
                details += f"{'='*60}\n"
                details += f"📝 ALL PROCESSED ({len(processed_list)})\n"
                details += f"{'='*60}\n"
                for idx, name in enumerate(processed_list, 1):
                    details += f"{idx}. {name}\n"
            
            self.session_details_text.delete(1.0, tk.END)
            self.session_details_text.insert(1.0, details)
            
        except Exception as e:
            self.session_details_text.delete(1.0, tk.END)
            self.session_details_text.insert(1.0, f"❌ Error reading summary:\n{str(e)}")
    
    def _open_logs_folder(self):
        """
        Open the logging folder in file explorer.
        """
        log_dir = "logging"
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Open folder in explorer
        import subprocess
        if os.name == 'nt':  # Windows
            os.startfile(log_dir)
        elif os.name == 'posix':  # Mac/Linux
            subprocess.call(['open', log_dir] if sys.platform == 'darwin' else ['xdg-open', log_dir])
    
    def _start_upload(self):
        """
        Start the upload process in a separate thread.
        """
        # Validation
        if not self.excel_file_path.get():
            messagebox.showerror("Error", "Pilih file Excel terlebih dahulu!")
            return
        
        if not os.path.exists(self.excel_file_path.get()):
            messagebox.showerror("Error", f"File tidak ditemukan:\n{self.excel_file_path.get()}")
            return
        
        if not self.spreadsheet_url.get():
            messagebox.showerror("Error", "Masukkan URL Google Spreadsheet!")
            return
        
        if not self.sheet_name.get():
            messagebox.showerror("Error", "Masukkan nama sheet!")
            return
        
        # Check if Apps Script URL configured
        if not self.config['apps_script_url'] or 'YOUR_SCRIPT_ID_HERE' in self.config['apps_script_url']:
            messagebox.showerror(
                "Error",
                "APPS_SCRIPT_URL belum dikonfigurasi!\n\n"
                "Silakan:\n"
                "1. Edit file .env\n"
                "2. Isi APPS_SCRIPT_URL dengan URL Apps Script Anda\n"
                "3. Restart aplikasi\n\n"
                "Lihat dokumentasi di APPS_SCRIPT_SETUP.md"
            )
            return
        
        # Disable upload button
        self.upload_btn.config(state=tk.DISABLED)
        self.is_uploading = True
        
        # Clear log
        self.upload_log_text.delete(1.0, tk.END)
        
        # Start upload in separate thread
        thread = threading.Thread(target=self._run_upload, daemon=True)
        thread.start()
    
    def _run_upload(self):
        """
        Main upload logic (runs in separate thread).
        """
        try:
            self.upload_log("=" * 60)
            self.upload_log("🚀 MEMULAI UPLOAD KE GOOGLE SHEETS")
            self.upload_log("=" * 60)
            
            excel_file = self.excel_file_path.get()
            spreadsheet_url = self.spreadsheet_url.get()
            sheet_name = self.sheet_name.get()
            
            self.upload_log(f"📂 File: {os.path.basename(excel_file)}")
            self.upload_log(f"📊 Target Sheet: {sheet_name}")
            self.upload_log("")
            
            # Call transfer function
            result = transfer_data_to_sheets(
                excel_file_path=excel_file,
                spreadsheet_url=spreadsheet_url,
                sheet_name=sheet_name,
                web_app_url=self.config['apps_script_url'],
                status_callback=self.upload_log
            )
            
            self.upload_log("")
            self.upload_log("=" * 60)
            self.upload_log("🎉 UPLOAD SELESAI!")
            self.upload_log("=" * 60)
            
            messagebox.showinfo(
                "Sukses",
                f"Data berhasil diupload ke Google Sheets!\n\n"
                f"Sheet: {sheet_name}\n"
                f"Baris: {result.get('rowsWritten', 'N/A')}"
            )
            
        except Exception as e:
            error_msg = str(e)
            self.upload_log(f"\n❌ ERROR: {error_msg}")
            
            # Detailed error message for 403 Forbidden
            if "403" in error_msg or "Forbidden" in error_msg:
                detailed_msg = (
                    "Upload gagal dengan error 403 Forbidden.\n\n"
                    "KEMUNGKINAN PENYEBAB:\n"
                    "1. Apps Script belum di-deploy dengan benar\n"
                    "2. Permission 'Who has access' tidak diset ke 'Anyone'\n\n"
                    "CARA MEMPERBAIKI:\n"
                    "1. Buka Apps Script di script.google.com\n"
                    "2. Klik Deploy → Manage Deployments\n"
                    "3. Edit deployment yang ada atau buat baru\n"
                    "4. Set 'Execute as' = Me (email Anda)\n"
                    "5. Set 'Who has access' = Anyone\n"
                    "6. Klik Deploy dan copy URL baru\n"
                    "7. Update APPS_SCRIPT_URL di file .env\n"
                    "8. Restart aplikasi\n\n"
                    f"Detail Error:\n{error_msg}\n\n"
                    "Lihat dokumentasi lengkap di APPS_SCRIPT_SETUP.md"
                )
                messagebox.showerror("Error 403: Forbidden", detailed_msg)
            else:
                messagebox.showerror("Error", f"Upload gagal:\n\n{error_msg}")
        
        finally:
            # Re-enable upload button
            self.upload_btn.config(state=tk.NORMAL)
            self.is_uploading = False
    
    def _start_scraping(self):
        """
        Start the scraping process in a separate thread.
        """
        # Validation based on mode
        mode = self.scraping_mode.get()
        
        if mode == "batch":
            # Validate file input
            if not self.input_file_path.get():
                messagebox.showerror("Error", "Pilih file input terlebih dahulu!")
                return
            
            if not os.path.exists(self.input_file_path.get()):
                messagebox.showerror("Error", f"File tidak ditemukan:\n{self.input_file_path.get()}")
                return
        else:  # single mode
            # Validate name input
            if not self.single_dosen_name.get().strip():
                messagebox.showerror("Error", "Masukkan nama dosen terlebih dahulu!")
                self.single_entry.focus()
                return
        
        # Disable start button, enable stop button
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.is_running = True
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Switch to Real-time Log tab
        self.notebook.select(1)  # Index 1 = Tab "📝 Log Aktivitas"
        
        # Start scraping in separate thread
        thread = threading.Thread(target=self._run_scraping, daemon=True)
        thread.start()
    
    def _stop_scraping(self):
        """
        Stop the scraping process.
        """
        self.is_running = False
        self.log("⏹️ Proses dihentikan oleh user")
        self._update_status("Stopped by user")
        
        # Re-enable buttons
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def _run_scraping(self):
        """
        Main scraping logic (runs in separate thread).
        """
        try:
            self.log("=" * 60)
            self.log("🚀 MEMULAI PROSES SCRAPING")
            self.log("=" * 60)
            self._update_status("Running...")
            
            mode = self.scraping_mode.get()
            
            # Step 1: Get dosen names based on mode
            if mode == "batch":
                input_file = self.input_file_path.get()
                self.log(f"\n[1/5] 📖 Membaca file: {os.path.basename(input_file)}")
                dosen_names_raw = read_dosen_from_file(input_file)
                self.log(f"      ✅ Berhasil membaca {len(dosen_names_raw)} nama dosen")
                
                if not dosen_names_raw:
                    raise ValueError("Tidak ada nama dosen dalam file")
                    
                # For filename
                input_filename = os.path.splitext(os.path.basename(input_file))[0]
            else:  # single mode
                single_name = self.single_dosen_name.get().strip()
                self.log(f"\n[1/5] 👤 Mode: Scraping Perorangan")
                self.log(f"      Nama: {single_name}")
                dosen_names_raw = [single_name]
                
                # For filename - clean the name
                input_filename = clean_dosen_name(single_name).replace(" ", "_").lower()
            
            # Step 2: Clean names
            self.log(f"\n[2/5] 🧹 Membersihkan nama dari gelar akademis...")
            dosen_names_clean = [clean_dosen_name(name) for name in dosen_names_raw]
            
            # Preview
            self.log("      Preview:")
            for i, (raw, clean) in enumerate(zip(dosen_names_raw[:3], dosen_names_clean[:3]), 1):
                self.log(f"      {i}. {raw} → {clean}")
            if len(dosen_names_raw) > 3:
                self.log(f"      ... dan {len(dosen_names_raw) - 3} nama lainnya")
            
            if not self.is_running:
                return
            
            # Step 3: Scraping
            self.log(f"\n[3/5] 🔍 Memulai scraping dari Google Scholar...")
            self.log(f"      Mode: {'Headless' if self.headless_mode.get() else 'Browser Visible'}")
            self.log(f"      Timeout: {self.wait_time.get()} detik")
            self.log(f"      CAPTCHA Timeout: {self.captcha_wait_time.get()} menit")
            
            # Prepare year list if valid range is selected
            year_start = self.year_from.get()
            year_end = self.year_to.get()
            if year_start <= year_end:
                years_list = list(range(year_start, year_end + 1))
                self.log(f"      Cited-by per tahun: {year_start} - {year_end}")
            else:
                years_list = None
                self.log(f"      Cited-by per tahun: semua (range tidak valid)")
            
            scraper = GoogleScholarScraper(
                headless=self.headless_mode.get(),
                wait_time=self.wait_time.get(),
                captcha_wait_minutes=self.captcha_wait_time.get()
            )
            
            df_results = scraper.run_scraper(dosen_names_clean, years=years_list)
            
            if not self.is_running:
                return
            
            # Step 4: Results
            self.log(f"\n[4/5] ✅ Scraping selesai!")
            self.log(f"      Total publikasi: {len(df_results)}")
            
            if len(df_results) == 0:
                raise ValueError("Tidak ada data yang berhasil di-scrape")
            
            # Statistics
            if 'Nama Dosen' in df_results.columns:
                self.log("\n      📊 Statistik per dosen:")
                stats = df_results.groupby('Nama Dosen').size().sort_values(ascending=False)
                for dosen, count in stats.items():
                    self.log(f"      - {dosen}: {count} publikasi")
            
            # Step 5: Save results
            self.log(f"\n[5/5] 💾 Menyimpan hasil...")
            
            output_dir = ensure_output_directory("output")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"publikasi_{input_filename}_{timestamp}"
            
            output_format = self.output_format.get()
            
            if output_format in ["csv", "both"]:
                csv_path = save_to_csv(df_results, os.path.join(output_dir, f"{base_filename}.csv"))
                self.log(f"      ✅ CSV: {os.path.basename(csv_path)}")
            
            if output_format in ["excel", "both"]:
                excel_path = save_to_excel(df_results, os.path.join(output_dir, f"{base_filename}.xlsx"))
                self.log(f"      ✅ Excel: {os.path.basename(excel_path)}")
                # Save last scraped file for upload tab
                self.last_scraped_file = excel_path
            elif output_format == "csv":
                # If only CSV, still try to create Excel for upload
                excel_path = save_to_excel(df_results, os.path.join(output_dir, f"{base_filename}.xlsx"))
                self.last_scraped_file = excel_path
            
            self.log("\n" + "=" * 60)
            self.log("🎉 PROSES SELESAI!")
            self.log("=" * 60)
            self.log(f"📁 File tersimpan di folder: {output_dir}")
            
            # Notify about upload tab
            if self.last_scraped_file:
                self.log(f"\n💡 Tip: Gunakan tab 'Upload ke Sheets' untuk mengunggah hasil ke Google Sheets")
            
            self._update_status("Completed successfully!")
            
            messagebox.showinfo(
                "Sukses",
                f"Scraping selesai!\n\n"
                f"Total publikasi: {len(df_results)}\n"
                f"Hasil tersimpan di folder: {output_dir}"
            )
            
        except Exception as e:
            self.log(f"\n❌ ERROR: {str(e)}")
            self._update_status("Error occurred")
            messagebox.showerror("Error", f"Terjadi kesalahan:\n{str(e)}")
        
        finally:
            # Re-enable buttons
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.is_running = False


def run_gui():
    """
    Main function to run the GUI application.
    """
    root = tk.Tk()
    app = GoogleScholarScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
