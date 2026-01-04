# ESP32 + MicroPython — Instrukcja

Krótki przewodnik: jak sflashować firmware i wgrać `main.py` na moduł ESP32 używając PowerShella na Windows.

**Wymagania:**
- `Python 3.8+` oraz `pip`
- `esptool` (lub `esptool.py`) oraz `mpremote` (zalecane)

Instalacja narzędzi (PowerShell):
```powershell
pip install esptool mpremote
```

**1. Flashowanie modułu**
- Opis: przed wgraniem nowego firmware zaleca się wymazać pamięć flash modułu.
- Polecenia (uruchom w PowerShell; dopasuj port/plik firmware do swojego sprzętu):
```powershell
esptool erase-flash
esptool --baud 460800 write_flash 0 .\ESP32_GENERIC_C3-20251209-v1.27.0.bin
```

Uwaga: w niektórych instalacjach polecenie może być `esptool.py erase_flash` oraz `esptool.py --baud 460800 write_flash 0 <firmware.bin>` — użyj formatu zgodnego z Twoją instalacją.

**2. Wgrywanie `main.py` na urządzenie**
- Opis: użyj `mpremote` aby skopiować lokalny `main.py` do katalogu root systemu plików MicroPython.
- Polecenie (przykład dla portu `COM9`):
```powershell
mpremote connect COM9 fs cp .\main.py :/main.py
```

Po wgraniu `main.py` urządzenie wykona kod podczas restartu (jeśli firmware używa `boot.py`/`main.py`).

**3. Polecenia pomocnicze**
- Wylistowanie plików na urządzeniu:
```powershell
mpremote connect COM9 fs ls
```
- Uruchomienie REPL na urządzeniu:
```powershell
mpremote connect COM9 repl
```

**Przydatne wskazówki:**
- Zmień `COM9` na numer portu, do którego podłączone jest Twoje urządzenie.
- Jeśli pojawią się problemy z połączeniem, sprawdź menedżera urządzeń oraz kable USB.
- W repozytorium znajdziesz skrypty pomocnicze w `scripts\\` (np. `deploy.ps1`) — możesz je uruchomić zamiast ręcznych komend.

Jeżeli chcesz, mogę zaktualizować `scripts\\deploy.ps1` żeby używał powyższego polecenia `mpremote` dla `COM9`.

ESP 1 MAC ADDRESS: ec:da:3b:bd:64:38
ESP 2 MAC ADDRESS: 
