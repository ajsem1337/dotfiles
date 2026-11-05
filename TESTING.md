# Sprawdzenie kopii — 2026-11-05

- Migracja wykonana na działającym systemie: `libcanberra` i
  `libcanberra-gtk2-compat` zastąpione w jednej transakcji pacmana przez
  `libcanberra-gtk2 1:0.30+r2+gc0620e4-6` z AUR. Bez wymuszania zależności
  i nadpisywania plików. Recepta AUR: commit
  `361aa1014fc822f051afdcb9657c9af807aeb540`.
- `pacman -T libcanberra libcanberra.so=0-64 libcanberra-gtk.so=0-64
  libcanberra-gtk3.so=0-64`: brak niespełnionych zależności.
- `pacman -Dk`: `No database errors have been found!`. Stary, niepakietowy
  plik `CACHY_UPDATE_NOTICE` przeniesiono z katalogu bazy do
  `/var/backups/dotfiles/CACHY_UPDATE_NOTICE-20261105`.
- `pacman -Qkk libcanberra-gtk2`: 73 pliki, 0 zmienionych.
- `ldd -r`: 10 bibliotek, backendów i modułów; brak brakujących bibliotek
  oraz nierozwiązanych symboli.
- `python scripts/check-gtk2.py`: moduły GTK2 i GTK3 załadowane, oba konteksty
  audio zwróciły `0`. Bez odtwarzania dźwięku.
- Kitty, Fish, Fastfetch, Micro, EasyEffects i ScopeBuddy są zainstalowane;
  listy odtwarzania zawierają wszystkie sześć programów.
- Micro użytkownika i roota: motyw `simple`, `syntax: true`. Próba w PTY
  potwierdziła start i zamknięcie edytora, kolory składni oraz domyślne tło
  terminala. Przezroczystość kompozytora zależy od ustawień Kitty.
- ScopeBuddy GUI uruchomił się z izolowanym katalogiem konfiguracji i
  platformą Qt `offscreen`. Kopia zawiera kod, zasoby, licencję i profile
  ScopeBuddy, do których odwołuje się zachowany launcher.
- Pełne odtworzenie do pustego katalogu: 47 140 zmienionych plików;
  ponowne odtworzenie: 0 zmian. Sprawdzono też payload GUI i symlink AppID.
- Pięć testów jednostkowych zakończonych powodzeniem, w tym zachowanie
  innych ustawień Micro roota, kopia i idempotencja oraz ochrona plików
  przed zastąpieniem przy błędnym JSON.
- `verify.py`, sprawdzenie składni skryptów i `git diff --check`: OK.
- Po weryfikacji usunięto lokalną receptę, źródłowe archiwum i artefakty
  compat. Odinstalowano cztery pakiety doinstalowane wyłącznie do budowy:
  `gtk-doc`, `docbook-xml`, `docbook-xsl`, `glib2-docs`.

Lista wersji zachowuje historyczny stan pozostałych pakietów; wpisy dotyczące
tej migracji i sześciu wymienionych programów zaktualizowano 2026-11-05.
Nie przeprowadzano pełnej instalacji pakietów na świeżej maszynie.

## Wcześniejsze kontrole — 2026-10-30

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
