import argparse
import requests
from rich.console import Console

console = Console()

def get_subdomains(domain):
    """Mengambil daftar subdomain dari crt.sh berdasarkan domain target."""
    try:
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        subdomains = set()
        
        if isinstance(data, list):
            for item in data:
                name_value = item.get("name_value", "")
                # Pisahkan jika ada newline
                for name in name_value.split("\n"):
                    clean_name = name.strip()
                    # Hapus wildcard *.
                    if clean_name.startswith("*."):
                        clean_name = clean_name[2:]
                    if clean_name:
                        subdomains.add(clean_name)
                        
        return list(subdomains)
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red][!] Gagal terhubung ke crt.sh: {e}[/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red][!] Terjadi kesalahan saat parsing data: {e}[/bold red]")
        return []

def main():
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

    # Tampilkan pesan inisialisasi menggunakan rich
    console.print(f"[bold cyan][*] Inisialisasi GovSpiders... Memulai pemindaian untuk target: {args.domain}[/bold cyan]")

    with console.status("[bold yellow]Mencari subdomain di crt.sh...[/bold yellow]"):
        subdomains = get_subdomains(args.domain)
        
    if subdomains:
        console.print(f"[bold green][*] Berhasil menemukan {len(subdomains)} subdomain unik.[/bold green]")
    else:
        console.print("[bold red][!] Tidak ada subdomain yang ditemukan atau terjadi kesalahan.[/bold red]")

if __name__ == "__main__":
    main()
