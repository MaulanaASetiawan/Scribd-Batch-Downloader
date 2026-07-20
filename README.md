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

## 🚀 Cara Menjalankan
1. Di terminal/CMD yang sama, jalankan aplikasinya pakai perintah: `python main.py`
2. Cari ID dokumen dari URL Scribd yang mau didownload. (Contoh: dari link https://www.scribd.com/document/123456789/Judul-Buku, ID-nya adalah 123456789).
3. Paste ID tersebut ke kotak input di sebelah kiri UI. Kalau mau download banyak sekaligus, enter saja ke bawah untuk ID selanjutnya.
4. Klik tombol Start.
5. ⚠️ Catatan Penting: Saat baru mulai, browser Chrome akan terbuka sebentar di latar belakang. Kalau Scribd memunculkan halaman Captcha, tolong selesaikan secara manual dulu di browser tersebut (ada waktu tunggu 15 detik). Setelah lolos, script akan otomatis lanjut kerja.
6. Tunggu progress bar selesai. PDF akan otomatis tersimpan di folder `Scribd_Downloads.`

## 📁 Struktur Folder
Biar manajemen filenya rapi, script ini bakal otomatis bikin folder berikut di lokasi yang sama dengan file main.py:
- `Scribd_Downloads/` → Folder utama tempat file PDF ngumpul.
- `Scribd_Downloads/.thumbnails/` → Folder tersembunyi (hidden) untuk nyimpen cache cover buku.
- `temp_images/` → Folder transit. Cuma muncul pas lagi proses download, habis itu otomatis hilang.

## ⚖️ Disclaimer
Script ini ditulis murni untuk tujuan pembelajaran (edukasi) dan mempermudah personal archiving (arsip pribadi). Segala bentuk penyalahgunaan, distribusi ulang, atau pelanggaran hak cipta dari dokumen yang diunduh sepenuhnya berada di luar tanggung jawab developer. Use it responsibly! ✌️