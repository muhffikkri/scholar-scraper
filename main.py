"""
Main entry point untuk aplikasi Google Scholar Scraper.
Script ini mengorkestrasikan alur kerja lengkap dari membaca input hingga menyimpan hasil.
"""

import os
import sys
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


# ==================== KONFIGURASI ====================
# Ubah path ini sesuai dengan lokasi file input Anda
INPUT_FILE_PATH = "input/daftar_dosen.csv"  # atau .txt

# Konfigurasi output
OUTPUT_DIR = "output"
OUTPUT_PREFIX = "publikasi_dosen"

# Konfigurasi scraper
HEADLESS_MODE = False  # Set True untuk menjalankan browser tanpa GUI
WAIT_TIME = 10  # Waktu tunggu maksimal dalam detik

# ======================================================


def main():
    """
    Fungsi utama yang mengorkestrasikan seluruh proses scraping.
    """
    print("=" * 70)
    print("GOOGLE SCHOLAR SCRAPER - APLIKASI SCRAPING PUBLIKASI DOSEN")
    print("=" * 70)
    print()
    
    # Step 1: Validasi file input
    print(f"[1/6] Memeriksa file input: {INPUT_FILE_PATH}")
    if not os.path.exists(INPUT_FILE_PATH):
        print(f"ERROR: File tidak ditemukan: {INPUT_FILE_PATH}")
        print(f"Silakan buat file tersebut atau ubah INPUT_FILE_PATH di main.py")
        return
    
    # Step 2: Baca nama dosen dari file
    print(f"[2/6] Membaca daftar nama dosen dari file...")
    try:
        dosen_names_raw = read_dosen_from_file(INPUT_FILE_PATH)
        print(f"      Berhasil membaca {len(dosen_names_raw)} nama dosen")
    except Exception as e:
        print(f"ERROR: Gagal membaca file: {e}")
        return
    
    if not dosen_names_raw:
        print("ERROR: Tidak ada nama dosen yang ditemukan dalam file")
        return
    
    # Step 3: Bersihkan nama dosen dari gelar
    print(f"[3/6] Membersihkan nama dosen dari gelar akademis...")
    dosen_names_clean = [clean_dosen_name(name) for name in dosen_names_raw]
    
    # Tampilkan preview
    print("      Preview nama yang dibersihkan:")
    for i, (raw, clean) in enumerate(zip(dosen_names_raw[:5], dosen_names_clean[:5]), 1):
        print(f"      {i}. {raw} → {clean}")
    if len(dosen_names_raw) > 5:
        print(f"      ... dan {len(dosen_names_raw) - 5} nama lainnya")
    print()
    
    # Step 4: Jalankan scraper
    print(f"[4/6] Memulai proses scraping...")
    print(f"      Mode: {'Headless (tanpa GUI)' if HEADLESS_MODE else 'Browser visible'}")
    print(f"      Timeout: {WAIT_TIME} detik")
    print()
    
    scraper = GoogleScholarScraper(headless=HEADLESS_MODE, wait_time=WAIT_TIME)
    
    try:
        df_results = scraper.run_scraper(dosen_names_clean)
    except Exception as e:
        print(f"ERROR: Terjadi kesalahan saat scraping: {e}")
        return
    
    # Step 5: Validasi hasil
    print()
    print(f"[5/6] Scraping selesai!")
    print(f"      Total publikasi ditemukan: {len(df_results)}")
    
    if len(df_results) == 0:
        print("      PERINGATAN: Tidak ada data yang berhasil di-scrape")
        print("      Pastikan nama dosen benar dan memiliki profil Google Scholar")
        return
    
    # Tampilkan statistik per dosen
    if 'Nama Dosen' in df_results.columns:
        print("\n      Statistik per dosen:")
        stats = df_results.groupby('Nama Dosen').size().sort_values(ascending=False)
        for dosen, count in stats.items():
            print(f"      - {dosen}: {count} publikasi")
    
    # Step 6: Simpan hasil
    print()
    print(f"[6/6] Menyimpan hasil ke berbagai format...")
    
    # Pastikan direktori output ada
    output_dir = ensure_output_directory(OUTPUT_DIR)
    
    # Buat timestamp untuk nama file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{OUTPUT_PREFIX}_{timestamp}"
    
    try:
        # Simpan ke CSV
        csv_path = save_to_csv(df_results, os.path.join(output_dir, f"{base_filename}.csv"))
        print(f"      ✓ CSV disimpan: {csv_path}")
        
        # Simpan ke Excel
        excel_path = save_to_excel(df_results, os.path.join(output_dir, f"{base_filename}.xlsx"))
        print(f"      ✓ Excel disimpan: {excel_path}")
        
        # Simpan ringkasan ke DOCX
        docx_path = generate_summary_docx(df_results, os.path.join(output_dir, f"{base_filename}_summary.docx"))
        print(f"      ✓ Ringkasan DOCX disimpan: {docx_path}")
        
    except Exception as e:
        print(f"ERROR: Gagal menyimpan hasil: {e}")
        return
    
    # Selesai
    print()
    print("=" * 70)
    print("PROSES SELESAI!")
    print("=" * 70)
    print(f"Semua file output tersimpan di folder: {output_dir}")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProses dibatalkan oleh pengguna (Ctrl+C)")
    except Exception as e:
        print(f"\n\nERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
