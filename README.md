# 📚 Scribd Batch Downloader

Suka males kalau harus download atau arsip dokumen dari Scribd satu-satu? Tool ini dibikin buat otomatisasi proses itu. Tinggal masukin list ID dokumennya, klik Start, dan biarin scriptnya jalan sendiri sampai diconvert jadi PDF utuh ☕.

UI-nya sengaja di-custom pakai dark theme biar lebih modern dan nggak kaku, plus ada fitur riwayat unduhan (history) buat nge-track dokumen apa aja yang udah pernah didownload sebelumnya.

🛡️ **100% Berjalan di Local (Aman!)**
Semua proses download dan convert ke PDF terjadi langsung di komputer/laptop kamu. Nggak ada data, ID dokumen, atau file yang dikirim ke server luar atau pihak ketiga. Privasi aman terkendali! 🔒

## ✨ Fitur

- **🚀 Batch Download**: Masukin ID dokumen sebanyak yang dimau (pisahkan pakai enter), tinggalin ngopi, biarin script yang kerja.
- **📄 Auto-compile ke PDF**: Gambar per halaman yang didownload langsung digabung jadi satu file PDF beresolusi tinggi.
- **🕒 Smart History**: Panel riwayat di bagian bawah UI. Lengkap sama thumbnail cover dokumen dan info waktu (misal: "5 menit yang lalu"). Walau aplikasi ditutup lalu dibuka lagi besoknya, history ini bakal tetap ada.
- **🧹 Auto-Cleanup**: Nggak bikin penuh storage atau nyampah. Folder `temp` buat nyimpen file mentahan bakal otomatis dihapus begitu PDF selesai dibuat.
- **📂 Show in Folder**: Klik tulisan di history buat langsung buka lokasi file PDF-nya di Windows Explorer.

## ⚙️ Cara Instalasi

Pastikan di PC kamu udah terpasang **Python 3.8** (atau yang lebih baru) dan **Google Chrome** (dibutuhkan Selenium buat bypass page awal).

1. **Download source code** ini (bisa via `git clone` atau download ZIP lalu ekstrak ke folder pilihanmu).
2. Buka terminal atau Command Prompt (CMD), lalu arahin ke folder tempat kamu nyimpen file ini.
3. Install library pendukung dengan menjalankan perintah berikut:
   ```bash
   pip install requests pillow selenium
4. Jalankan file `main.py` dan Download semua file yang kalian butuhkan dalam satu kali klik.