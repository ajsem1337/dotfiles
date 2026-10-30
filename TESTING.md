# Sprawdzenie kopii — 2026-10-30

- GTK2: prawdziwy moduł został załadowany do procesu GTK2, a
  `ca_context_open()` zwróciło 0. Nie odtwarzano dźwięku. Brak komunikatu
  `Failed to load module` i brak nierozwiązanych symboli.
- Integralność paczek: systemowy libcanberra — 64 pliki, 0 zmienionych;
  libcanberra-gtk2-compat — 10 plików, 0 zmienionych.
- Pełne odtworzenie plików do pustego katalogu innego użytkownika:
  ponad 47 tys. plików. Zweryfikowano motywy, kursor, symlinki, PipeWire,
  presety oraz podmianę ścieżki katalogu domowego i daty instalacji Fastfetch.
- Drugie odtworzenie tego samego zestawu: 0 zmienionych plików.
- 623 ustawienia GNOME sprawdzono rzeczywistym `gsettings set` na backendzie
  pamięciowym — bez zmieniania ustawień działającej sesji; 0 błędów.
- Cztery testy: przenośność i kopie, idempotencja, ochrona przed wyjściem
  archiwum/symlinków poza katalog docelowy, stabilne pierwszeństwo repozytoriów.
- Sprawdzono składnię skryptów i wzorce sekretów oraz sumy SHA-256 plików kopii.

Nie przeprowadzano formatu ani pełnej instalacji pakietów na świeżej maszynie.
Etap uprzywilejowany wymaga lokalnej sesji CachyOS GNOME i jest oddzielony
od sprawdzonego odtwarzania plików. Jego funkcję układania repozytoriów
sprawdzono testem; pozostałe operacje są jawne w scripts/system.py.
