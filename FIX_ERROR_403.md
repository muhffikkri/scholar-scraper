# 🚨 Quick Fix: Error 403 Forbidden

## ❌ Error yang Muncul:

```
ERROR: Gagal menghubungi server - 403 Client Error: Forbidden for url: https://...
```

atau

```
403 Forbidden
```

---

## ✅ Solusi Cepat (5 Menit):

### Langkah 1: Buka Apps Script

```
https://script.google.com
```

### Langkah 2: Manage Deployments

1. Pilih project Anda
2. Klik **Deploy** (pojok kanan atas)
3. Klik **Manage deployments**

### Langkah 3: Edit Permission

1. Klik icon **pensil** (edit) di deployment aktif
2. **PENTING**: Set permission:
   ```
   Execute as: Me (email@gmail.com)
   Who has access: Anyone  ← Ubah ke "Anyone"
   ```
3. Klik **Deploy**

### Langkah 4: Copy URL Baru

```
Web app URL: https://script.google.com/macros/s/AKfycby.../exec
```

### Langkah 5: Update .env

Buka file `.env` di root project:

```env
APPS_SCRIPT_URL=https://script.google.com/macros/s/[URL_BARU]/exec
```

### Langkah 6: Restart Aplikasi

```powershell
python run_gui.py
```

---

## 🔍 Penjelasan Masalah:

**Penyebab:**

- Apps Script deployment memiliki permission "Anyone with Google account"
- Aplikasi desktop tidak bisa authenticate sebagai Google user
- Server menolak request dengan error 403 Forbidden

**Solusi:**

- Ubah permission ke **"Anyone"** (tanpa authentication)
- Apps Script tetap aman karena hanya akses spreadsheet Anda

---

## ⚡ Alternative: Buat Deployment Baru

Jika edit tidak berhasil, buat deployment baru:

1. **Delete Deployment Lama:**

   - Deploy → Manage deployments
   - Klik icon **trash** di deployment lama

2. **Buat Deployment Baru:**

   - Deploy → New deployment
   - Select type: **Web app**
   - Execute as: **Me**
   - Who has access: **Anyone** ← PENTING!
   - Deploy

3. **Copy URL Baru & Update .env**

---

## 📋 Checklist

Pastikan semua ini sudah benar:

- [ ] Apps Script code sudah dicopy dengan benar
- [ ] Deployment type: **Web app**
- [ ] Execute as: **Me** (bukan "User accessing the web app")
- [ ] Who has access: **Anyone** (bukan "Anyone with Google account")
- [ ] URL sudah dicopy dengan lengkap (termasuk `/exec` di akhir)
- [ ] .env file sudah diupdate dengan URL baru
- [ ] Aplikasi sudah direstart

---

## 🆘 Masih Error?

### Cek URL Format:

**✅ Benar:**

```
https://script.google.com/macros/s/AKfycbyXXXXXXXXXXXXXXXXXXXXXXXX/exec
```

**❌ Salah:**

```
https://script.google.com/macros/s/YOUR_SCRIPT_ID_HERE/exec
https://script.google.com/home/projects/xxxxx  (ini URL editor, bukan web app)
https://script.google.com/macros/s/AKfycby.../dev  (ini dev mode, bukan production)
```

### Test Manual:

Test Apps Script dengan browser:

1. Copy URL dari .env
2. Paste di browser
3. Tekan Enter

**Expected Response:**

```json
{ "status": "error", "message": "..." }
```

**Jika 403:**

- Permission masih salah
- Ulangi langkah 1-6

**Jika JSON muncul:**

- Apps Script bekerja!
- Error mungkin di tempat lain

---

## 📖 Dokumentasi Lengkap:

- [APPS_SCRIPT_SETUP.md](APPS_SCRIPT_SETUP.md) - Setup lengkap
- [ENV_CONFIGURATION.md](ENV_CONFIGURATION.md) - Konfigurasi .env
- [README.md](README.md) - Dokumentasi utama

---

## 💡 Tips Debugging:

### 1. Cek Log Upload di GUI:

```
[14:30:20] 🚀 Mengirim data ke Google Sheets...
[14:30:21] ❌ ERROR: Gagal menghubungi server - 403 Client Error
```

### 2. Cek .env File:

```powershell
cat .env | Select-String "APPS_SCRIPT_URL"
```

### 3. Cek Apps Script Log:

- Apps Script Editor → View → Executions
- Lihat apakah ada request masuk

---

**Setelah mengikuti langkah di atas, error 403 seharusnya sudah teratasi!** ✅
