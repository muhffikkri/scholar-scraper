"""
Main entry point untuk aplikasi Google Scholar Scraper.
Mendukung mode CLI dan GUI.

Usage:
    python main.py              # Mode CLI (default)
    python main.py --gui        # Mode GUI
    python main.py --cli        # Mode CLI (explicit)
"""

import os
import sys
import argparse
from datetime import datetime

# Tambahkan path src ke sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core_logic.file_handler import (
    read_dosen_from_file,
    save_to_csv,
    save_to_excel,
    generate_summary_docx,
    ensure_output_directory
)
from core_logic.utils import clean_dosen_name
from core_logic.scraper import GoogleScholarScraper


# ==================== KONFIGURASI CLI ====================
INPUT_FILE_PATH = "input/daftar_dosen.csv"
OUTPUT_DIR = "output"
HEADLESS_MODE = False
WAIT_TIME = 10
# ========================================================


def run_cli():
    """Menjalankan aplikasi dalam mode CLI."""
    print("=" * 70)
    print("GOOGLE SCHOLAR SCRAPER - MODE CLI")
    print("=" * 70)
    print()
    
    # Step 1: Validasi file input
    print(f"[1/6] Memeriksa file input: {INPUT_FILE_PATH}")
    if not os.path.exists(INPUT_FILE_PATH):
        print(f"ERROR: File tidak ditemukan: {INPUT_FILE_PATH}")
        print(f"Silakan buat file tersebut atau ubah INPUT_FILE_PATH di main.py")
        return
    
    # Step 2: Baca nama dosen dari file
    print(f"[2/6] Membaca daftar nama dosen...")
    try:
        dosen_names_raw = read_dosen_from_file(INPUT_FILE_PATH)
        print(f"      Berhasil membaca {len(dosen_names_raw)} nama dosen")
    except Exception as e:
        print(f"ERROR: Gagal membaca file: {e}")
        return
    
    if not dosen_names_raw:
        print("ERROR: Tidak ada nama dosen dalam file")
        return
    
    # Step 3: Bersihkan nama
    print(f"[3/6] Membersihkan nama dari gelar akademis...")
    dosen_names_clean = [clean_dosen_name(name) for name in dosen_names_raw]
    
    print("      Preview:")
    for i, (raw, clean) in enumerate(zip(dosen_names_raw[:3], dosen_names_clean[:3]), 1):
        print(f"      {i}. {raw} → {clean}")
    if len(dosen_names_raw) > 3:
        print(f"      ... dan {len(dosen_names_raw) - 3} nama lainnya")
    print()
    
    # Step 4: Scraping
    print(f"[4/6] Memulai scraping...")
    print(f"      Mode: {'Headless' if HEADLESS_MODE else 'Browser visible'}")
    print(f"      Timeout: {WAIT_TIME} detik")
    print()
    
    scraper = GoogleScholarScraper(headless=HEADLESS_MODE, wait_time=WAIT_TIME)
    
    try:
        df_results = scraper.run_scraper(dosen_names_clean)
    except Exception as e:
        print(f"ERROR: {e}")
        return
    
    # Step 5: Validasi
    print()
    print(f"[5/6] Scraping selesai! Total: {len(df_results)} publikasi")
    
    if len(df_results) == 0:
        print("      PERINGATAN: Tidak ada data")
        return
    
    if 'Nama Dosen' in df_results.columns:
        print("\n      Statistik:")
        stats = df_results.groupby('Nama Dosen').size().sort_values(ascending=False)
        for dosen, count in stats.items():
            print(f"      - {dosen}: {count}")
    
    # Step 6: Simpan
    print()
    print(f"[6/6] Menyimpan hasil...")
    
    output_dir = ensure_output_directory(OUTPUT_DIR)
    input_filename = os.path.splitext(os.path.basename(INPUT_FILE_PATH))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"publikasi_{input_filename}_{timestamp}"
    
    try:
        csv_path = save_to_csv(df_results, os.path.join(output_dir, f"{base_filename}.csv"))
        print(f"      ✓ CSV: {os.path.basename(csv_path)}")
        
        excel_path = save_to_excel(df_results, os.path.join(output_dir, f"{base_filename}.xlsx"))
        print(f"      ✓ Excel: {os.path.basename(excel_path)}")
        
        docx_path = generate_summary_docx(df_results, os.path.join(output_dir, f"{base_filename}_summary.docx"))
        print(f"      ✓ DOCX: {os.path.basename(docx_path)}")
    except Exception as e:
        print(f"ERROR: {e}")
        return
    
    print()
    print("=" * 70)
    print("SELESAI!")
    print("=" * 70)
    print(f"Output: {output_dir}")
    print()


def run_gui():
    """Menjalankan aplikasi dalam mode GUI."""
    try:
        from gui.app import GoogleScholarScraperGUI
        import tkinter as tk
        
        print("Memulai GUI...")
        root = tk.Tk()
        app = GoogleScholarScraperGUI(root)
        root.mainloop()
    except ImportError as e:
        print(f"ERROR: Gagal import GUI module: {e}")
        print("Pastikan semua dependencies terinstall.")
        sys.exit(1)


def main():
    """Main entry point dengan argparse."""
    parser = argparse.ArgumentParser(
        description="Google Scholar Scraper - Scraping publikasi dosen dari Google Scholar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Mode CLI (default)
  python main.py --gui        # Mode GUI
  python main.py --cli        # Mode CLI (explicit)
        """
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Jalankan dalam mode GUI (graphical user interface)'
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Jalankan dalam mode CLI (command line interface) - default'
    )
    
    args = parser.parse_args()
    
    # Determine mode
    if args.gui:
        run_gui()
    else:
        # Default to CLI
        run_cli()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDibatalkan oleh user (Ctrl+C)")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
