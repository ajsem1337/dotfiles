# Sprawdzenie konfiguracji — 2026-11-05

- Przepis wyglądu: 28 pakietów repo i 7 AUR. Opcjonalny system: 23 repo
  i 3 AUR. `pacman -T` potwierdził obecność zależności, a nazwy repo są
  dostępne w skonfigurowanych źródłach. Nie instalowano pełnego zestawu
  na świeżej maszynie.
- Audio, wszystkie zapisane pliki EasyEffects/PipeWire, dźwięki GNOME,
  ScopeBuddy i tablet przeniesiono do `system/`. `--all` nie wywołuje
  odtwarzania tej części; test sprawdza również rozdział pakietów AUR.
- Z `home/` usunięto standardowe pliki Bash, puste Millennium Quick CSS,
  skojarzenia MIME, cache i launchery niezwiązanych programów. Zostały
  trzy uzasadnione pliki desktop: dwa dla skrótów Vicinae i Micro w Kitty.
- `assets/appearance.tar.gz` zebrano ponownie z działającej konfiguracji.
  `assets/manifest.json` zapisuje datę i sześć grup zasobów. Stare
  `desktop.tar.gz` usunięto. W nowym archiwum nie ma repozytorium dotfiles.
- GNOME: 583 ustawienia wyglądu/skróty i 43 ustawienia systemowe. Manifest
  obejmuje 10 obecnych rozszerzeń, w tym Tiling Shell 18.0; usunięto z eksportu
  5 wpisów bez zainstalowanych plików. Bieżące układy i autotiling są zapisane.
- `check-keybindings.py` oraz `--live`: 148 efektywnych skrótów, brak kolizji.
  Test wykrywa równoważność Ctrl/Control/Primary i respektuje zastąpienie
  domyślnych skrótów multimedialnych. Super + strzałki należą do Tiling Shell;
  odpowiedniki GNOME są wyłączone, a stan przywracania rozszerzenia zachowany.
- Ustawienia rozszerzeń i klawiszy są stosowane przed włączeniem rozszerzeń.
- Vicinae zachowuje konfigurację, motyw, font i dwa skróty; zależność
  `ttf-firacode-nerd` dopisano na podstawie ustawionego fontu.
- Equicord ma zapisany i włączony System24. Test scalania JSON potwierdza
  zachowanie konta, ustawień wtyczek i zagnieżdżonych opcji, utworzenie kopii,
  idempotencję i zatrzymanie bez nadpisania przy błędnym JSON.
- Steam: GNOME Mocha Pink to lokalny arkusz 5695 B. `check-steam-theme.py`
  potwierdził brak skryptów/importów/rozmycia oraz obecność 30 klas układu
  w plikach zainstalowanego klienta. Makietę wyrenderowano i obejrzano
  w headless Floorp. To nie jest zrzut klienta ani benchmark płynności.
- Motyw Steama zastosowano po potwierdzeniu zamknięcia klienta, z kopią
  poprzedniej konfiguracji Millennium. Pozostałe ustawienia zostały zachowane.
  Przy odtwarzaniu świeżej instalacji powstają standardowe linki bootstrapu
  do bibliotek z pakietu AUR, bez kopiowania instalacji Steama do repo.
- Dziesięć testów jednostkowych: OK. Sprawdzone również przenośność,
  ochrona przed wyjściem archiwum/symlinków poza katalog i rozdział zakresów.
- Pełne odtworzenie wyglądu i osobne odtworzenie systemowych plików użytkownika
  do pustych katalogów: odpowiednio 47 083 i 63 pliki. Ponowne uruchomienia: 0 zmian.
- Składnia Pythona, `verify.py` i kontrola diff: OK.

Wcześniejsza migracja libcanberra z tego samego dnia pozostaje zweryfikowana:
73 pliki paczki `libcanberra-gtk2`, 0 zmienionych; komplet SONAME, brak błędów
bazy pacmana; GTK2 i GTK3 ładują moduły, oba konteksty audio zwracają 0.
Nie uruchamiano ponownie ustawień zapory ani schedulera podczas tej korekty.

Korekta płaskiego wyglądu Steama: wyzerowane promienie rogów, usunięta
wewnętrzna ramka oraz jednolite tło Mocha bibliotek, półek i panelu bocznego.
Render sprawdza również nadpisanie gradientów z oryginalnego CSS klienta
i zachowanie grafik na kartach.

Port stylistyki System24 do Steama:

- Nowy wariant System24-Mocha-Pink jest domyślny w zapisanym wyborze Millennium;
  GNOME Mocha Pink pozostaje alternatywą.
- Font DM Mono Light/Regular/Medium jest dołączony z oficjalnego Google Fonts,
  razem z OFL 1.1; pliki binarne są objęte sumami kontrolnymi.
- Kontrola klas obejmuje oba motywy. System24 używa lokalnego CSS, bez JS,
  importów sieciowych, rozmycia i własnych animacji.
- Render sprawdza monospace, etykiety ASCII, obramowania i zachowanie grafik;
  nie stanowi pełnego testu wszystkich ekranów klienta ani benchmarku.

System24: arkusz 9074 B, 32 klasy obecne w plikach klienta. Render potwierdził
DM Mono, etykiety ASCII, ramki, proste krawędzie, brak gradientów tła oraz
zachowanie grafik. Wariant zainstalowano i wybrano przy zamkniętym Steamie.
