"""
Logging module for Google Scholar Scraper.
Mencatat semua aktivitas scraping termasuk success, failure, dan CAPTCHA errors.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd


class ScraperLogger:
    """
    Logger untuk mencatat proses scraping dengan detail lengkap.
    """
    
    def __init__(self, log_dir: str = "logging"):
        """
        Initialize logger.
        
        Args:
            log_dir: Base directory untuk menyimpan log files
        """
        self.base_log_dir = log_dir
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = None
        self.end_time = None
        
        # Create session-specific folder
        self.log_dir = os.path.join(self.base_log_dir, f"session_{self.session_id}")
        
        # Data tracking
        self.dosen_list = []
        self.success_list = []
        self.failed_list = []
        self.captcha_list = []
        self.details = []
        
        # Ensure session log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
    def start_session(self, dosen_names: List[str]):
        """
        Memulai session logging.
        
        Args:
            dosen_names: List nama dosen yang akan di-scrape
        """
        self.start_time = datetime.now()
        self.dosen_list = dosen_names.copy()
        
        print(f"\n{'='*60}")
        print(f"LOGGING SESSION STARTED")
        print(f"{'='*60}")
        print(f"Session ID: {self.session_id}")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Dosen: {len(dosen_names)}")
        print(f"Log Directory: {self.log_dir}")
        print(f"{'='*60}\n")
        
    def log_success(self, nama_dosen: str, publications_count: int, detail_msg: str = ""):
        """
        Log scraping yang berhasil.
        
        Args:
            nama_dosen: Nama dosen yang berhasil di-scrape
            publications_count: Jumlah publikasi yang berhasil di-scrape
            detail_msg: Pesan detail tambahan
        """
        self.success_list.append(nama_dosen)
        self.details.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'nama_dosen': nama_dosen,
            'status': 'SUCCESS',
            'publications_count': publications_count,
            'detail': detail_msg
        })
        print(f"✅ SUCCESS: {nama_dosen} ({publications_count} publikasi)")
        
    def log_failure(self, nama_dosen: str, error_msg: str, error_type: str = "GENERAL_ERROR"):
        """
        Log scraping yang gagal.
        
        Args:
            nama_dosen: Nama dosen yang gagal di-scrape
            error_msg: Pesan error
            error_type: Tipe error (CAPTCHA, TIMEOUT, NOT_FOUND, etc.)
        """
        self.failed_list.append(nama_dosen)
        
        if error_type == "CAPTCHA":
            self.captcha_list.append(nama_dosen)
            
        self.details.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'nama_dosen': nama_dosen,
            'status': 'FAILED',
            'error_type': error_type,
            'error_message': error_msg,
            'publications_count': 0
        })
        
        icon = "🤖" if error_type == "CAPTCHA" else "❌"
        print(f"{icon} {error_type}: {nama_dosen} - {error_msg}")
        
    def end_session(self):
        """
        Mengakhiri session dan menyimpan semua log.
        """
        self.end_time = datetime.now()
        duration = self.end_time - self.start_time
        
        print(f"\n{'='*60}")
        print(f"LOGGING SESSION ENDED")
        print(f"{'='*60}")
        print(f"End Time: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {duration}")
        print(f"{'='*60}\n")
        
        # Save all logs
        self._save_summary()
        self._save_detailed_log()
        self._save_failed_names()
        self._save_captcha_names()
        
        return {
            'session_id': self.session_id,
            'log_dir': self.log_dir,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': str(duration),
            'total': len(self.dosen_list),
            'success': len(self.success_list),
            'failed': len(self.failed_list),
            'captcha': len(self.captcha_list)
        }
        
    def _save_summary(self):
        """
        Menyimpan summary log dalam format JSON.
        """
        summary = {
            'session_info': {
                'session_id': self.session_id,
                'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'duration_seconds': (self.end_time - self.start_time).total_seconds()
            },
            'statistics': {
                'total_dosen': len(self.dosen_list),
                'success_count': len(self.success_list),
                'failed_count': len(self.failed_list),
                'captcha_count': len(self.captcha_list),
                'success_rate': f"{(len(self.success_list) / len(self.dosen_list) * 100):.2f}%" if self.dosen_list else "0%"
            },
            'dosen_processed': self.dosen_list,
            'success_list': self.success_list,
            'failed_list': self.failed_list,
            'captcha_list': self.captcha_list
        }
        
        filename = os.path.join(self.log_dir, f"summary_{self.session_id}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Summary saved: {filename}")
        
    def _save_detailed_log(self):
        """
        Menyimpan detailed log dalam format CSV.
        """
        if not self.details:
            return
            
        df = pd.DataFrame(self.details)
        filename = os.path.join(self.log_dir, f"detailed_log_{self.session_id}.csv")
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"📋 Detailed log saved: {filename}")
        
    def _save_failed_names(self):
        """
        Menyimpan daftar nama yang gagal di-scrape.
        """
        if not self.failed_list:
            print("✅ No failed names to save")
            return
            
        filename = os.path.join(self.log_dir, f"failed_names_{self.session_id}.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"FAILED SCRAPING - Session: {self.session_id}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Failed: {len(self.failed_list)}\n")
            f.write("="*60 + "\n\n")
            
            for idx, nama in enumerate(self.failed_list, 1):
                # Find detail for this name
                detail = next((d for d in self.details if d['nama_dosen'] == nama and d['status'] == 'FAILED'), None)
                error_type = detail.get('error_type', 'UNKNOWN') if detail else 'UNKNOWN'
                error_msg = detail.get('error_message', '') if detail else ''
                
                f.write(f"{idx}. {nama}\n")
                f.write(f"   Error Type: {error_type}\n")
                f.write(f"   Error Message: {error_msg}\n\n")
        
        print(f"❌ Failed names saved: {filename}")
        
    def _save_captcha_names(self):
        """
        Menyimpan daftar nama yang terkena CAPTCHA (subset dari failed).
        """
        if not self.captcha_list:
            print("✅ No CAPTCHA blocks encountered")
            return
            
        filename = os.path.join(self.log_dir, f"captcha_blocked_{self.session_id}.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"CAPTCHA BLOCKED - Session: {self.session_id}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total CAPTCHA Blocks: {len(self.captcha_list)}\n")
            f.write("="*60 + "\n\n")
            f.write("REKOMENDASI:\n")
            f.write("1. Jalankan ulang scraping untuk nama-nama ini dengan delay lebih lama\n")
            f.write("2. Gunakan mode non-headless untuk manual CAPTCHA solving\n")
            f.write("3. Pertimbangkan menggunakan proxy atau VPN\n")
            f.write("="*60 + "\n\n")
            
            for idx, nama in enumerate(self.captcha_list, 1):
                f.write(f"{idx}. {nama}\n")
        
        print(f"🤖 CAPTCHA blocked names saved: {filename}")
        
    def get_summary(self) -> Dict:
        """
        Get current session summary.
        
        Returns:
            Dictionary dengan summary data
        """
        return {
            'total': len(self.dosen_list),
            'success': len(self.success_list),
            'failed': len(self.failed_list),
            'captcha': len(self.captcha_list),
            'pending': len(self.dosen_list) - len(self.success_list) - len(self.failed_list)
        }


def get_all_sessions(log_dir: str = "logging") -> List[Dict]:
    """
    Mendapatkan semua session log yang tersedia.
    
    Args:
        log_dir: Base directory logging
        
    Returns:
        List of session info sorted by date (newest first)
    """
    sessions = []
    
    if not os.path.exists(log_dir):
        return sessions
    
    # Scan semua folder session_*
    for item in os.listdir(log_dir):
        item_path = os.path.join(log_dir, item)
        
        # Skip jika bukan directory atau bukan session folder
        if not os.path.isdir(item_path) or not item.startswith("session_"):
            continue
        
        # Cari file summary
        summary_file = None
        for file in os.listdir(item_path):
            if file.startswith("summary_") and file.endswith(".json"):
                summary_file = os.path.join(item_path, file)
                break
        
        if summary_file and os.path.exists(summary_file):
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['log_folder'] = item_path
                    sessions.append(data)
            except Exception as e:
                print(f"Error reading {summary_file}: {e}")
    
    # Sort by start_time (newest first)
    sessions.sort(key=lambda x: x.get('session_info', {}).get('start_time', ''), reverse=True)
    
    return sessions
