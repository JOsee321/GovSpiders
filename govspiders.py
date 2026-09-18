import argparse
from rich.console import Console

console = Console()

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

if __name__ == "__main__":
    main()
