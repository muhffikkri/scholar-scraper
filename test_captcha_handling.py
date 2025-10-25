"""
Test script untuk CAPTCHA handling.
Script ini mendemonstrasikan bagaimana scraper menangani CAPTCHA dengan manual solving.
"""

from src.core_logic.scraper import GoogleScholarScraper

def test_captcha_handling():
    """
    Test CAPTCHA handling dengan satu nama dosen.
    
    CATATAN:
    - Script ini akan membuka browser (non-headless)
    - Jika CAPTCHA muncul, Anda akan punya waktu 5 menit untuk solve
    - Script akan otomatis melanjutkan setelah CAPTCHA terselesaikan
    """
    print("="*60)
    print("TESTING CAPTCHA HANDLING")
    print("="*60)
    print("Mode: Browser Visible (Non-Headless)")
    print("CAPTCHA Timeout: 5 menit")
    print("="*60)
    print("\nJika CAPTCHA muncul:")
    print("1. Browser akan tetap terbuka")
    print("2. Selesaikan CAPTCHA secara manual")
    print("3. Script akan otomatis melanjutkan\n")
    
    # Test dengan satu nama
    test_names = ["Harjum Muharam"]  # Ganti dengan nama yang valid
    
    # Initialize scraper dengan mode non-headless
    scraper = GoogleScholarScraper(
        headless=False,  # Browser visible untuk manual CAPTCHA solving
        wait_time=10,
        captcha_wait_minutes=5  # 5 menit untuk solve CAPTCHA
    )
    
    print(f"Testing dengan nama: {test_names[0]}\n")
    
    try:
        # Run scraper
        df = scraper.run_scraper(test_names, years=[2020, 2021, 2022, 2023, 2024, 2025])
        
        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        
        if len(df) > 0:
            print(f"✅ Berhasil scrape {len(df)} publikasi")
            print(f"\nSample data (5 publikasi pertama):")
            print(df[['Judul', 'Tahun', 'Sitasi']].head())
            
            # Show cited_by columns
            cited_cols = [col for col in df.columns if '_cited_by' in col]
            if cited_cols:
                print(f"\nCited-by per tahun:")
                print(df[['Judul'] + cited_cols].head())
        else:
            print("❌ Tidak ada data yang berhasil di-scrape")
            print("Kemungkinan:")
            print("1. CAPTCHA tidak diselesaikan dalam waktu yang ditentukan")
            print("2. Profil tidak ditemukan")
            print("3. Error lainnya (cek log)")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test dibatalkan oleh user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_captcha_handling()
