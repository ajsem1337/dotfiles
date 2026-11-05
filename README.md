# CachyOS GNOME — spójny wygląd i osobny profil systemowy

Bazą jest gotowa instalacja **CachyOS GNOME**. Repo ma dwa zakresy:

| Zakres | Co odtwarza |
| --- | --- |
| Wygląd — `--all` | GTK2/3/4, libadwaita, Qt5/6, Kvantum, ikony, kursor, fonty, tapetę, GNOME i rozszerzenia, Kitty/Fish/Fastfetch/Micro, Vicinae i Equicord System24 |
| System — osobne `--system` | Zapora, sieć, scheduler, dźwięki GTK, PipeWire, całe EasyEffects z presetami/autoloadem, ScopeBuddy i tablet |

Nie zapisujemy pełnych spisów pakietów ani wersji. Listy w `packages/` są
ręcznym przepisem na zależności tych konfiguracji. Partycje, rozruch, sterowniki,
konta i dostęp do internetu konfiguruje instalator systemu.

## Odtworzenie wyglądu

Zamknij aplikacje, których ustawienia zamierzasz odtworzyć.
Uruchom jako użytkownik zalogowany do lokalnej sesji GNOME:

```bash
cd ~/dotfiles
./restore.sh --all --plan
./restore.sh --all
```

Skrypt instaluje pakiety z `packages/repo.txt` i `packages/aur.txt`, kopiuje
konfigurację oraz zasoby, ustawia GNOME i wygląd Micro roota. Sam wywołuje
`sudo` w potrzebnych miejscach. Nie uruchamiaj całego skryptu jako root.
Przejrzyj pytania pacmana i recepty AUR, a na końcu wyloguj się i zaloguj ponownie.

Osobne kroki:

```bash
./restore.sh --packages      # zależności wyglądu
./restore.sh --home          # pliki, zasoby i motywy aplikacji
./restore.sh --gnome         # ustawienia GNOME, rozszerzenia i skróty
./restore.sh --root-micro    # motyw simple i składnia w sudo micro
```

`--all` nie stosuje ustawień zapory, sieci, schedulera ani audio. Nie importuje
starego `pacman.conf` i nie dodaje automatycznie Omarchy. Pacman używa źródeł
nowej instalacji i dobiera zależności wskazanych pakietów.

## Theme — co jest gdzie

Katalog `home/` odpowiada katalogowi domowemu użytkownika: np.
`home/.config/kitty/` trafia do `~/.config/kitty/`.
Duże zestawy zasobów są w `assets/appearance.tar.gz`; poniższe ścieżki
zaczynające się od `~/` wskazują ich miejsce po odtworzeniu.

| Element | Zapisany wygląd | Gdzie w repo |
| --- | --- | --- |
| GTK2/GTK3 | Catppuccin-Pink-Dark, silnik Murrine | `assets/appearance.tar.gz` → `~/.themes/Catppuccin-Pink-Dark/`; wybór motywu w `gnome/settings.json` |
| GTK4 / libadwaita | Kolory i akcenty spójne z Mocha Pink | [`home/.config/gtk-4.0/gtk.css`](home/.config/gtk-4.0/gtk.css) |
| Qt5 / Qt6 | Integracja z GTK3: fonty, ikony i styl Kvantum | [`home/.config/environment.d/10-qt.conf`](home/.config/environment.d/10-qt.conf), [`home/.config/qt5ct/`](home/.config/qt5ct/), [`home/.config/qt6ct/`](home/.config/qt6ct/) |
| Kvantum | Catppuccin Mocha Pink: motyw SVG, kolory i ustawienia | [`home/.config/Kvantum/`](home/.config/Kvantum/) |
| GNOME Shell | Catppuccin-Pink-Dark, różowy akcent, ciemny tryb | Motyw w `assets/appearance.tar.gz`; wybór, panel i ustawienia w [`gnome/settings.json`](gnome/settings.json) |
| Ikony | Tela Pink — wariant ciemny, jasny i podstawowy | `assets/appearance.tar.gz` → `~/.local/share/icons/Tela-pink*` |
| Kursor | MyCursor-GNOME51, rozmiar 40 | Archiwum → `~/.local/share/icons/MyCursor-GNOME51/`; [`home/.config/environment.d/40-cursor.conf`](home/.config/environment.d/40-cursor.conf) i `gnome/settings.json` |
| Fonty | Adwaita Sans/Mono, Maple Mono NF w Kitty, FiraCode Nerd Font w Vicinae | Pakiety w `packages/`; [`home/.config/fontconfig/`](home/.config/fontconfig/), `gnome/settings.json` i konfiguracje aplikacji |
| Tapeta | Zapisany obraz i wybór tła GNOME | [`home/.local/share/backgrounds/`](home/.local/share/backgrounds/) i `gnome/settings.json` |
| Kitty | Catppuccin Mocha, Maple Mono NF, przezroczystość, karty i skróty | [`home/.config/kitty/kitty.conf`](home/.config/kitty/kitty.conf), [`current-theme.conf`](home/.config/kitty/current-theme.conf) |
| Fish | Prompt, kolory składni i skróty powłoki | [`home/.config/fish/`](home/.config/fish/) — `config.fish`, `functions/`, `conf.d/99-dotfiles-colors.fish` |
| Fastfetch | Układ informacji i obrazek | [`home/.config/fastfetch/`](home/.config/fastfetch/) |
| Micro | Motyw `simple`, tło terminala i podświetlanie składni | [`home/.config/micro/`](home/.config/micro/); odpowiednik dla `sudo micro`: [`scripts/configure-root-micro.py`](scripts/configure-root-micro.py) |
| Vicinae | Catppuccin Mocha Pink, FiraCode Nerd Font, launcher i schowek | [`home/.config/vicinae/`](home/.config/vicinae/), dwa launchery w `home/.local/share/applications/`, skróty i rozszerzenie w `gnome/` |
| Equicord | System24 Catppuccin Mocha, różowy akcent | [`home/.config/Equicord/themes/`](home/.config/Equicord/themes/), wybór motywu w [`themes/apps/equicord.json`](themes/apps/equicord.json) |
| Flatpak | Dostęp aplikacji do tych samych motywów GTK, ikon i kursora | Uprawnienia użytkownika stosowane przez [`scripts/restore.py`](scripts/restore.py) |
| Pomocnicze narzędzia wyglądu | Profil rozmycia GNOME i ustawianie ciemnego wyglądu Wine | [`home/.local/bin/`](home/.local/bin/) |

`QT_QPA_PLATFORMTHEME=gtk3` pobiera ustawienia integracji z GNOME,
a `QT_STYLE_OVERRIDE=kvantum` wybiera styl kontrolek. Konfiguracje qt5ct/qt6ct
są zapisane jako uzupełnienie; nie są obecnie wybranym pluginem integracji.
Dekoracje Qt na Waylandzie mają zależności w `packages/aur.txt`.

Wygląd Equicorda jest **scalany** z plikiem ustawień. Dane kont, wtyczki,
proxy i pozostałe ustawienia pozostają zachowane. Poprzedni plik trafia do
kopii przed zmianą. Pakiet `equicord-installer-bin` dostarcza instalator;
wstrzyknięcie do wybranego Discorda wykonaj w jego GUI. System24 importuje
arkusz upstream przez HTTPS, więc do jego pobrania potrzebna jest sieć.

## Mapa pozostałych katalogów

| Katalog / plik | Zawartość |
| --- | --- |
| `gnome/` | Ustawienia wyglądu, rozszerzeń i skrótów; `extensions.json` opisuje wersje i stan włączenia |
| `assets/` | Archiwum motywów, ikon, kursora i kodu rozszerzeń; `manifest.json` opisuje jego zasoby i datę eksportu |
| `packages/repo.txt`, `packages/aur.txt` | Zależności wyglądu i konfiguracji aplikacji |
| `packages/system.txt`, `packages/system-aur.txt` | Zależności opcjonalnego profilu systemowego |
| `system/home/` | EasyEffects z presetami i autoloadem, PipeWire, ScopeBuddy, tablet i powiązane launchery |
| `system/gnome/settings.json` | Dźwięki GNOME i ustawienia urządzeń wejściowych |
| `system/etc/` | Zapora, sieć, scheduler, reguły urządzeń i usługi |
| `system/reference/` | Materiały pomocnicze dla odtwarzania konfiguracji systemowej |
| `scripts/`, `restore.sh` | Eksport, odtwarzanie, kopie i kontrole |
| `snapshot.json`, `checksums.json` | Data i zakres eksportu oraz sumy kontrolne plików |
| `tests/`, `TESTING.md` | Testy odtwarzania i wyniki weryfikacji |

## Rozszerzenia GNOME, tiling i skróty

`gnome/extensions.json` opisuje obecne rozszerzenia, wersje i stan włączenia.
Eksport z 2026-11-05 zawiera 11 rozszerzeń, w tym Tiling Shell 18.0
i Rounded Window Corners Native 51.0. Pięć starych wpisów, których plików nie ma w systemie, pominięto w liście do odtworzenia.

| Rozszerzenie | Rola |
| --- | --- |
| User Themes | Wczytuje motyw GNOME Shell |
| Logo Menu | Menu pod ikoną na górnym panelu |
| AppIndicator | Ikony aplikacji w panelu |
| Fullscreen Avoider | Zachowanie okien względem pełnego ekranu |
| Alphabetical App Grid | Alfabetyczny układ siatki aplikacji |
| Weather O'Clock | Pogoda przy zegarze |
| Blur my Shell | Rozmycie panelu, widoków i okien |
| Vicinae | Integracja launchera z GNOME |
| Quick Settings Audio Panel | Panel urządzeń i głośności w szybkich ustawieniach |
| Tiling Shell | Układy kafelkowania, autotiling i skróty okien |
| Rounded Window Corners Native | Narożniki, obrys i cień okien zgodne z libadwaitą |

Rounded Window Corners Native nie ma własnego schematu ustawień ani skrótów.
Czyta wygląd z libadwaity i `~/.config/gtk-4.0/gtk.css`, więc jest odtwarzane
razem z kodem rozszerzenia i istniejącą konfiguracją GTK4. Wymaga GNOME 51.

Zapisujemy bieżące układy tilingu, autotiling, odstępy, wygląd okien i skróty.
Tiling Shell przejmuje **Super + strzałki**. Odpowiedniki GNOME są wyłączone,
a rozszerzenie zachowuje własny zapis ustawień do przywrócenia po wyłączeniu.
Ustawienia rozszerzeń i skróty GNOME są odtwarzane przed listą włączenia rozszerzeń.

```bash
python scripts/check-keybindings.py          # sprawdź zapisany profil
python scripts/check-keybindings.py --live   # sprawdź bieżącą sesję
```

Kontrola porównuje skróty GNOME, włączonych rozszerzeń i własnych poleceń,
rozpoznaje aliasy Control/Ctrl/Primary oraz zastępowanie skrótów multimedialnych.
`--gnome` wykonuje ją przed zmianami i zatrzymuje się przy wykryciu kolizji.
Eksport pomija historię konsoli, wartości kluczy z danymi prywatnymi i cache
pozycji wszystkich aplikacji (`app-picker-layout`). Siatkę porządkuje Alphabetical App Grid.

## Po co zostały trzy pliki .desktop

- `vicinae-toggle.desktop` i `vicinae-clipboard.desktop` są ukrytymi poleceniami
  dla skrótów GNOME; nie dublują pozycji w menu.
- `micro.desktop` otwiera Micro w Kitty po wybraniu pliku z menedżera plików.

Usunięto kopie launcherów Code, przeglądarek, poczty i narzędzi systemowych,
cache menu, skojarzenia MIME oraz niezwiązany z wyglądem autostart Nextcloud.
Launcher lokalnego GUI ScopeBuddy znajduje się w `system/home/` razem z GUI.
Standardowe pliki `.bashrc` i `.bash_profile` nie są częścią tego profilu.

## Zasoby wyglądu i aktualność archiwum

`assets/appearance.tar.gz` zawiera wyłącznie motyw GTK, ikony, kursor i kod
lokalnych rozszerzeń GNOME. To nie jest spakowane repozytorium dotfiles.
Zastąpiło stare `desktop.tar.gz` i zostało ponownie zebrane z działającej
konfiguracji. `assets/manifest.json` podaje datę, katalogi i liczbę plików.

Archiwum ogranicza liczbę drobnych plików ikon w Git. Ustawienia rozszerzeń
są osobno w czytelnym `gnome/settings.json`, a konfiguracje aplikacji w `home/`.

## Osobny profil systemowy i audio

Po przejrzeniu `system/`, `packages/system.txt` oraz `packages/system-aur.txt`:

```bash
./restore.sh --packages --system --plan
./restore.sh --packages --system
```

Ten krok instaluje tylko zależności profilu systemowego, odtwarza pliki z
`system/home/`, ustawienia dźwięku i urządzeń z `system/gnome/settings.json`,
a następnie stosuje zapisane pliki `/etc`, zaporę i usługi. Wykonuj go lokalnie.
Presety audio, autoload, geometria tabletu i rozdzielczości ScopeBuddy mogą
wymagać dopasowania po zmianie sprzętu. Oba zakresy naraz odtworzysz przez
`./restore.sh --all --system`.

`game-performance` pochodzi z bazowego CachyOS. Nie kopiujemy go ani nie
instalujemy ponownie `cachyos-settings`. Profile ScopeBuddy używają istniejącego
`/usr/bin/game-performance`; własny wrapper powersave usunięto z przepisu.

Dźwięki GTK2/GTK3 zapewnia `libcanberra-gtk2` z AUR, który zastępuje systemowe
`libcanberra`. Jest wyłącznie na liście systemowej. Kontrola modułów w sesji GNOME:

```bash
pacman -T libcanberra libcanberra.so=0-64 libcanberra-gtk.so=0-64 libcanberra-gtk3.so=0-64
pacman -Dk
pacman -Qkk libcanberra-gtk2
python scripts/check-gtk2.py
```

## Kopie i sprawdzanie

Zmieniane pliki użytkownika trafiają do `~/.local/state/dotfiles-backups/`,
a pliki systemowe do `/var/backups/dotfiles-*`. Drugie odtworzenie pomija
identyczne pliki. Stan GNOME można przywrócić z zapisanej kopii:

```bash
python scripts/revert-gnome.py /ścieżka/do/gnome-before.json
```

Próba plików wyglądu w pustym katalogu, bez zmieniania sesji i pakietów:

```bash
./restore.sh --home --target-home /tmp/proba-dotfiles
```

Aktualizacja na własnym pulpicie:

```bash
python scripts/capture.py
python scripts/check-keybindings.py
python scripts/seal.py
python scripts/verify.py
python -m unittest discover -s tests -v
```

`capture.py` zbiera wyłącznie wskazane pliki i ustawienia, odświeża archiwum
oraz listę rozszerzeń. Listy pakietów utrzymujemy ręcznie; każdy pakiet ma
mieć rolę w wyglądzie albo opcjonalnym profilu systemowym. Przed wysłaniem
obejrzyj `git diff`.

Hasła, klucze, konta, keyringi, profile przeglądarek, historia, gry, Wine,
dokumenty i instalatory wymagają oddzielnej kopii. Kopię tego repo również
przenieś poza dysk przeznaczony do formatowania.

Prywatne repozytorium: [ajsem1337/dotfiles](https://github.com/ajsem1337/dotfiles).
