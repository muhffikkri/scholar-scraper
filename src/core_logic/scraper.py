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
        
        Args:
            detail_url (str): URL halaman detail artikel
            
        Returns:
            Dict[str, str]: Dictionary berisi detail publikasi
        """
        try:
            self.driver.get(detail_url)
            time.sleep(1.5)
            
            # Tunggu tabel detail muncul
            wait = WebDriverWait(self.driver, self.wait_time)
            table = wait.until(
                EC.presence_of_element_located((By.ID, "gsc_oci_table"))
            )
            
            # Parse dengan BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            detail_table = soup.find('table', {'id': 'gsc_oci_table'})
            
            details = {}
            if detail_table:
                rows = detail_table.find_all('div', class_='gs_scl')
                for row in rows:
                    field = row.find('div', class_='gsc_oci_field')
                    value = row.find('div', class_='gsc_oci_value')
                    
                    if field and value:
                        field_text = field.get_text(strip=True)
                        value_text = value.get_text(strip=True)
                        details[field_text] = value_text
            
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
                'Venue': venue_info,
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
            
            # Load semua publikasi
            self._load_all_publications()
            
            # Dapatkan semua baris publikasi
            pub_rows = self.driver.find_elements(By.CLASS_NAME, "gsc_a_tr")
            
            for idx, row in enumerate(pub_rows):
                try:
                    pub_data = self._parse_publication_row(row, scraped_titles)
                    
                    if not pub_data:
                        continue
                    
                    # Jika data tidak lengkap, ambil detail
                    if pub_data['Is_Incomplete'] and pub_data['Detail_Link']:
                        print(f"  Mengambil detail untuk: {pub_data['Judul'][:50]}...")
                        
                        # Ambil detail
                        details = self._scrape_publication_detail(pub_data['Detail_Link'])
                        
                        # Update data dengan detail
                        if details:
                            pub_data['Venue'] = details.get('Jurnal', details.get('Konferensi', pub_data['Venue']))
                            pub_data['Tahun'] = details.get('Tanggal publikasi', pub_data['Tahun'])
                            pub_data['Penulis'] = details.get('Penulis', pub_data['Penulis'])
                            pub_data['Publisher'] = details.get('Penerbit', '')
                        
                        # Kembali ke halaman profil
                        self.driver.get(profile_url)
                        time.sleep(1)
                        
                        # Muat ulang semua publikasi
                        self._load_all_publications()
                        
                        # Refresh list baris publikasi
                        pub_rows = self.driver.find_elements(By.CLASS_NAME, "gsc_a_tr")
                    
                    # Tambahkan nama dosen
                    pub_data['Nama Dosen'] = nama_dosen
                    
                    # Hapus flag is_incomplete
                    del pub_data['Is_Incomplete']
                    del pub_data['Detail_Link']
                    
                    # Tambahkan ke hasil
                    publications.append(pub_data)
                    scraped_titles.add(pub_data['Judul'])
                    
                    print(f"  [{idx+1}/{len(pub_rows)}] {pub_data['Judul'][:60]}...")
                    
                except StaleElementReferenceException:
                    # Element sudah tidak valid, skip
                    continue
                except Exception as e:
                    print(f"  Error pada publikasi {idx+1}: {e}")
                    continue
            
            print(f"Selesai: {nama_dosen} - {len(publications)} publikasi")
            
        except Exception as e:
            print(f"Error saat scraping {nama_dosen}: {e}")
        
        return publications
    
    def run_scraper(self, dosen_list: List[str]) -> pd.DataFrame:
        """
        Menjalankan scraper untuk list nama dosen.
        
        Args:
            dosen_list (List[str]): List nama dosen yang sudah dibersihkan
            
        Returns:
            pd.DataFrame: DataFrame berisi semua publikasi
        """
        all_publications = []
        
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
        
        return df
