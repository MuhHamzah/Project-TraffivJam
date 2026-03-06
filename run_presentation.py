#!/usr/bin/env python3
"""
QUICK START - PRESENTATION SCRIPTS
===================================
Script helper untuk menjalankan semua script presentasi dengan mudah
"""

import os
import sys
import subprocess
from colorama import Fore, Back, Style, init

init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    print(f"\n{Back.CYAN}{Fore.BLACK}{'='*70}")
    print(f"{Back.CYAN}{Fore.BLACK}{text:^70}")
    print(f"{Back.CYAN}{Fore.BLACK}{'='*70}{Style.RESET_ALL}\n")

def print_menu(title, options):
    print(f"{Fore.YELLOW}{'─'*70}")
    print(f"{Fore.YELLOW}▶ {title}")
    print(f"{Fore.YELLOW}{'─'*70}")
    
    for i, (key, label, desc) in enumerate(options, 1):
        print(f"\n{Fore.LIGHTGREEN}{i}. {label}{Style.RESET_ALL}")
        print(f"   {Fore.LIGHTBLUE_EX}{desc}{Style.RESET_ALL}")

def check_app():
    """Check if app is running"""
    import requests
    try:
        requests.get("http://localhost:5000/api/health", timeout=2)
        return True
    except:
        return False

def check_dependencies():
    """Check if all dependencies are installed"""
    required = ['requests', 'colorama', 'pandas', 'tabulate']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing

def main_menu():
    clear_screen()
    print_header("SMART TRAFFIC MONITORING - PRESENTATION SCRIPTS")
    
    # Check prerequisites
    print(f"{Fore.CYAN}Checking prerequisites...{Style.RESET_ALL}\n")
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"{Fore.RED}✗ Missing dependencies: {', '.join(missing)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Install with: pip install {' '.join(missing)}{Style.RESET_ALL}\n")
        input("Press Enter to continue anyway...")
    else:
        print(f"{Fore.GREEN}✓ All dependencies installed{Style.RESET_ALL}\n")
    
    # Check app status
    app_running = check_app()
    if app_running:
        print(f"{Fore.GREEN}✓ Application is running at http://localhost:5000{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.YELLOW}⚠ Application not detected at http://localhost:5000{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Start it with: python app.py{Style.RESET_ALL}\n")
    
    while True:
        print_menu("SELECT PRESENTATION SCRIPT", [
            (1, "Demo Aplikasi", "Penjelasan komprehensif semua halaman & fitur"),
            (2, "Presentasi Visual", "Tabel terstruktur untuk formal presentation"),
            (3, "API Test", "Testing semua 14 API endpoints"),
            (4, "View Documentation", "Baca PRESENTATION_SCRIPTS_README.md"),
            (5, "Exit", "Keluar dari menu"),
        ])
        
        choice = input(f"\n{Fore.LIGHTGREEN}Pilih menu (1-5): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            run_demo_aplikasi()
        elif choice == '2':
            run_presentasi_visual()
        elif choice == '3':
            run_api_test()
        elif choice == '4':
            view_documentation()
        elif choice == '5':
            print(f"\n{Fore.GREEN}Terima kasih! Sampai jumpa.{Style.RESET_ALL}\n")
            break
        else:
            print(f"{Fore.RED}Pilihan tidak valid!{Style.RESET_ALL}")

def run_demo_aplikasi():
    print_header("DEMO APLIKASI")
    
    print(f"""{Fore.CYAN}
Menampilkan:
  ✓ Penjelasan 10 halaman aplikasi
  ✓ Daftar kamera & konfigurasi
  ✓ Real-time data, analytics, forecast
  ✓ Maps routing, system health
  ✓ Data export & multi-camera analysis

Script ini cocok untuk presentasi umum dan training.
{Style.RESET_ALL}""")
    
    input(f"{Fore.LIGHTGREEN}Tekan Enter untuk menjalankan...{Style.RESET_ALL}")
    
    try:
        subprocess.run([sys.executable, 'demo_aplikasi.py'], check=True)
    except subprocess.CalledProcessError:
        print(f"{Fore.RED}Error menjalankan script{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.RED}File demo_aplikasi.py tidak ditemukan{Style.RESET_ALL}")
    
    input(f"\n{Fore.LIGHTGREEN}Tekan Enter untuk kembali ke menu...{Style.RESET_ALL}")

def run_presentasi_visual():
    print_header("PRESENTASI VISUAL")
    
    print(f"""{Fore.CYAN}
Menampilkan data dalam format tabel professional:
  ✓ Section 1: Dashboard Overview
  ✓ Section 2: Real-Time Data (Per-Second)
  ✓ Section 3: Aggregated Data (Per-Minute)
  ✓ Section 4: Daily Statistics
  ✓ Section 5: Traffic Forecast
  ✓ Section 6: Maps & Routing
  ✓ Section 7: System Health
  ✓ Section 8: Multi-Camera Comparison

Script ini cocok untuk formal meeting dan reporting.
{Style.RESET_ALL}""")
    
    input(f"{Fore.LIGHTGREEN}Tekan Enter untuk menjalankan...{Style.RESET_ALL}")
    
    try:
        subprocess.run([sys.executable, 'presentasi_visual.py'], check=True)
    except subprocess.CalledProcessError:
        print(f"{Fore.RED}Error menjalankan script{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.RED}File presentasi_visual.py tidak ditemukan{Style.RESET_ALL}")
    
    input(f"\n{Fore.LIGHTGREEN}Tekan Enter untuk kembali ke menu...{Style.RESET_ALL}")

def run_api_test():
    print_header("API TEST SUITE")
    
    print(f"""{Fore.CYAN}
Testing 14 API endpoints dengan detailed logging:
{Style.RESET_ALL}""")
    
    print(f"""
  1. System Health              7. Daily Summary
  2. Configuration              8. Traffic Forecast
  3. Diagnostics                9. Map Data
  4. Camera Locations           10. Routes/Routing
  5. Real-Time (Per-Second)     11. Detection Control
  6. Per-Minute                 12. CSV Download
  
  13. All Cameras Daily         14. Page Routes

Pilihan:
  {Fore.LIGHTGREEN}Enter{Style.RESET_ALL}        - Run semua tests
  {Fore.LIGHTGREEN}health{Style.RESET_ALL}      - Test health check saja
  {Fore.LIGHTGREEN}routes{Style.RESET_ALL}      - Test routing saja
  {Fore.LIGHTGREEN}forecast{Style.RESET_ALL}    - Test forecast saja
  {Fore.LIGHTGREEN}q{Style.RESET_ALL}           - Kembali

Contoh: {Fore.LIGHTGREEN}python api_test.py health{Style.RESET_ALL}
""")
    
    choice = input(f"{Fore.LIGHTGREEN}Pilih (Enter/health/routes/forecast/q): {Style.RESET_ALL}").strip().lower()
    
    if choice == 'q':
        return
    
    try:
        if choice == '':
            subprocess.run([sys.executable, 'api_test.py'], check=True)
        else:
            subprocess.run([sys.executable, 'api_test.py', choice], check=True)
    except subprocess.CalledProcessError:
        print(f"{Fore.RED}Error menjalankan script{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.RED}File api_test.py tidak ditemukan{Style.RESET_ALL}")
    
    input(f"\n{Fore.LIGHTGREEN}Tekan Enter untuk kembali ke menu...{Style.RESET_ALL}")

def view_documentation():
    print_header("DOCUMENTATION")
    
    doc_file = "PRESENTATION_SCRIPTS_README.md"
    
    if not os.path.exists(doc_file):
        print(f"{Fore.RED}File {doc_file} tidak ditemukan{Style.RESET_ALL}\n")
        input(f"{Fore.LIGHTGREEN}Tekan Enter untuk kembali...{Style.RESET_ALL}")
        return
    
    # Try to open with default text editor
    try:
        if sys.platform == 'win32':
            os.startfile(doc_file)
        elif sys.platform == 'darwin':  # macOS
            subprocess.run(['open', doc_file], check=True)
        else:  # Linux
            subprocess.run(['xdg-open', doc_file], check=True)
    except Exception as e:
        # Fallback: print file content
        print(f"{Fore.YELLOW}Opening file in terminal...{Style.RESET_ALL}\n")
        try:
            with open(doc_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Show first 50 lines, then allow scrolling
                for i, line in enumerate(lines[:50]):
                    print(line, end='')
                
                if len(lines) > 50:
                    print(f"\n{Fore.YELLOW}... ({len(lines)} total lines) ...{Style.RESET_ALL}\n")
                    print(f"{Fore.YELLOW}File is too long to display. Open it with a text editor:{Style.RESET_ALL}")
                    print(f"  {doc_file}")
        except Exception as read_error:
            print(f"{Fore.RED}Error reading file: {str(read_error)}{Style.RESET_ALL}")
    
    input(f"\n{Fore.LIGHTGREEN}Tekan Enter untuk kembali...{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Program dihentikan.{Style.RESET_ALL}")
        sys.exit(0)
