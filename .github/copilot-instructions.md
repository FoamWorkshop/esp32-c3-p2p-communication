# Copilot Instructions — ESP32 + MicroPython Workspace

Cel
- Ten plik opisuje stos technologiczny projektu oraz sposób pracy w trybie agentowym (workflow 3x3), którego będziemy przestrzegać.

Stack technologiczny
- **Platforma:** ESP32 (np. ESP32-WROOM-32)
- **Firmware:** MicroPython (polecane stabilne wydanie kompatybilne z ESP32)
- **Narzędzia hosta:**
  - `esptool` — do flashowania firmware (przydatne)
  - `mpremote` — rekomendowane do komunikacji z urządzeniem (REPL, transfer plików)
  - `rshell`/`ampy` — alternatywy (opcjonalne)
  - `pip`, `python` — środowisko do instalacji narzędzi
- **Edytor:** VS Code (zalecane), możliwe wtyczki: Pymakr, Python

Konwencje workspace
- Root projektu zawiera `README.md` i `copilot-instructions.md`.
- Skrypty dla hosta umieszczamy w `scripts/` (PowerShell na Windowsie).
- Pliki MicroPython (np. `main.py`) trafiają na urządzenie do katalogu root fs urządzenia.

Workflow agentowy — 3x3 (zasady)
- Przygotowanie: najpierw tworzę listę TODO (9 zadań). Użytkownik akceptuje lub zgłasza uwagi.
- Wykonanie w pętlach 3x3:
  1. Wybieram pierwsze 3 zadania z listy.
  2. Oznaczam jedno zadanie jako `in-progress` przed rozpoczęciem (narzędzie TODO list śledzi statusy).
  3. Wykonuję wszystkie 3 zadania (tworzę/edytuję pliki, skrypty itp.).
  4. Po wykonaniu oznaczam zadania jako `completed` i zwracam gotowe artefakty do ewaluacji użytkownika.
  5. Użytkownik akceptuje lub zgłasza uwagi.
  6. Jeśli zaakceptowane — planuję kolejne 3 zadania i powtarzam cykl. Jeśli są uwagi — nanoszę poprawki i ponownie proszę o ewaluację.

Zasady komunikacji i wysyłania zmian
- Zawsze aktualizuję TODO listę przez narzędzie `manage_todo_list` (statusy: `not-started`, `in-progress`, `completed`).
- Przed wykonaniem zmian informuję krótkim preambułem co zrobię (1–2 zdania).
- Po zestawie zmian (3–5 operacji lub >3 plików) wysyłam postęp i następne kroki.

Przykłady poleceń (PowerShell)
```powershell
# instalacja narzędzi
pip install esptool mpremote

# flash firmware (jeśli masz .bin)
esptool.py --chip esp32 erase_flash
esptool.py --chip esp32 write_flash -z 0x1000 firmware.bin

# przesyłanie pliku przy użyciu mpremote
mpremote connect COM3 fs put main.py :/main.py
mpremote connect COM3 repl
```

Uwagi do agenta (dla Copilota)
- Nie modyfikuj większej liczby niż 3 zadania na raz bez zgody użytkownika.
- Po każdym zestawie 3 zadań czekaj na ewaluację.
- Zachowuj prostotę w plikach startowych — rozszerzenia dodajemy w kolejnych cyklach.
