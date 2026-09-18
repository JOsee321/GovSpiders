# Product Requirements Document (PRD): GovSpiders

## 1. Ringkasan Eksekutif
**GovSpiders** adalah antarmuka baris perintah (CLI) berbasis Python yang dirancang khusus untuk memetakan, memindai, dan mendeteksi penyisipan halaman judi online (SEO poisoning/Defacement) pada infrastruktur domain institusi pemerintah (`.go.id`) dan pendidikan (`.ac.id`). Alat ini mengotomatisasi proses intelijen keamanan yang sebelumnya dilakukan secara manual via dorking.

## 2. Tujuan & Sasaran
*   **Kecepatan:** Memetakan dan memindai ratusan subdomain dalam hitungan menit menggunakan konkurensi (multithreading).
*   **Akurasi:** Meminimalkan *false positive* menggunakan sistem *Weighted Keyword Scoring* dan identifikasi teknik *Cloaking*.
*   **Aksi Cepat:** Menghasilkan laporan teks sederhana yang bisa langsung diserahkan kepada tim insiden respons (CSIRT).

## 3. Metodologi Deteksi & Logika Inti
GovSpiders menggunakan 3 lapis pemeriksaan pada setiap *endpoint* yang dipindai:
1.  **User-Agent Spoofing:** Setiap HTTP Request dikirim menggunakan dua simulasi *User-Agent*: standar (Mozilla/Chrome) dan *Crawler* (Googlebot) untuk membongkar teknik *cloaking*.
2.  **DOM Tag Parsing:** Pengecekan difokuskan pada metadata SEO (`<title>`, `<meta name="description">`, `<meta name="keywords">`) dan pencarian tag `<iframe>` atau `<script>` asing.
3.  **Threshold Scoring Engine:** 
    *   Nilai ambang batas (*threshold*) = 100 poin.
    *   Kata umum (contoh: "slot", "zeus") = 20 poin.
    *   Kata spesifik judol (contoh: "rtp live", "maxwin", "pragmatic play") = 100 poin.

## 4. Fitur Utama
*   **Subdomain Enumeration:** Mengintegrasikan pemanggilan API ke `crt.sh` untuk mengekstrak seluruh daftar subdomain dari *root domain* target secara instan.
*   **Concurrent Scanner:** Penggunaan `ThreadPoolExecutor` untuk memindai hingga 50 URL secara bersamaan tanpa memblokir proses.
*   **Color-coded CLI:** Tampilan terminal yang intuitif. Merah terang untuk indikator positif judol, Hijau untuk aman, Kuning untuk *timeout/error*.
*   **Auto-Reporting:** Mengekspor hasil pemindaian langsung ke format `govspiders_report.txt` dan `govspiders_report.json` untuk keperluan forensik lanjutan.

## 5. Arsitektur Teknis
*   **Bahasa Utama:** Python 3.9+
*   **Core Libraries:**
    *   `argparse`: Pengelolaan argumen CLI (`-d` untuk domain, `-o` untuk output).
    *   `concurrent.futures`: Manajemen *thread pool*.
    *   `requests`: Eksekusi HTTP/HTTPS.
    *   `re` (Regex): Pencocokan pola teks lanjutan.
    *   `rich`: Antarmuka terminal, pemformatan tabel, dan *progress bar*.
    *   `BeautifulSoup4` (opsional): Untuk *parsing* struktur HTML DOM yang kompleks jika *regex* tidak cukup.

## 6. Alur Kerja (Workflow)
1.  **Inisialisasi:** Pengguna mengeksekusi `python govspiders.py -d target.go.id`.
2.  **Pengumpulan (Recon):** Alat mengambil log sertifikat SSL dari crt.sh $\to$ menghasilkan daftar subdomain unik.
3.  **Pemindaian (Scanning):** Membuka 50 *threads* HTTP $\to$ memalsukan User-Agent $\to$ mengambil respons teks HTML.
4.  **Analisis (Scoring):** Mencocokkan isi HTML dengan *database signature* $\to$ menghitung bobot per URL.
5.  **Pelaporan (Output):** Mencetak hasil ke layar secara *real-time* dan menyimpan *log* URL yang terkompromi.

## 7. Fase Pengembangan (Roadmap)
*   **Tahap 1:** Rilis kerangka dasar CLI, koneksi crt.sh, dan HTTP *request* sekuensial (single-thread).
*   **Tahap 2:** Implementasi *multithreading* dan mesin deteksi *Weighted Scoring*.
*   **Tahap 3:** Integrasi *User-Agent spoofing* untuk melewati WAF dasar dan pelaporan ke format JSON.