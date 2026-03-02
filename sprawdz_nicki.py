import requests
import string
import time
import threading
from queue import Queue
from datetime import datetime
import traceback
import sys
import os

print("="*70)
print("   SKRYPT SPRAWDZANIA 3-LITEROWYCH NICKÓW UBISOFT")
print("="*70)
print("Uruchamiam skrypt...\n")

# === SPRAWDZENIE BIBLIOTEKI requests ===
try:
    session = requests.Session()
    print("✓ Biblioteka requests jest zainstalowana")
except ImportError:
    print("✗ BŁĄD: Brak biblioteki 'requests'")
    print("   Wpisz w cmd: pip install requests")
    input("\nNaciśnij Enter aby zamknąć...")
    sys.exit()

# =====================================================================
#   ZAPIS W FOLDERZE DOKUMENTY (zawsze działa!)
# =====================================================================
documents = os.path.join(os.path.expanduser("~"), "Documents", "UbiNicki")
os.makedirs(documents, exist_ok=True)

SAVE_AVAILABLE_TO = os.path.join(documents, "wolne_nicki.txt")
SAVE_TAKEN_TO     = os.path.join(documents, "zajete_nicki.txt")

print(f"✓ Wyniki będą zapisane tutaj:")
print(f"   {documents}")
print("   (otwórz folder Dokumenty → UbiNicki)\n")
# =====================================================================

THREAD_COUNT = 8
DELAY_BETWEEN = 0.2
TIMEOUT = 8

session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
})

q = Queue()
available_count = 0
taken_count = 0
lock = threading.Lock()

# =====================================================================

def save_nick(nick: str, available: bool):
    global available_count, taken_count
    fname = SAVE_AVAILABLE_TO if available else SAVE_TAKEN_TO
    try:
        with lock:
            with open(fname, "a", encoding="utf-8") as f:
                f.write(nick + "\n")
            
            if available:
                available_count += 1
                print(f"[FREE]  {nick}   ← WOLNY!")
            else:
                taken_count += 1
                print(f"[TAKEN] {nick}")
    except Exception as e:
        print(f"✗ Błąd zapisu {nick}: {e}")

def check_one(nick: str):
    try:
        r = session.get(
            f"https://public-ubiservices.ubi.com/v3/profiles?namesOnPlatform={nick}&platformType=uplay",
            timeout=TIMEOUT
        )
        
        if r.status_code == 429:
            print(f"  Rate limit - czekam 30s...")
            time.sleep(30)
            return check_one(nick)
            
        is_available = len(r.json()) == 0
        save_nick(nick, is_available)
        
    except Exception as e:
        print(f"  Błąd przy {nick}: {e}")

def worker():
    while True:
        try:
            nick = q.get_nowait()
            check_one(nick)
            time.sleep(DELAY_BETWEEN)
        except:
            break

def main():
    print(f"[{datetime.now():%H:%M:%S}] Generuję 46 656 kombinacji...\n")
    
    chars = string.ascii_lowercase + string.digits
    total = 0
    for a in chars:
        for b in chars:
            for c in chars:
                q.put(a + b + c)
                total += 1
    
    print(f"Łącznie do sprawdzenia: {total:,}")
    print("Rozpoczynam sprawdzanie...\n")
    
    threads = []
    for _ in range(THREAD_COUNT):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    print("\n" + "="*60)
    print(f"ZAKOŃCZONO!")
    print(f"Wolne: {available_count} | Zajęte: {taken_count}")
    print(f"Pliki znajdziesz w: {documents}")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n=== WYSTĄPIŁ BŁĄD ===")
        traceback.print_exc()
    finally:
        print("\nSkrypt zakończył pracę.")
        input("Naciśnij Enter, aby zamknąć okno...") 
//xpp