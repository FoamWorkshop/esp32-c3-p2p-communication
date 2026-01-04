# Wymagane narzędzia hosta — szczegóły

Ten dokument opisuje narzędzia rekomendowane do pracy z ESP32 i MicroPython na maszynie hosta (Windows PowerShell).

1) Python i virtualenv
- Zainstaluj Python 3.8+ i `pip`.
- Tworzenie środowiska (zalecane):
```powershell
python -m venv my_env
.\my_env\Scripts\Activate.ps1
```
- Alternatywnie uruchom przygotowany skrypt: `.\scripts\setup_venv.ps1` (tworzy `my_env` i instaluje zależności z `requirements.txt`).

2) mpremote (rekomendowane)
- Służy do komunikacji z MicroPython: REPL, przesył plików, wykonywanie poleceń.
- Instalacja:
```powershell
pip install mpremote
```
- Przykłady:
```powershell
# przesłanie pliku
mpremote connect COM3 fs put main.py :/main.py
# otwarcie REPL
mpremote connect COM3 repl
```

3) esptool
- Użyteczne do flashowania firmware (bin).
- Instalacja:
```powershell
pip install esptool
```
- Przykład flashowania (po pobraniu firmware.bin):
```powershell
esptool.py --chip esp32 erase_flash
esptool.py --chip esp32 write_flash -z 0x1000 firmware.bin
```

4) alternatywy
- `ampy`, `rshell` — starsze narzędzia do przesyłania plików (opcjonalne).

5) uprawnienia i porty
- Na Windowsie używaj odpowiedniego portu COM (np. `COM3`) w poleceniach `mpremote` lub `esptool`.
- Sprawdź Menedżera urządzeń, by zidentyfikować numer portu.

6) Firmware
- Pobierz najnowsze, stabilne wydanie MicroPython dla ESP32 ze strony projektu MicroPython (wersja zgodna z Twoją płytką) i wgraj przez `esptool`.

Uwagi
- Ten dokument jest przewodnikiem minimalnym; rozszerzę go o dodatkowe wskazówki, skrypty i troubleshooting w kolejnych krokach.
