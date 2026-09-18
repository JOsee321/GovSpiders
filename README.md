<p align="center">
  <a href="https://github.com/JOsee321/GovSpiders">
    <img src="logo.png" alt="GovSpiders Logo" width="200">
  </a>
</p>
<h1 align="center">GovSpiders</h1>
<p align="center">CLI tool to detect SEO Poisoning on government and educational domains.</p>
<p align="center"><i>Read this documentation in <a href="README_id.md">Indonesian</a></i></p><br>

---

## Key Features

- **Subdomain Enumeration (crt.sh):** Automatically gathers a complete list of target subdomains via public certificate records.
- **Concurrent Scanning (50 Threads):** Scans run in parallel asynchronously using 50 threads at once, ensuring very fast processing.
- **Regex Weighted Scoring Engine:** Detects specific elements within the DOM such as title, meta tags, and body. Keywords are assigned weighted scores. If the total score exceeds the threshold, the URL is marked as infected.
- **Double-agent Cloaking Detection:** Prevents cloaking tricks often used by attackers to deceive search engines. The script poses as Googlebot on the first request, then re-verifies using a standard browser user-agent if suspicion arises.

## Installation

Ensure you have the latest version of Python installed (minimum version 3.9).

1. Clone this repository:
   ```bash
   git clone https://github.com/JOsee321/GovSpiders.git
   cd GovSpiders
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Use the `-d` argument for the domain and `-o` for the output report filename.

CLI command example:
```bash
python govspiders.py -d target-instansi.go.id -o audit_results.txt
```

The script will immediately find all associated subdomains and scan them one by one in parallel. Output reports will be available in a text file and a JSON file containing complete details of scores and cloaking detection results.

## Disclaimer

This tool is designed purely for internal security audits and compliance purposes. Only use it on assets you manage yourself or have explicit authorization to test (e.g., by CSIRT or related institutions). Any form of misuse is solely the responsibility of the user.
