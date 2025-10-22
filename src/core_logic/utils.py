"""
Utility functions for Google Scholar scraper.
Berisi fungsi-fungsi bantuan seperti pembersihan nama dosen.
"""

import re
from typing import List


def clean_dosen_name(full_name: str) -> str:
    """
    Membersihkan nama dosen dari gelar akademis.
    
    Args:
        full_name (str): Nama lengkap dosen dengan gelar akademis
        
    Returns:
        str: Nama dosen yang sudah dibersihkan dari gelar
        
    Examples:
        >>> clean_dosen_name("Dr. Ir. Bambang Riyanto, M.Kom., Ph.D")
        "Bambang Riyanto"
        >>> clean_dosen_name("Prof. Siti Nurhaliza, S.T., M.T.")
        "Siti Nurhaliza"
        >>> clean_dosen_name("Drs. Ahmad Dahlan, M.Si.")
        "Ahmad Dahlan"
    """
    if not full_name or not isinstance(full_name, str):
        return ""
    
    # Daftar gelar akademis yang umum (dengan word boundary yang lebih ketat)
    # Gelar depan harus diikuti titik dan spasi atau titik di akhir kata
    gelar_depan = [
        r'\bProf\.?\s+',      # Prof. atau Prof diikuti spasi
        r'\bDr\.?\s+',        # Dr. atau Dr diikuti spasi
        r'\bIr\.?\s+',        # Ir. atau Ir diikuti spasi
        r'\bDrs\.?\s+',       # Drs. atau Drs diikuti spasi
        r'\bDra\.?\s+',       # Dra. atau Dra diikuti spasi
        r'\bHC\.?\s+',        # HC. atau HC diikuti spasi
        r'\bH\.?\s+',         # H. atau H diikuti spasi (harus setelah HC untuk menghindari konflik)
        r'\bHj\.?\s+',        # Hj. atau Hj diikuti spasi
    ]
    
    # Gelar belakang dengan koma opsional
    gelar_belakang = [
        r',?\s*S\.T\.?',      # S.T. atau S.T
        r',?\s*S\.Si\.?',     # S.Si. atau S.Si
        r',?\s*S\.Kom\.?',    # S.Kom. atau S.Kom
        r',?\s*S\.Pd\.?',     # S.Pd. atau S.Pd
        r',?\s*S\.E\.?',      # S.E. atau S.E
        r',?\s*S\.H\.?',      # S.H. atau S.H
        r',?\s*S\.Sos\.?',    # S.Sos. atau S.Sos
        r',?\s*M\.T\.?',      # M.T. atau M.T
        r',?\s*M\.Si\.?',     # M.Si. atau M.Si
        r',?\s*M\.Kom\.?',    # M.Kom. atau M.Kom
        r',?\s*M\.Pd\.?',     # M.Pd. atau M.Pd
        r',?\s*M\.Sc\.?',     # M.Sc. atau M.Sc
        r',?\s*M\.A\.?',      # M.A. atau M.A
        r',?\s*M\.M\.?',      # M.M. atau M.M
        r',?\s*M\.E\.?',      # M.E. atau M.E
        r',?\s*M\.H\.?',      # M.H. atau M.H
        r',?\s*M\.Sos\.?',    # M.Sos. atau M.Sos
        r',?\s*M\.Eng\.?',    # M.Eng. atau M.Eng
        r',?\s*MBA\.?',       # MBA. atau MBA
        r',?\s*Ph\.?D\.?',    # Ph.D. atau PhD atau Ph.D
        r',?\s*PhD',          # PhD
        r',?\s*Dr\.?',        # Dr. di belakang
    ]
    
    # Hapus gelar depan
    cleaned_name = full_name
    for gelar in gelar_depan:
        cleaned_name = re.sub(gelar, '', cleaned_name, flags=re.IGNORECASE)
    
    # Hapus gelar belakang
    for gelar in gelar_belakang:
        cleaned_name = re.sub(gelar, '', cleaned_name, flags=re.IGNORECASE)
    
    # Hapus koma yang tersisa dan spasi berlebih
    cleaned_name = re.sub(r'\s*,\s*', ' ', cleaned_name)
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
    cleaned_name = cleaned_name.strip()
    
    # Hapus karakter khusus yang tidak perlu (koma atau titik koma di akhir)
    cleaned_name = re.sub(r'[,;.]+$', '', cleaned_name)
    
    return cleaned_name.strip()


def sanitize_filename(filename: str) -> str:
    """
    Membersihkan nama file dari karakter yang tidak valid.
    
    Args:
        filename (str): Nama file yang akan dibersihkan
        
    Returns:
        str: Nama file yang sudah dibersihkan
    """
    # Karakter yang tidak diperbolehkan di Windows
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    sanitized = re.sub(r'\s+', '_', sanitized)
    return sanitized.strip('_')


def extract_spreadsheet_id_from_url(url: str) -> str:
    """
    Mengekstrak Spreadsheet ID dari URL Google Sheets.
    
    Args:
        url (str): URL Google Spreadsheet
        
    Returns:
        str: Spreadsheet ID atau empty string jika tidak valid
        
    Examples:
        >>> extract_spreadsheet_id_from_url("https://docs.google.com/spreadsheets/d/1ABC123XYZ/edit")
        "1ABC123XYZ"
    """
    # Pattern untuk Google Sheets URL
    # Format: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/...
    pattern = r'/spreadsheets/d/([a-zA-Z0-9-_]+)'
    
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    
    return ""


def parse_publication_info(info_string: str) -> dict:
    """
    Melakukan parsing cerdas pada string informasi publikasi.
    Memecah venue menjadi komponen detail berdasarkan pola:
    - Jurnal: Nama Jurnal Volume (Terbitan), Halaman
    - Buku/Lainnya: Nama Penerbit
    
    Args:
        info_string (str): String informasi publikasi dari Google Scholar
        
    Returns:
        dict: Dictionary berisi komponen-komponen publikasi
        
    Examples:
        >>> parse_publication_info("IEEE Transactions on AI 15 (3), 45-60")
        {'journal_name': 'IEEE Transactions on AI', 'volume': '15', 'issue': '3', 'pages': '45-60', 'publisher': '', 'year': ''}
        
        >>> parse_publication_info("Springer Nature, 2020")
        {'journal_name': '', 'volume': '', 'issue': '', 'pages': '', 'publisher': 'Springer Nature', 'year': '2020'}
    """
    result = {
        'journal_name': '',
        'volume': '',
        'issue': '',
        'pages': '',
        'publisher': '',
        'year': ''
    }
    
    if not info_string:
        return result
    
    # Ekstrak tahun (4 digit)
    year_match = re.search(r'\b(19|20)\d{2}\b', info_string)
    if year_match:
        result['year'] = year_match.group(0)
        # Hapus tahun dari string untuk memudahkan parsing selanjutnya
        info_string = info_string.replace(year_match.group(0), '').strip()
    
    # Hapus koma trailing atau leading
    info_string = info_string.strip(',').strip()
    
    # Pola 1: Artikel Jurnal dengan Volume dan Issue
    # Contoh: "Journal Name 15 (3), 45-60" atau "Journal Name 15, 45-60"
    journal_pattern = r'^(.+?)\s+(\d+)\s*(?:\((\d+)\))?\s*,\s*(.+)$'
    match = re.match(journal_pattern, info_string)
    
    if match:
        # Ini adalah artikel jurnal
        result['journal_name'] = match.group(1).strip()
        result['volume'] = match.group(2).strip()
        result['issue'] = match.group(3).strip() if match.group(3) else ''
        result['pages'] = match.group(4).strip()
        return result
    
    # Pola 2: Artikel Jurnal tanpa halaman eksplisit
    # Contoh: "Journal Name 15 (3)" atau "Journal Name 15"
    journal_pattern_no_pages = r'^(.+?)\s+(\d+)\s*(?:\((\d+)\))?$'
    match = re.match(journal_pattern_no_pages, info_string)
    
    if match:
        result['journal_name'] = match.group(1).strip()
        result['volume'] = match.group(2).strip()
        result['issue'] = match.group(3).strip() if match.group(3) else ''
        return result
    
    # Pola 3: Halaman tanpa volume (jarang tapi mungkin terjadi)
    # Contoh: "Journal Name, 45-60"
    journal_pattern_pages_only = r'^(.+?),\s*(\d+[-–]\d+)$'
    match = re.match(journal_pattern_pages_only, info_string)
    
    if match:
        result['journal_name'] = match.group(1).strip()
        result['pages'] = match.group(2).strip()
        return result
    
    # Jika tidak cocok dengan pola jurnal, anggap sebagai publisher/buku
    # Bisa berupa penerbit, konferensi, atau informasi lainnya
    if info_string:
        result['publisher'] = info_string.strip()
    
    return result


def parse_venue_from_detail(detail_dict: dict) -> dict:
    """
    Memparse venue dari dictionary detail publikasi yang di-scrape dari halaman detail.
    
    Args:
        detail_dict (dict): Dictionary berisi detail publikasi dari halaman detail
        
    Returns:
        dict: Dictionary berisi komponen venue yang sudah dipecah
    """
    result = {
        'journal_name': '',
        'volume': '',
        'issue': '',
        'pages': '',
        'publisher': '',
        'year': ''
    }
    
    # Ambil informasi dari berbagai field yang mungkin ada
    journal = detail_dict.get('Jurnal', detail_dict.get('Journal', ''))
    conference = detail_dict.get('Konferensi', detail_dict.get('Conference', ''))
    book_title = detail_dict.get('Buku', detail_dict.get('Book', ''))
    publisher = detail_dict.get('Penerbit', detail_dict.get('Publisher', ''))
    volume = detail_dict.get('Volume', '')
    issue = detail_dict.get('Terbitan', detail_dict.get('Issue', ''))
    pages = detail_dict.get('Halaman', detail_dict.get('Pages', ''))
    year = detail_dict.get('Tanggal publikasi', detail_dict.get('Publication date', ''))
    
    # Prioritaskan jurnal, lalu konferensi, lalu buku
    if journal:
        result['journal_name'] = journal
    elif conference:
        result['journal_name'] = conference
    elif book_title:
        result['journal_name'] = book_title
    
    # Isi volume, issue, pages jika ada
    if volume:
        result['volume'] = volume
    if issue:
        result['issue'] = issue
    if pages:
        result['pages'] = pages
    
    # Isi publisher
    if publisher:
        result['publisher'] = publisher
    
    # Ekstrak tahun dari tanggal publikasi
    if year:
        year_match = re.search(r'\b(19|20)\d{2}\b', year)
        if year_match:
            result['year'] = year_match.group(0)
        else:
            result['year'] = year
    
    return result
