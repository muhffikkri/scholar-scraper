# Panduan Setup Google Apps Script untuk Upload Data

## 📋 Langkah-langkah Setup

### 1. Buat Project Apps Script

1. Buka browser dan akses https://script.google.com
2. Klik tombol **"+ New project"**
3. Project baru akan terbuka dengan nama "Untitled project"
4. Klik "Untitled project" untuk memberi nama, misal: "Scholar Scraper API"

### 2. Copy Code Apps Script

1. Hapus code default yang ada
2. Buka file `apps-script-web-app.gs` di folder proyek ini
3. Copy seluruh isi file
4. Paste ke editor Apps Script
5. Save project (Ctrl+S atau File > Save)

### 3. Deploy sebagai Web App

1. Klik **Deploy** (di pojok kanan atas) > **New deployment**
2. Klik icon **gear/settings** di sebelah "Select type"
3. Pilih **"Web app"**
4. Isi konfigurasi:
   - **Description**: "Scholar Scraper API v1"
   - **Execute as**: **Me** (email Anda)
   - **Who has access**: **Anyone**
5. Klik **Deploy**

### 4. Authorize Aplikasi (Pertama Kali)

1. Akan muncul pop-up "Authorization required"
2. Klik **Authorize access**
3. Pilih account Google Anda
4. Klik **Advanced** (di bawah warning)
5. Klik **Go to [Project Name] (unsafe)**
6. Klik **Allow**

### 5. Copy Web App URL

Setelah deployment berhasil:

1. Akan muncul dialog dengan **Web app URL**
2. Format URL: `https://script.google.com/macros/s/AKfycby.../exec`
3. **Copy URL ini** - akan digunakan di aplikasi desktop
4. Simpan URL ini di tempat aman

## 🔧 Cara Menggunakan di Aplikasi

### Di Tab "Upload ke Google Sheets":

1. **Web App URL**: Paste URL yang sudah dicopy

   ```
   https://script.google.com/macros/s/AKfycby.../exec
   ```

2. **URL Google Spreadsheet**: Copy dari browser

   ```
   https://docs.google.com/spreadsheets/d/1ABC123XYZ456/edit
   ```

3. **Nama Sheet**: Nama sheet yang akan ditulis

   ```
   Publikasi 2024
   ```

4. Klik **Transfer Data ke Sheets**

## 🧪 Testing Apps Script

Untuk memastikan Apps Script bekerja:

1. Di Apps Script editor, pilih function `testDoPost`
2. Edit `YOUR_SPREADSHEET_ID` dengan ID spreadsheet test Anda
3. Klik **Run** (▶️)
4. Lihat hasil di **Execution log** (View > Logs)

## 🔐 Keamanan

- **Execute as: Me** = Script berjalan dengan permission Anda
- **Who has access: Anyone** = Siapa saja bisa memanggil API (tanpa auth)
- Script hanya bisa menulis ke spreadsheet yang Anda punya akses
- Tidak ada data sensitif yang disimpan

## 🔄 Update Apps Script

Jika ada perubahan code:

1. Edit code di Apps Script editor
2. Save (Ctrl+S)
3. **Deploy** > **Manage deployments**
4. Klik icon **pencil/edit** di deployment aktif
5. Ubah **Version** ke "New version"
6. Klik **Deploy**
7. **Web App URL tetap sama**, tidak perlu update di aplikasi

## ❓ Troubleshooting

### ⚠️ Error: "403 Forbidden" atau "403 Client Error"

**Penyebab Utama:**

- Apps Script deployment **tidak diset dengan permission yang benar**
- "Who has access" tidak diset ke "Anyone"

**Solusi Lengkap:**

1. **Buka Apps Script:**

   - Pergi ke https://script.google.com
   - Buka project Anda

2. **Manage Deployments:**

   - Klik **Deploy** (pojok kanan atas)
   - Klik **Manage deployments**

3. **Edit Deployment:**

   - Klik icon **pensil (edit)** di deployment yang aktif
   - Atau hapus deployment lama dan buat baru

4. **Set Permission dengan Benar:**

   ```
   Execute as: Me (your-email@gmail.com)
   Who has access: Anyone  ← PENTING! Harus "Anyone"
   ```

5. **Deploy Ulang:**

   - Jika edit: Klik **Deploy**
   - Jika baru: Klik **New deployment**

6. **Copy URL Baru:**

   - Copy **Web app URL** yang baru
   - Format: `https://script.google.com/macros/s/AKfycby.../exec`

7. **Update .env File:**

   ```env
   APPS_SCRIPT_URL=https://script.google.com/macros/s/[URL_BARU]/exec
   ```

8. **Restart Aplikasi:**
   - Tutup aplikasi GUI
   - Jalankan lagi: `python run_gui.py`

**Catatan:**

- ✅ **"Anyone"** = Siapa saja bisa memanggil API (diperlukan untuk aplikasi desktop)
- ❌ **"Anyone with Google account"** = TIDAK akan bekerja dari aplikasi desktop
- ✅ Script tetap aman karena hanya bisa akses spreadsheet milik Anda

### Error: "Authorization required"

- Ulangi langkah authorize (langkah 4)
- Pastikan pilih account yang benar

### Error: "Permission denied"

- Pastikan account yang deploy punya akses Editor ke spreadsheet
- Buka spreadsheet > Share > Tambahkan email account yang deploy

### Error: "Spreadsheet not found"

- Periksa URL spreadsheet sudah benar
- Pastikan spreadsheet tidak dihapus
- Spreadsheet ID harus valid

### Upload lambat atau timeout

- Ukuran data terlalu besar (>1000 baris)
- Koneksi internet lambat
- Google API sedang sibuk (coba lagi nanti)

## 📚 Referensi

- [Apps Script Documentation](https://developers.google.com/apps-script)
- [Spreadsheet Service](https://developers.google.com/apps-script/reference/spreadsheet)
- [Web Apps Guide](https://developers.google.com/apps-script/guides/web)
