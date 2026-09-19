<p align="center">
  <img src="https://github.com/user-attachments/assets/5bd6d4b9-0835-44cb-be71-ffad6af64a00" alt="GovSpiders Logo" width="200">
</p>
<h1 align="center">GovSpiders</h1>
<p align="center">CLI tool to detect SEO Poisoning on government and educational domains.</p>
<p align="center"><i>Read this documentation in <a href="README_id.md">Indonesian</a></i></p><br>

---

## Key Features

- **Subdomain Enumeration (crt.sh):** Automatically gathers a complete list of target subdomains via public certificate records.
- **Concurrent Scanning (50 Threads):** Scans run in parallel asynchronously using 50 threads at once, ensuring very fast processing.
- **Regex Weighted Scoring Engine:** Detects specific elements within the DOM such as title, meta tags, and body. Keywords are assigned weighted scores. If the total score exceeds the threshold, the URL is marked as infected.
- **Heuristic OSINT / Syndicate Mapping:** Automatically extracts affiliate communication links (such as WhatsApp, Telegram, or gambling domains) from infected pages to map syndicate networks.
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

Use the `-d` argument for the domain, `-o` for the output report filename, `--proxy` (or `-p`) to route traffic through an HTTP/HTTPS proxy (e.g., `http://127.0.0.1:8080`), and `--depth` to set the maximum crawling depth (default: 2).

CLI command example:
```bash
python govspiders.py -d target-instansi.go.id -o audit_results.txt --proxy http://127.0.0.1:8080 --depth 3
```

The script will immediately find all associated subdomains, crawl them using BeautifulSoup to find all internal sub-directory links up to the specified depth, and scan all gathered URLs one by one in parallel. The tool automatically generates two types of output: a human-readable `.txt` file and a pipeline-ready `.json` file for integration into external tools like Nuclei or Burp Suite.

## Threat Intelligence Dashboard

GovSpiders includes a web-based GUI dashboard built with Streamlit to visualize the `.json` output from your scans. The dashboard displays key metrics, an interactive ratio chart, and a relational table of extracted syndicate footprints.

To run the dashboard:
```bash
streamlit run dashboard.py
```
*Note: If you run this on a remote server, you may want to pass `--server.headless true` or simply answer the email prompt if it's your first time running Streamlit.*

## Customization

You can easily customize the detection keywords and their corresponding scoring weights by editing the `rules.json` file. This allows you to add or modify online gambling keywords without needing to touch the Python source code. Additionally, you can add new syndicate footprints (like specific TLDs or URL paths) to the `syndicate_footprints` array so the engine detects them as malicious outbound links. If the file is deleted or missing, GovSpiders will automatically generate a new one with the default signature database.

Example JSON output:
```json
[
  {
    "url": "http://dinas.target-instansi.go.id/path",
    "score": 140,
    "status": "Vulnerable",
    "cloaking_detected": true,
    "title": "Situs Gacor",
    "syndicate_links": [
      "https://wa.me/6281234567890"
    ]
  }
]
```

## Disclaimer

This tool is designed purely for internal security audits and compliance purposes. Only use it on assets you manage yourself or have explicit authorization to test (e.g., by CSIRT or related institutions). Any form of misuse is solely the responsibility of the user.
