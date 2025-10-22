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
        >>> clean_dosen_name("Dr. Ir. John Doe, M.Kom., Ph.D")
        "John Doe"
        >>> clean_dosen_name("Prof. Jane Smith, S.T., M.T.")
        "Jane Smith"
    """
    if not full_name or not isinstance(full_name, str):
        return ""
    
    # Daftar gelar akademis yang umum
    gelar_depan = [
        r'\bDr\.\s*', r'\bIr\.\s*', r'\bProf\.\s*', r'\bDrs\.\s*',
        r'\bDra\.\s*', r'\bH\.\s*', r'\bHj\.\s*', r'\bHC\.\s*'
    ]
    
    gelar_belakang = [
        r',?\s*S\.T\.?', r',?\s*S\.Si\.?', r',?\s*S\.Kom\.?', r',?\s*S\.Pd\.?',
        r',?\s*M\.T\.?', r',?\s*M\.Si\.?', r',?\s*M\.Kom\.?', r',?\s*M\.Pd\.?',
        r',?\s*M\.Sc\.?', r',?\s*M\.A\.?', r',?\s*M\.M\.?', r',?\s*MBA\.?',
        r',?\s*Ph\.?D\.?', r',?\s*Ph\.D', r',?\s*PhD', r',?\s*M\.Eng\.?',
        r',?\s*Dr\.?', r',?\s*S\.E\.?', r',?\s*M\.E\.?', r',?\s*S\.H\.?',
        r',?\s*M\.H\.?', r',?\s*S\.Sos\.?', r',?\s*M\.Sos\.?'
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
    
    # Hapus karakter khusus yang tidak perlu
    cleaned_name = re.sub(r'[,;]$', '', cleaned_name)
    
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
