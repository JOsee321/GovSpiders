import argparse
import requests
import concurrent.futures
import re
import json
import time
from bs4 import BeautifulSoup
from rich.console import Console

console = Console()

SIGNATURES = {
    "slot": 20, 
    "gacor": 50, 
    "rtp live": 100, 
    "deposit pulsa": 100, 
    "maxwin": 100, 
    "zeus": 20,
    "pragmatic play": 100
}

def check_url(subdomain):
    url = f"http://{subdomain}"
    headers_bot = {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    }
    headers_std = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers_bot, timeout=10)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        total_skor = 0
        
        target_texts = []
        if soup.title and soup.title.string:
            target_texts.append(soup.title.string.lower())
            
        meta_desc = soup.find('meta', attrs={'name': re.compile(r'^description$', re.I)})
        if meta_desc and meta_desc.get('content'):
            target_texts.append(meta_desc.get('content').lower())
            
        meta_keys = soup.find('meta', attrs={'name': re.compile(r'^keywords$', re.I)})
        if meta_keys and meta_keys.get('content'):
            target_texts.append(meta_keys.get('content').lower())
            
        if soup.body:
            target_texts.append(soup.body.get_text(separator=' ').lower())
            
        combined_text = " ".join(target_texts)
        
        for keyword, weight in SIGNATURES.items():
            if re.search(re.escape(keyword), combined_text, re.IGNORECASE):
                total_skor += weight
                
        hidden_tags = soup.find_all(['iframe', 'script'])
        for tag in hidden_tags:
            style = tag.get('style', '').lower()
            if 'display:none' in style or 'display: none' in style or 'visibility:hidden' in style or 'visibility: hidden' in style:
                total_skor += 50
                break
                
        status = "terinfeksi" if total_skor >= 100 else "aman"
        cloaking = False
        
        if status == "terinfeksi":
            try:
                response_std = requests.get(url, headers=headers_std, timeout=10)
                html_std = response_std.text.lower()
                
                is_clean = True
                for keyword in SIGNATURES.keys():
                    if re.search(re.escape(keyword), html_std, re.IGNORECASE):
                        is_clean = False
                        break
                        
                if is_clean:
                    cloaking = True
            except requests.exceptions.RequestException:
                pass
                
        return {"url": subdomain, "status": status, "score": total_skor, "cloaking": cloaking}
        
    except requests.exceptions.RequestException:
        return {"url": subdomain, "status": "error", "score": 0, "cloaking": False}

def print_banner():
    banner = r"""
[bold #0B2F4C]  ____             [/][bold #1BA6B2] ____       _     _               [/]
[bold #0B2F4C] / ___| _____   __/[/][bold #1BA6B2] ___| _ __ (_) __| | ___ _ __ ___ [/]
[bold #0B2F4C]| |  _ / _ \ \ / /[/][bold #1BA6B2]\___ \| '_ \| |/ _` |/ _ \ '__/ __|[/]
[bold #0B2F4C]| |_| | (_) \ V / [/][bold #1BA6B2] ___) | |_) | | (_| |  __/ |  \__ \[/]
[bold #0B2F4C] \____|\___/ \_/  [/][bold #1BA6B2]|____/| .__/|_|\__,_|\___|_|  |___/[/]
[bold #0B2F4C]                  [/][bold #1BA6B2]      |_|                          [/]
"""
    console.print(banner)

def alienvault_fallback(domain):
    """Fallback reconnaissance using AlienVault OTX API."""
    try:
        url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        subdomains = set()
        
        if "passive_dns" in data:
            for entry in data["passive_dns"]:
                hostname = entry.get("hostname", "")
                if hostname.endswith(domain):
                    subdomains.add(hostname)
                    
        return list(subdomains)
    except Exception as e:
        console.print(f"[bold red][!] Semua metode enumerasi telah gagal. AlienVault error: {e}[/bold red]")
        return []

def get_subdomains(domain):
    """Fetch a list of subdomains from crt.sh based on the target domain."""
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    max_retries = 3
    
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            subdomains = set()
            
            if isinstance(data, list):
                for item in data:
                    name_value = item.get("name_value", "")
                    # Split if there are newlines
                    for name in name_value.split("\n"):
                        clean_name = name.strip()
                        # Remove wildcard *.
                        if clean_name.startswith("*."):
                            clean_name = clean_name[2:]
                        if clean_name:
                            subdomains.add(clean_name)
                            
            return list(subdomains)
            
        except requests.exceptions.HTTPError as e:
            if response.status_code in [500, 502, 503, 504]:
                if attempt < max_retries:
                    console.print(f"[bold yellow][!] crt.sh error {response.status_code}. Mencoba ulang ({attempt}/{max_retries})...[/bold yellow]")
                    time.sleep(2)
                    continue
                else:
                    console.print("[bold yellow][!] crt.sh gagal merespons. Mengaktifkan Fallback Reconnaissance via AlienVault OTX...[/bold yellow]")
                    return alienvault_fallback(domain)
            console.print(f"[bold red][!] Gagal terhubung ke crt.sh: {e}[/bold red]")
            return alienvault_fallback(domain)
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                console.print(f"[bold yellow][!] Koneksi bermasalah. Mencoba ulang ({attempt}/{max_retries})...[/bold yellow]")
                time.sleep(2)
                continue
            console.print("[bold yellow][!] crt.sh gagal merespons. Mengaktifkan Fallback Reconnaissance via AlienVault OTX...[/bold yellow]")
            return alienvault_fallback(domain)
            
        except Exception as e:
            console.print(f"[bold red][!] Terjadi kesalahan saat parsing data: {e}[/bold red]")
            return []
            
    return []

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="GovSpiders - Pemindai SEO poisoning/Defacement pada infrastruktur domain pemerintah dan pendidikan."
    )
    parser.add_argument(
        "-d", "--domain", 
        required=True, 
        help="Target root domain untuk dipindai (contoh: target.go.id)"
    )
    parser.add_argument(
        "-o", "--output", 
        required=False, 
        help="Nama file output untuk pelaporan (opsional)"
    )

    args = parser.parse_args()

    # Display initialization message using rich
    console.print(f"[bold cyan][*] Inisialisasi GovSpiders... Memulai pemindaian untuk target: {args.domain}[/bold cyan]")

    with console.status("[bold yellow]Mencari subdomain di crt.sh...[/bold yellow]"):
        subdomains = get_subdomains(args.domain)
        
    if subdomains:
        console.print(f"[bold green][*] Berhasil menemukan {len(subdomains)} subdomain unik.[/bold green]")
        
        console.print("[bold cyan][*] Memulai pemindaian multithreading...[/bold cyan]")
        
        infected_results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            future_to_url = {executor.submit(check_url, sub): sub for sub in subdomains}
            
            for future in concurrent.futures.as_completed(future_to_url):
                result = future.result()
                
                if result["status"] == "terinfeksi":
                    if result.get("cloaking"):
                        console.print(f"[bold red][TERINFEKSI] [CLOAKING] {result['url']} (Skor: {result['score']})[/bold red]")
                    else:
                        console.print(f"[bold red][TERINFEKSI] {result['url']} (Skor: {result['score']})[/bold red]")
                    infected_results.append(result)
                elif result["status"] == "aman":
                    console.print(f"[green][AMAN] {result['url']}[/green]")
                elif result["status"] == "error":
                    console.print(f"[yellow][ERROR] {result['url']}[/yellow]")
                    
        # Export process
        if args.output:
            txt_filename = args.output
        else:
            txt_filename = "govspiders_report.txt"
            
        # Separate extension and replace with json
        if "." in txt_filename:
            json_filename = txt_filename.rsplit(".", 1)[0] + ".json"
        else:
            json_filename = txt_filename + ".json"
            
        with open(txt_filename, "w") as f_txt:
            for item in infected_results:
                f_txt.write(f"{item['url']}\n")
                
        with open(json_filename, "w") as f_json:
            json.dump(infected_results, f_json, indent=4)
            
        console.print(f"\n[bold cyan][*] Pemindaian selesai! Laporan TXT disimpan di {txt_filename} dan log forensik di {json_filename}[/bold cyan]")
        
    else:
        console.print("[bold red][!] Tidak ada subdomain yang ditemukan atau terjadi kesalahan.[/bold red]")

if __name__ == "__main__":
    main()
