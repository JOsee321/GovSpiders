<p align="center">
  <img src="https://github.com/user-attachments/assets/5bd6d4b9-0835-44cb-be71-ffad6af64a00" alt="GovSpiders Logo" width="200">
</p>
<h1 align="center">GovSpiders</h1>
<p align="center">CLI tool untuk mendeteksi sisipan judol (SEO Poisoning) pada domain pemerintah dan kampus.</p>
<p align="center"><i>Read this documentation in <a href="README.md">English</a></i></p><br>

---

## Fitur Utama

- **Subdomain Enumeration (crt.sh):** Secara otomatis mengumpulkan seluruh daftar subdomain target melalui rekaman sertifikat publik.
- **Concurrent Scanning (50 Threads):** Pemindaian berjalan paralel secara asinkron menggunakan 50 thread sekaligus, sehingga proses sangat cepat.
- **Regex Weighted Scoring Engine:** Mendeteksi elemen khusus di dalam DOM seperti title, meta tags, dan body. Kata kunci diberi bobot skor. Jika total skor melampaui batas ambang, URL ditandai terinfeksi.
- **Double-agent Cloaking Detection:** Mencegah trik cloaking yang sering dipakai peretas untuk mengelabui mesin pencari. Skrip ini akan menyamar sebagai Googlebot pada request pertama, lalu memverifikasi ulang dengan user-agent browser biasa jika ditemukan kecurigaan.

## Cara Instalasi

Pastikan Python versi terbaru (minimal versi 3.9) sudah terpasang.

1. Clone repositori ini:
   ```bash
   git clone https://github.com/JOsee321/GovSpiders.git
   cd GovSpiders
   ```

2. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```

## Cara Penggunaan

Gunakan argumen `-d` untuk domain, `-o` untuk nama file output laporannya, `--proxy` (atau `-p`) untuk merutekan trafik melalui proxy HTTP/HTTPS (contoh: `http://127.0.0.1:8080`), dan `--depth` untuk mengatur kedalaman maksimal crawling (default: 2).

Contoh command CLI:
```bash
python govspiders.py -d target-instansi.go.id -o hasil_audit.txt --proxy http://127.0.0.1:8080 --depth 3
```

Skrip akan langsung bekerja mencari semua subdomain yang berasosiasi, melakukan spidering menggunakan BeautifulSoup untuk mengumpulkan semua link sub-direktori internal target hingga kedalaman yang ditentukan, lalu memindainya satu per satu secara paralel. Tool ini secara otomatis menghasilkan dua jenis output: file `.txt` untuk pembacaan manusia dan file `.json` (pipeline-ready) untuk integrasi ke tools eksternal seperti Nuclei atau Burp Suite.

## Kustomisasi Deteksi

Pengguna dapat dengan mudah menambah atau mengubah kata kunci judi online beserta bobot skornya hanya dengan mengedit file `rules.json`, tanpa perlu menyentuh kode Python. Jika file tersebut dihapus atau tidak ditemukan, GovSpiders secara otomatis akan men-generate ulang file tersebut menggunakan signature database bawaan.

## Disclaimer

Tool ini dirancang murni untuk tujuan audit keamanan dan kepatuhan internal. Gunakan hanya pada aset yang Anda kelola sendiri, atau yang sudah diizinkan (misal oleh CSIRT/institusi terkait). Segala bentuk penyalahgunaan adalah tanggung jawab pengguna sepenuhnya.
