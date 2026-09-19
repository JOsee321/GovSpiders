import argparse
import requests
import concurrent.futures
import re
import json
import time
import random
import urllib3
import os
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from rich.console import Console

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()

def load_rules():
    default_rules = {
        "threshold": 100,
        "signatures": {
            "100": [
                "rtp live", "maxwin", "pragmatic play", "slot gacor", "judi online", 
                "situs toto", "bandar togel", "pg soft", "mahjong ways", "gates of olympus",
                "slot deposit dana", "pola slot", "situs judi terpercaya", "agen taruhan",
                "slot88", "sbobet", "judi bola", "togel macau", "toto wuhan", "situs gampang menang"
            ],
            "50": [
                "bonus new member", "deposit pulsa tanpa potongan", "anti rungkad", 
                "bocoran rtp", "wd kilat", "minimal deposit", "link alternatif", 
                "daftar akun pro", "server thailand", "server kamboja", "pasti jp"
            ],
            "20": [
                "slot", "zeus", "toto", "togel", "deposit", "bet", "gacor", 
                "scatter", "jackpot", "taruhan", "casino", "poker", "roulette"
            ]
        },
        "syndicate_footprints": [
            "wa.me/", "api.whatsapp.com/", "t.me/", "t.link/", "linktr.ee/", "heylink.me/", 
            "s.id/", "bit.ly/", "cutt.ly/", "tinyurl.com/",
            ".vip", ".top", ".cc", ".icu", ".xyz", ".win", ".club", ".click", ".pro",
            "rtp", "bet", "gacor", "slot", "toto", "judi", "togel"
        ]
    }
    if not os.path.exists("rules.json"):
        try:
            with open("rules.json", "w") as f:
                json.dump(default_rules, f, indent=4)
        except Exception as e:
            console.print(f"[bold red][!] Gagal membuat file rules.json default: {e}[/bold red]")
            
    try:
        with open("rules.json", "r") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[bold red][!] Gagal membaca rules.json, menggunakan rules default. Error: {e}[/bold red]")
        return default_rules

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
]


def crawl_urls(base_url, max_depth, proxy_url=None):
    visited_urls = set()
    urls_to_visit = [(base_url, 0)]
    internal_urls = set([base_url])
    
    base_domain = urlparse(base_url).netloc
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
    
    while urls_to_visit:
        current_url, current_depth = urls_to_visit.pop(0)
        
        if current_url in visited_urls or current_depth > max_depth:
            continue
            
        visited_urls.add(current_url)
        
        try:
            selected_ua = random.choice(USER_AGENTS)
            headers = {"User-Agent": selected_ua}
            response = requests.get(current_url, headers=headers, proxies=proxies, timeout=10, verify=False)
            
            if "text/html" in response.headers.get("Content-Type", ""):
                soup = BeautifulSoup(response.text, 'html.parser')
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    absolute_url = urljoin(current_url, href)
                    parsed_url = urlparse(absolute_url)
                    
                    if parsed_url.netloc == base_domain and absolute_url not in visited_urls:
                        internal_urls.add(absolute_url)
                        if current_depth + 1 <= max_depth:
                            urls_to_visit.append((absolute_url, current_depth + 1))
        except Exception:
            pass
            
    return internal_urls

def extract_syndicates(base_url, soup_obj, rules_dict):
    syndicate_links = set()
    base_domain = urlparse(base_url).netloc
    footprints = rules_dict.get("syndicate_footprints", [])
    
    if not footprints:
        return []
        
    for a_tag in soup_obj.find_all('a', href=True):
        href = a_tag['href']
        parsed_url = urlparse(href)
        
        if not parsed_url.netloc or parsed_url.netloc == base_domain:
            continue
            
        href_lower = href.lower()
        for fp in footprints:
            if fp.lower() in href_lower:
                syndicate_links.add(href)
                break
                
    return list(syndicate_links)

def check_url(url, rules_data, proxy_url=None):
    if not url.startswith("http"):
        url = f"http://{url}"
    
    proxies = None
    if proxy_url:
        proxies = {"http": proxy_url, "https": proxy_url}
        
    try:
        selected_ua_1 = random.choice(USER_AGENTS)
        headers_1 = {"User-Agent": selected_ua_1}
        response = requests.get(url, headers=headers_1, proxies=proxies, timeout=10, verify=False)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        total_skor = 0
        
        title_text = ""
        target_texts = []
        if soup.title and soup.title.string:
            title_text = soup.title.string.strip()
            target_texts.append(title_text.lower())
            
        meta_desc = soup.find('meta', attrs={'name': re.compile(r'^description$', re.I)})
        if meta_desc and meta_desc.get('content'):
            target_texts.append(meta_desc.get('content').lower())
            
        meta_keys = soup.find('meta', attrs={'name': re.compile(r'^keywords$', re.I)})
        if meta_keys and meta_keys.get('content'):
            target_texts.append(meta_keys.get('content').lower())
            
        if soup.body:
            target_texts.append(soup.body.get_text(separator=' ').lower())
            
        combined_text = " ".join(target_texts)
        
        for weight_str, keywords in rules_data.get("signatures", {}).items():
            try:
                weight = int(weight_str)
            except ValueError:
                continue
            for keyword in keywords:
                if re.search(re.escape(keyword), combined_text, re.IGNORECASE):
                    total_skor += weight
                    
        hidden_tags = soup.find_all(['iframe', 'script'])
        for tag in hidden_tags:
            style = tag.get('style', '').lower()
            if 'display:none' in style or 'display: none' in style or 'visibility:hidden' in style or 'visibility: hidden' in style:
                total_skor += 50
                break
                
        threshold = rules_data.get("threshold", 100)
        status = "terinfeksi" if total_skor >= threshold else "aman"
        cloaking = False
        syndicate_links = []
        
        if status == "terinfeksi":
            syndicate_links = extract_syndicates(url, soup, rules_data)
            try:
                selected_ua_2 = random.choice(USER_AGENTS)
                headers_2 = {"User-Agent": selected_ua_2}
                response_std = requests.get(url, headers=headers_2, proxies=proxies, timeout=10, verify=False)
                html_std = response_std.text.lower()
                
                is_clean = True
                for weight_str, keywords in rules_data.get("signatures", {}).items():
                    for keyword in keywords:
                        if re.search(re.escape(keyword), html_std, re.IGNORECASE):
                            is_clean = False
                            break
                    if not is_clean:
                        break
                        
                if is_clean:
                    cloaking = True
            except requests.exceptions.RequestException:
                pass
                
        return {"url": url, "status": status, "score": total_skor, "cloaking": cloaking, "title": title_text, "syndicate_links": syndicate_links}
        
    except requests.exceptions.RequestException:
        return {"url": url, "status": "error", "score": 0, "cloaking": False, "title": "", "syndicate_links": []}

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
        console.print(f"[bold red][!] All enumeration methods failed. AlienVault error: {e}[/bold red]")
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
                    console.print(f"[bold yellow][!] crt.sh error {response.status_code}. Retrying ({attempt}/{max_retries})...[/bold yellow]")
                    time.sleep(2)
                    continue
                else:
                    console.print("[bold yellow][!] crt.sh unresponsive. Activating Fallback Reconnaissance via AlienVault OTX...[/bold yellow]")
                    return alienvault_fallback(domain)
            console.print(f"[bold red][!] Failed to connect to crt.sh: {e}[/bold red]")
            return alienvault_fallback(domain)
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                console.print(f"[bold yellow][!] Connection issue. Retrying ({attempt}/{max_retries})...[/bold yellow]")
                time.sleep(2)
                continue
            console.print("[bold yellow][!] crt.sh unresponsive. Activating Fallback Reconnaissance via AlienVault OTX...[/bold yellow]")
            return alienvault_fallback(domain)
            
        except Exception as e:
            console.print(f"[bold red][!] Error occurred during data parsing: {e}[/bold red]")
            return []
            
    return []

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="GovSpiders - SEO poisoning/Defacement scanner for government and educational domain infrastructure."
    )
    parser.add_argument(
        "-d", "--domain", 
        required=True, 
        help="Target root domain to scan (e.g., target.go.id)"
    )
    parser.add_argument(
        "-p", "--proxy", 
        required=False, 
        help="Route traffic through HTTP/HTTPS proxy (e.g., http://127.0.0.1:8080)"
    )
    parser.add_argument(
        "--depth", 
        type=int,
        default=2,
        help="Maximum crawling depth (default: 2)"
    )
    parser.add_argument(
        "-o", "--output", 
        required=False, 
        help="Output filename for reporting (optional)"
    )

    args = parser.parse_args()
    
    rules_data = load_rules()

    # Display initialization message using rich
    console.print(f"[bold cyan][*] Initializing GovSpiders... Starting scan for target: {args.domain}[/bold cyan]")

    with console.status("[bold yellow]Searching for subdomains via crt.sh...[/bold yellow]"):
        subdomains = get_subdomains(args.domain)
        
    if subdomains:
        console.print(f"[bold green][*] Successfully found {len(subdomains)} unique subdomains.[/bold green]")
        
        all_urls_to_scan = set()
        with console.status(f"[bold yellow]Performing deep crawling (depth: {args.depth}) on subdomains...[/bold yellow]"):
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                future_to_crawl = {executor.submit(crawl_urls, f"http://{sub}", args.depth, args.proxy): sub for sub in subdomains}
                
                for future in concurrent.futures.as_completed(future_to_crawl):
                    all_urls_to_scan.update(future.result())
                    
        console.print(f"[bold cyan][*] Starting multithreaded scanning on {len(all_urls_to_scan)} URLs...[/bold cyan]")
        
        infected_results = []
        json_results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            future_to_url = {executor.submit(check_url, url, rules_data, args.proxy): url for url in all_urls_to_scan}
            
            for future in concurrent.futures.as_completed(future_to_url):
                result = future.result()
                
                status_mapped = "Vulnerable" if result["status"] == "terinfeksi" else "Safe" if result["status"] == "aman" else "Timeout/Error"
                json_results.append({
                    "url": result["url"],
                    "score": result["score"],
                    "status": status_mapped,
                    "cloaking_detected": result["cloaking"],
                    "title": result.get("title", ""),
                    "syndicate_links": result.get("syndicate_links", [])
                })
                
                if result["status"] == "terinfeksi":
                    if result.get("cloaking"):
                        console.print(f"[bold red][VULNERABLE] [CLOAKING] {result['url']} (Score: {result['score']})[/bold red]")
                    else:
                        console.print(f"[bold red][VULNERABLE] {result['url']} (Score: {result['score']})[/bold red]")
                    
                    syndicates = result.get("syndicate_links", [])
                    if syndicates:
                        console.print(f"[bold yellow][!] Syndicate Footprints Detected: {len(syndicates)} link(s) detected.[/bold yellow]")
                        
                    infected_results.append(result)
                elif result["status"] == "aman":
                    console.print(f"[green][SAFE] {result['url']}[/green]")
                elif result["status"] == "error":
                    console.print(f"[yellow][TIMEOUT/ERROR] {result['url']}[/yellow]")
                    
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
            json.dump(json_results, f_json, indent=4)
            
        console.print(f"\n[bold cyan][*] Scan complete! TXT report saved to {txt_filename} and forensic log to {json_filename}[/bold cyan]")
        
    else:
        console.print("[bold red][!] No subdomains found or an error occurred.[/bold red]")

if __name__ == "__main__":
    main()
