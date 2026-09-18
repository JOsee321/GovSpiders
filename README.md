# 🕷️ GovSpiders

**GovSpiders** adalah antarmuka baris perintah (CLI) berbasis Python yang dirancang khusus untuk memetakan, memindai, dan mendeteksi penyisipan halaman judi online (SEO poisoning/Defacement) pada infrastruktur domain institusi pemerintah (`.go.id`) dan pendidikan (`.ac.id`). Alat ini mengotomatisasi proses intelijen keamanan dengan efisien dan sangat akurat.

---

## 🚀 Fitur Utama

- **Subdomain Enumeration (crt.sh):** Secara otomatis mengumpulkan seluruh daftar subdomain yang valid dari target *root domain* menggunakan catatan sertifikat publik (SSL/TLS).
- **Concurrent Scanning (50 Threads):** Memindai hingga 50 URL secara bersamaan tanpa pemblokiran (*non-blocking*) menggunakan `ThreadPoolExecutor` untuk performa yang sangat cepat.
- **Regex Weighted Scoring Engine:** Sistem deteksi cerdas yang menggunakan `BeautifulSoup4` untuk menganalisis elemen DOM penting (`<title>`, `<meta>`, `<body>`) dan menilai berdasarkan ambang batas skor (threshold) guna meminimalisasi *false positive*. Dilengkapi juga deteksi *hidden injection* (injeksi `<iframe>` atau `<script>` tersembunyi).
- **Double-agent Cloaking Detection:** Strategi pengiriman *dual HTTP Request*! GovSpiders mampu mendeteksi teknik *cloaking* (manipulasi hasil perayapan Google) dengan memalsukan *headers* sebagai Googlebot, lalu otomatis memverifikasi ulang dengan *User-Agent* standar jika terindikasi terinfeksi.
- **Auto-Reporting (TXT & JSON):** Hasil pencarian otomatis dieskpor dalam format laporan teks dan format JSON yang komprehensif untuk rekam jejak forensik.

---

## ⚙️ Prasyarat & Instalasi

Pastikan Anda telah menginstal **Python 3.9+** di sistem Anda.

1. Clone repositori ini:
   ```bash
   git clone https://github.com/username/GovSpiders.git
   cd GovSpiders
   ```
   *(Catatan: Sesuaikan URL repository jika Anda memindahkannya ke git remote Anda).*

2. Instalasi semua pustaka dependensi yang dibutuhkan:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🛠️ Cara Penggunaan

Cukup jalankan *script* dengan *flag* domain `-d`. Anda juga bisa menentukan nama kustom untuk file pelaporan menggunakan `-o`.

Contoh menjalankan pemindaian:
```bash
python govspiders.py -d banjarbarukota.go.id -o hasil_audit.txt
```

**Penjelasan Argumen:**
* `-d` atau `--domain` *(Wajib)*: Masukkan nama *root domain* target.
* `-o` atau `--output` *(Opsional)*: Menentukan nama file keluaran khusus (Laporan `TXT` dan log forensik `JSON`). Jika diabaikan, ia akan menyimpannya menggunakan nama bawaan `govspiders_report.txt`.

---

## ⚠️ Disclaimer

**PERINGATAN HUKUM DAN ETIKA:** 
Alat **GovSpiders** ini dibuat murni dengan niat baik (*good faith*) dan ditujukan HANYA untuk tujuan audit keamanan proaktif, *compliance* internal, dan mitigasi insiden oleh Tim Insiden Respons Siber (CSIRT/CERT). Alat ini DILARANG KERAS digunakan untuk tindakan peretasan ofensif, memindai infrastruktur tanpa otorisasi tertulis, atau disalahgunakan dalam kegiatan siber ilegal lainnya. Pengembang tidak bertanggung jawab atas segala kerugian maupun konsekuensi hukum yang ditimbulkan dari penyalahgunaan alat ini.
