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
    
    Args:
        info_string (str): String informasi publikasi dari Google Scholar
        
    Returns:
        dict: Dictionary berisi komponen-komponen publikasi
        
    Examples:
        >>> parse_publication_info("Journal of AI, 2020")
        {'venue': 'Journal of AI', 'year': '2020'}
    """
    result = {
        'venue': '',
        'year': '',
        'volume': '',
        'pages': '',
        'publisher': ''
    }
    
    if not info_string:
        return result
    
    # Ekstrak tahun (4 digit)
    year_match = re.search(r'\b(19|20)\d{2}\b', info_string)
    if year_match:
        result['year'] = year_match.group(0)
        # Hapus tahun dari string untuk memudahkan parsing selanjutnya
        info_string = info_string.replace(year_match.group(0), '').strip()
    
    # Split berdasarkan koma
    parts = [p.strip() for p in info_string.split(',') if p.strip()]
    
    if parts:
        result['venue'] = parts[0]
        
        # Coba identifikasi publisher atau informasi tambahan
        if len(parts) > 1:
            result['publisher'] = ', '.join(parts[1:])
    
    return result
