"""
GUI Application for Google Scholar Scraper
Menggunakan Tkinter untuk antarmuka pengguna yang sederhana dan intuitif.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core_logic.file_handler import (
    read_dosen_from_file,
    save_to_csv,
    save_to_excel,
    generate_summary_docx,
    ensure_output_directory
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
        self.root.title("Google Scholar Scraper - Aplikasi Scraping Publikasi Dosen")
        self.root.geometry("800x700")
        self.root.resizable(False, False)
        
        # Variables
        self.input_file_path = tk.StringVar()
        self.output_format = tk.StringVar(value="csv")  # Default: CSV
        self.headless_mode = tk.BooleanVar(value=False)
        self.wait_time = tk.IntVar(value=10)
        self.is_running = False
        
        # Setup GUI components
        self._setup_ui()
        
        # Load available input files
        self._load_input_files()
    
    def _setup_ui(self):
        """
        Setup all UI components.
        """
        # Title Frame
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🎓 Google Scholar Scraper",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        # Main Content Frame
        main_frame = tk.Frame(self.root, padx=20, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== Section 1: File Input =====
        input_section = tk.LabelFrame(
            main_frame,
            text="📁 Pilih File Input",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        input_section.pack(fill=tk.X, pady=(0, 10))
        
        # File selection
        file_frame = tk.Frame(input_section)
        file_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            file_frame,
            text="File Dosen:",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.file_combo = ttk.Combobox(
            file_frame,
            textvariable=self.input_file_path,
            state="readonly",
            width=40,
            font=("Arial", 10)
        )
        self.file_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_btn = tk.Button(
            file_frame,
            text="🔄 Refresh",
            command=self._load_input_files,
            bg="#3498db",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            relief=tk.FLAT,
            padx=10
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        browse_btn = tk.Button(
            file_frame,
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
        
        # ===== Section 5: Log Output =====
        log_section = tk.LabelFrame(
            main_frame,
            text="📋 Log Aktivitas",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        log_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(
            log_section,
            wrap=tk.WORD,
            height=12,
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
        Add message to log text area.
        
        Args:
            message (str): Message to log
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def _update_status(self, message):
        """
        Update status bar.
        
        Args:
            message (str): Status message
        """
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def _start_scraping(self):
        """
        Start the scraping process in a separate thread.
        """
        # Validation
        if not self.input_file_path.get():
            messagebox.showerror("Error", "Pilih file input terlebih dahulu!")
            return
        
        if not os.path.exists(self.input_file_path.get()):
            messagebox.showerror("Error", f"File tidak ditemukan:\n{self.input_file_path.get()}")
            return
        
        # Disable start button, enable stop button
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.is_running = True
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
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
            
            input_file = self.input_file_path.get()
            
            # Step 1: Read input file
            self.log(f"\n[1/5] 📖 Membaca file: {os.path.basename(input_file)}")
            dosen_names_raw = read_dosen_from_file(input_file)
            self.log(f"      ✅ Berhasil membaca {len(dosen_names_raw)} nama dosen")
            
            if not dosen_names_raw:
                raise ValueError("Tidak ada nama dosen dalam file")
            
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
            
            scraper = GoogleScholarScraper(
                headless=self.headless_mode.get(),
                wait_time=self.wait_time.get()
            )
            
            df_results = scraper.run_scraper(dosen_names_clean)
            
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
            input_filename = os.path.splitext(os.path.basename(input_file))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"publikasi_{input_filename}_{timestamp}"
            
            output_format = self.output_format.get()
            
            if output_format in ["csv", "both"]:
                csv_path = save_to_csv(df_results, os.path.join(output_dir, f"{base_filename}.csv"))
                self.log(f"      ✅ CSV: {os.path.basename(csv_path)}")
            
            if output_format in ["excel", "both"]:
                excel_path = save_to_excel(df_results, os.path.join(output_dir, f"{base_filename}.xlsx"))
                self.log(f"      ✅ Excel: {os.path.basename(excel_path)}")
            
            self.log("\n" + "=" * 60)
            self.log("🎉 PROSES SELESAI!")
            self.log("=" * 60)
            self.log(f"📁 File tersimpan di folder: {output_dir}")
            
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
