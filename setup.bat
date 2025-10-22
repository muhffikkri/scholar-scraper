@echo off
REM ============================================================
REM Setup Script untuk Google Scholar Scraper
REM ============================================================
REM Script ini akan:
REM 1. Membuat virtual environment (venv)
REM 2. Mengaktifkan venv
REM 3. Menginstall semua dependencies
REM 4. Menjalankan aplikasi dalam mode GUI
REM ============================================================

echo ========================================
echo Google Scholar Scraper - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python tidak ditemukan!
    echo Silakan install Python 3.8+ dari https://python.org
    pause
    exit /b 1
)

echo [1/4] Memeriksa virtual environment...
if not exist "venv\" (
    echo        Virtual environment belum ada, membuat yang baru...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Gagal membuat virtual environment
        pause
        exit /b 1
    )
    echo        ✓ Virtual environment berhasil dibuat
) else (
    echo        ✓ Virtual environment sudah ada
)

echo.
echo [2/4] Mengaktifkan virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Gagal mengaktifkan virtual environment
    pause
    exit /b 1
)
echo        ✓ Virtual environment aktif

echo.
echo [3/4] Menginstall dependencies...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Gagal menginstall dependencies
    pause
    exit /b 1
)
echo        ✓ Dependencies terinstall

echo.
echo [4/4] Menjalankan aplikasi (mode GUI)...
echo ========================================
echo.

python main.py --gui

REM Deactivate venv setelah selesai
deactivate

echo.
echo ========================================
echo Setup selesai
echo ========================================
pause
