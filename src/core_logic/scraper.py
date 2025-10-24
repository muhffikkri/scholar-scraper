"""
Google Scholar scraper module.
Berisi logika utama untuk scraping publikasi menggunakan Selenium dan BeautifulSoup4.
"""

import time
import re
from typing import List, Dict, Set, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    StaleElementReferenceException,
    ElementClickInterceptedException
)
from bs4 import BeautifulSoup
import pandas as pd
from .utils import parse_publication_info, parse_venue_from_detail


class GoogleScholarScraper:
    """
    Kelas untuk melakukan scraping publikasi dari Google Scholar.
    """
    
    def __init__(self, headless: bool = False, wait_time: int = 10):
        """
        Inisialisasi scraper dengan konfigurasi Selenium.
        
        Args:
            headless (bool): Jika True, browser akan berjalan tanpa GUI
            wait_time (int): Waktu maksimal tunggu dalam detik untuk WebDriverWait
        """
        self.wait_time = wait_time
        self.headless = headless
        self.driver = None
        self.results = []
        
    def _init_driver(self):
        """
        Inisialisasi Selenium WebDriver dengan konfigurasi yang optimal.
        """
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless')
        
        # Tambahkan opsi untuk menghindari deteksi bot
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def _search_dosen(self, nama_dosen: str) -> bool:
        """
        Melakukan pencarian nama dosen di Google Scholar.
        
        Args:
            nama_dosen (str): Nama dosen yang akan dicari
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        try:
            # Navigasi ke halaman utama Google Scholar
            self.driver.get("https://scholar.google.com/schhp?hl=id")
            
            # Tunggu input field muncul
            wait = WebDriverWait(self.driver, self.wait_time)
            search_box = wait.until(
                EC.presence_of_element_located((By.ID, "gs_hdr_tsi"))
            )
            
            # Ketik nama dosen
            search_box.clear()
            search_box.send_keys(nama_dosen)
            
            # Klik tombol search
            search_button = self.driver.find_element(By.ID, "gs_hdr_tsb")
            search_button.click()
            
            # Tunggu hasil pencarian muncul
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"Error saat mencari {nama_dosen}: {e}")
            return False
    
    def _find_and_click_profile(self) -> Optional[str]:
        """
        Mencari dan mengklik link profil dosen di hasil pencarian.
        
        Returns:
            Optional[str]: URL profil jika ditemukan, None jika tidak
        """
        try:
            wait = WebDriverWait(self.driver, self.wait_time)
            
            # Cari link profil dalam tag <h4 class="gs_rt2"><a href="...">...</a></h4>
            profile_link = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h4.gs_rt2 a"))
            )
            
            profile_url = profile_link.get_attribute("href")
            
            # Klik link profil
            profile_link.click()
            
            # Tunggu halaman profil dimuat
            time.sleep(2)
            
            return profile_url
            
        except TimeoutException:
            print("Profil tidak ditemukan dalam waktu yang ditentukan")
            return None
        except Exception as e:
            print(f"Error saat mencari profil: {e}")
            return None
    
    def _load_all_publications(self):
        """
        Mengklik tombol 'Tampilkan lainnya' hingga semua publikasi dimuat.
        """
        while True:
            try:
                # Cari tombol "Tampilkan lainnya"
                show_more_button = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, "gsc_bpf_more"))
                )
                
                # Periksa apakah tombol disabled
                if show_more_button.get_attribute("disabled"):
                    break
                
                # Scroll ke tombol
                self.driver.execute_script("arguments[0].scrollIntoView(true);", show_more_button)
                time.sleep(0.5)
                
                # Klik tombol
                show_more_button.click()
                time.sleep(1.5)
                
            except TimeoutException:
                # Tidak ada tombol lagi, semua publikasi sudah dimuat
                break
            except Exception as e:
                # Error lainnya, hentikan loading
                print(f"Error saat loading publikasi: {e}")
                break
    
    def _scrape_publication_detail(self, detail_url: str) -> Dict[str, str]:
        """
        Scrape detail publikasi dari halaman detail artikel.
        Mengambil data langsung dari field terstruktur di gsc_oci_table.
        
        Args:
            detail_url (str): URL halaman detail artikel (untuk fallback)
            
        Returns:
            Dict[str, str]: Dictionary berisi detail publikasi
        """
        try:
            # NOTE: Sebaiknya menggunakan klik pada elemen, bukan navigasi langsung
            # Tapi karena kita sudah kembali ke profil, kita perlu navigasi ulang
            self.driver.get(detail_url)
            time.sleep(1.5)
            
            return self._scrape_publication_detail_from_current_page()
            
        except Exception as e:
            print(f"Error saat scraping detail: {e}")
            return {}
    
    def _scrape_publication_detail_from_current_page(self) -> Dict[str, str]:
        """
        Scrape detail publikasi dari halaman yang SUDAH DIBUKA.
        Mengambil data langsung dari field terstruktur di gsc_oci_table.
        
        Returns:
            Dict[str, str]: Dictionary berisi detail publikasi
        """
        try:
            
            # Tunggu tabel detail muncul
            wait = WebDriverWait(self.driver, self.wait_time)
            table = wait.until(
                EC.presence_of_element_located((By.ID, "gsc_oci_table"))
            )
            
            # Parse dengan BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            detail_table = soup.find('div', {'id': 'gsc_oci_table'})
            
            details = {}
            if detail_table:
                rows = detail_table.find_all('div', class_='gs_scl')
                for row in rows:
                    field = row.find('div', class_='gsc_oci_field')
                    value = row.find('div', class_='gsc_oci_value')
                    
                    if field and value:
                        field_text = field.get_text(strip=True)
                        value_text = value.get_text(strip=True)
                        
                        # Map field names (Indonesian) ke key yang digunakan
                        field_mapping = {
                            'Pengarang': 'Authors',
                            'Penulis': 'Authors',
                            'Tanggal terbit': 'Publication_Date',
                            'Jurnal': 'Journal',
                            'Jilid': 'Volume',
                            'Terbitan': 'Issue',
                            'Halaman': 'Pages',
                            'Penerbit': 'Publisher',
                            'Deskripsi': 'Description',
                            'Total kutipan': 'Total_Citations'
                        }
                        
                        # Gunakan mapped key jika ada, otherwise gunakan original
                        key = field_mapping.get(field_text, field_text)
                        details[key] = value_text

            # Parse cited-by per year dari grafik
            # Ambil dari <div id="gsc_oci_graph_bars">
            # Struktur: <span class="gsc_oci_g_t">tahun</span> untuk label tahun
            #           <span class="gsc_oci_g_al">angka</span> untuk jumlah sitasi
            cited_by_per_year = {}
            graph_bars = soup.find('div', id='gsc_oci_graph_bars')
            if graph_bars:
                # Ambil semua tahun
                year_spans = graph_bars.find_all('span', class_='gsc_oci_g_t')
                years = [span.get_text(strip=True) for span in year_spans]
                
                # Ambil semua anchor dengan class gsc_oci_g_a yang berisi angka sitasi
                citation_anchors = graph_bars.find_all('a', class_='gsc_oci_g_a')
                counts = []
                for anchor in citation_anchors:
                    count_span = anchor.find('span', class_='gsc_oci_g_al')
                    if count_span:
                        txt = count_span.get_text(strip=True)
                        try:
                            # Clean dan convert ke integer
                            count_value = int(txt.replace('\xa0', '').replace(',', '').replace('.', ''))
                            counts.append(count_value)
                        except Exception:
                            # Fallback: extract hanya angka
                            try:
                                count_value = int(re.sub(r'[^0-9]', '', txt) or '0')
                                counts.append(count_value)
                            except Exception:
                                counts.append(0)
                
                # Pasangkan tahun dengan jumlah sitasi
                # Asumsi: jumlah tahun = jumlah counts (seharusnya selalu sama)
                for i, year_str in enumerate(years):
                    try:
                        year_int = int(year_str)
                        count = counts[i] if i < len(counts) else 0
                        cited_by_per_year[year_int] = count
                    except (ValueError, IndexError):
                        # Skip jika tahun tidak valid atau index out of range
                        continue

            details['Cited_By_Per_Year'] = cited_by_per_year
            
            return details
            
        except Exception as e:
            print(f"Error saat scraping detail: {e}")
            return {}
    
    def _parse_publication_row(self, row_element, scraped_titles: Set[str]) -> Optional[Dict[str, str]]:
        """
        Parse satu baris publikasi dari halaman profil.
        
        Args:
            row_element: Element Selenium dari baris publikasi
            scraped_titles (Set[str]): Set judul yang sudah di-scrape
            
        Returns:
            Optional[Dict[str, str]]: Data publikasi atau None jika sudah di-scrape
        """
        try:
            soup = BeautifulSoup(row_element.get_attribute('innerHTML'), 'html.parser')
            
            # Ekstrak judul
            title_elem = soup.find('a', class_='gsc_a_at')
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            
            # Skip jika sudah di-scrape
            if title in scraped_titles:
                return None
            
            # Ekstrak link detail
            detail_link = title_elem.get('href', '')
            if detail_link:
                detail_link = "https://scholar.google.com" + detail_link
            
            # Ekstrak informasi publikasi
            pub_info_elem = soup.find('div', class_='gs_gray')
            authors = pub_info_elem.get_text(strip=True) if pub_info_elem else ''
            
            # Ekstrak venue dan tahun
            venue_elem = soup.find_all('div', class_='gs_gray')
            venue_info = venue_elem[1].get_text(strip=True) if len(venue_elem) > 1 else ''
            
            # Ekstrak tahun dan kutipan
            year_elem = soup.find('span', class_='gsc_a_h')
            year = year_elem.get_text(strip=True) if year_elem else ''
            
            cited_elem = soup.find('a', class_='gsc_a_ac')
            citations = cited_elem.get_text(strip=True) if cited_elem else '0'
            
            # Periksa apakah info lengkap (diakhiri dengan ...)
            is_incomplete = venue_info.endswith('...')
            
            publication_data = {
                'Judul': title,
                'Penulis': authors,
                'Venue_Raw': venue_info,  # Simpan venue mentah
                'Tahun': year,
                'Sitasi': citations,
                'Detail_Link': detail_link,
                'Is_Incomplete': is_incomplete
            }
            
            return publication_data
            
        except Exception as e:
            print(f"Error parsing row: {e}")
            return None
    
    def scrape_dosen_publications(self, nama_dosen: str) -> List[Dict[str, str]]:
        """
        Scrape semua publikasi untuk satu dosen.
        Strategi: Scrape artikel yang sudah dimuat di layar, baru tekan tombol "Tampilkan lainnya".
        
        Args:
            nama_dosen (str): Nama dosen yang sudah dibersihkan
            
        Returns:
            List[Dict[str, str]]: List berisi data publikasi
        """
        publications = []
        scraped_titles: Set[str] = set()
        
        try:
            # Cari dosen
            if not self._search_dosen(nama_dosen):
                print(f"Gagal mencari: {nama_dosen}")
                return publications
            
            # Klik profil
            profile_url = self._find_and_click_profile()
            if not profile_url:
                print(f"Profil tidak ditemukan untuk: {nama_dosen}")
                return publications
            
            print(f"Memproses profil: {nama_dosen}")
            
            # Loop untuk scraping batch per batch
            batch_number = 1
            has_more = True
            
            while has_more:
                print(f"\n  === Batch {batch_number} ===")
                
                # Dapatkan semua baris publikasi yang saat ini dimuat di layar
                pub_rows = self.driver.find_elements(By.CLASS_NAME, "gsc_a_tr")
                current_row_count = len(pub_rows)
                print(f"  Total artikel di layar: {current_row_count}")
                
                # Scrape semua artikel yang ada di layar
                for idx, row in enumerate(pub_rows):
                    try:
                        pub_data = self._parse_publication_row(row, scraped_titles)
                        
                        if not pub_data:
                            continue
                        
                        # SELALU masuk ke halaman detail untuk setiap artikel
                        # Strategi: Klik link artikel di halaman profil
                        try:
                            print(f"  [{idx+1}/{current_row_count}] Mengambil detail: {pub_data['Judul'][:50]}...")
                            
                            # Cari link artikel dengan class gsc_a_at di row ini
                            # Re-find row element untuk menghindari stale reference
                            current_rows = self.driver.find_elements(By.CLASS_NAME, "gsc_a_tr")
                            if idx < len(current_rows):
                                current_row = current_rows[idx]
                                
                                # Cari dan klik link judul artikel
                                article_link = current_row.find_element(By.CLASS_NAME, "gsc_a_at")
                                
                                # Scroll ke elemen agar terlihat
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", article_link)
                                time.sleep(0.3)
                                
                                # Klik link artikel
                                article_link.click()
                                time.sleep(1.5)
                                
                                # Sekarang kita ada di halaman detail, scrape datanya
                                details = self._scrape_publication_detail_from_current_page()
                                
                                # Jika ada detail, ambil langsung dari field terstruktur
                                if details:
                                    # Ambil data dari field yang sudah di-map
                                    pub_data['Journal_Name'] = details.get('Journal', '')
                                    pub_data['Volume'] = details.get('Volume', '')
                                    pub_data['Issue'] = details.get('Issue', '')
                                    pub_data['Pages'] = details.get('Pages', '')
                                    pub_data['Publisher'] = details.get('Publisher', '')
                                    
                                    # Update penulis dari field Authors jika ada
                                    if details.get('Authors'):
                                        pub_data['Penulis'] = details.get('Authors')
                                    
                                    # Extract tahun dari Publication_Date jika ada (format: 2014/7/1)
                                    if details.get('Publication_Date'):
                                        try:
                                            pub_date = details.get('Publication_Date')
                                            year_from_date = pub_date.split('/')[0] if '/' in pub_date else pub_date.split('-')[0]
                                            if year_from_date.isdigit():
                                                pub_data['Tahun'] = year_from_date
                                        except Exception:
                                            pass
                                    
                                    # Simpan cited_by per year (PRIORITAS UTAMA)
                                    cited_map = details.get('Cited_By_Per_Year', {})
                                    pub_data['Cited_By_Per_Year'] = cited_map
                                else:
                                    # Jika gagal scrape detail, parse dari venue_raw
                                    venue_parsed = parse_publication_info(pub_data['Venue_Raw'])
                                    pub_data['Journal_Name'] = venue_parsed['journal_name']
                                    pub_data['Volume'] = venue_parsed['volume']
                                    pub_data['Issue'] = venue_parsed['issue']
                                    pub_data['Pages'] = venue_parsed['pages']
                                    pub_data['Publisher'] = venue_parsed['publisher']
                                    pub_data['Cited_By_Per_Year'] = {}
                                
                                # Kembali ke halaman profil
                                self.driver.back()
                                time.sleep(1)
                            else:
                                raise Exception("Row index out of range")

                        except Exception as e:
                            print(f"    ⚠️  Gagal mengambil detail: {e}")
                            # Fallback: parse dari venue_raw dan set cited_by kosong
                            venue_parsed = parse_publication_info(pub_data['Venue_Raw'])
                            pub_data['Journal_Name'] = venue_parsed['journal_name']
                            pub_data['Volume'] = venue_parsed['volume']
                            pub_data['Issue'] = venue_parsed['issue']
                            pub_data['Pages'] = venue_parsed['pages']
                            pub_data['Publisher'] = venue_parsed['publisher']
                            pub_data['Cited_By_Per_Year'] = {}
                            
                            # Pastikan kembali ke profil jika error terjadi setelah klik
                            try:
                                if "citations" in self.driver.current_url and "view_op=view_citation" in self.driver.current_url:
                                    self.driver.back()
                                    time.sleep(1)
                            except Exception:
                                pass
                        
                        # Tambahkan nama dosen
                        pub_data['Nama Dosen'] = nama_dosen
                        
                        # Simpan link detail sebagai kolom Link
                        pub_data['Link'] = pub_data['Detail_Link']
                        
                        # Hapus flag is_incomplete dan data sementara
                        del pub_data['Is_Incomplete']
                        del pub_data['Detail_Link']
                        del pub_data['Venue_Raw']
                        
                        # Tambahkan ke hasil
                        publications.append(pub_data)
                        scraped_titles.add(pub_data['Judul'])
                        
                    except StaleElementReferenceException:
                        # Element sudah tidak valid, skip
                        continue
                    except Exception as e:
                        print(f"    ⚠️  Error pada publikasi {idx+1}: {e}")
                        continue
                
                print(f"  ✅ Batch {batch_number} selesai: {len(publications)} total publikasi")
                
                # Coba tekan tombol "Tampilkan lainnya" untuk load batch berikutnya
                try:
                    show_more_button = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.ID, "gsc_bpf_more"))
                    )
                    
                    # Periksa apakah tombol disabled
                    if show_more_button.get_attribute("disabled"):
                        print(f"  ℹ️  Tidak ada artikel lagi (tombol disabled)")
                        has_more = False
                    else:
                        # Scroll ke tombol dan klik
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", show_more_button)
                        time.sleep(0.5)
                        show_more_button.click()
                        print(f"  ⏬ Memuat batch berikutnya...")
                        time.sleep(1.5)
                        batch_number += 1
                        
                except TimeoutException:
                    # Tidak ada tombol lagi, semua publikasi sudah dimuat
                    print(f"  ℹ️  Tidak ada tombol 'Tampilkan lainnya'")
                    has_more = False
                except Exception as e:
                    print(f"  ⚠️  Error saat mencari tombol: {e}")
                    has_more = False
            
            print(f"\n✅ Selesai: {nama_dosen} - {len(publications)} publikasi total")
            
        except Exception as e:
            print(f"❌ Error saat scraping {nama_dosen}: {e}")
        
        return publications
    
    def run_scraper(self, dosen_list: List[str], years: Optional[List[int]] = None) -> pd.DataFrame:
        """
        Menjalankan scraper untuk list nama dosen.
        
        Args:
            dosen_list (List[str]): List nama dosen yang sudah dibersihkan
            
        Returns:
            pd.DataFrame: DataFrame berisi semua publikasi
        """
        all_publications = []
        # store requested years (set) to filter output columns later
        self.years_to_collect = set(years) if years else None
        
        try:
            # Inisialisasi driver
            self._init_driver()
            
            # Loop untuk setiap dosen
            for idx, nama_dosen in enumerate(dosen_list, 1):
                print(f"\n[{idx}/{len(dosen_list)}] Memproses: {nama_dosen}")
                
                publications = self.scrape_dosen_publications(nama_dosen)
                all_publications.extend(publications)
                
                # Jeda antar dosen
                time.sleep(2)
        
        finally:
            # Pastikan driver ditutup
            if self.driver:
                self.driver.quit()
        
        # Konversi ke DataFrame
        df = pd.DataFrame(all_publications)

        # Jika ada data Cited_By_Per_Year, expand menjadi kolom terpisah
        if 'Cited_By_Per_Year' in df.columns:
            # determine years to output
            if self.years_to_collect:
                years_out = sorted(self.years_to_collect)
            else:
                # union of all years present
                years_union = set()
                for m in df['Cited_By_Per_Year'].dropna().tolist():
                    if isinstance(m, dict):
                        years_union.update(m.keys())
                years_out = sorted(years_union)

            # create columns like 2025_cited_by
            for y in years_out:
                col = f"{y}_cited_by"
                df[col] = df['Cited_By_Per_Year'].apply(lambda m, y=y: int(m.get(y, 0)) if isinstance(m, dict) else 0)

        return df
