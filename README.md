# CachyOS GNOME — spójny wygląd i osobny profil systemowy

Bazą jest gotowa instalacja **CachyOS GNOME**. Repo ma dwa zakresy:

| Zakres | Co odtwarza |
| --- | --- |
| Wygląd — `--all` | GTK2/3/4, libadwaita, Qt5/6, Kvantum, ikony, kursor, fonty, tapetę, GNOME i rozszerzenia, Kitty/Fish/Fastfetch/Micro, Vicinae, Equicord System24 oraz Steam Millennium |
| System — osobne `--system` | Zapora, sieć, scheduler, dźwięki GTK, PipeWire, całe EasyEffects z presetami/autoloadem, ScopeBuddy i tablet |

Nie zapisujemy pełnych spisów pakietów ani wersji. Listy w `packages/` są
ręcznym przepisem na zależności tych konfiguracji. Partycje, rozruch, sterowniki,
konta i dostęp do internetu konfiguruje instalator systemu.

## Odtworzenie wyglądu

Zamknij Steama i aplikacje, których ustawienia zamierzasz odtworzyć.
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

## Co składa się na wygląd

- **GTK2/3:** Catppuccin-Pink-Dark i silnik Murrine.
- **GTK4/libadwaita:** mała nakładka CSS z kolorami i akcentami.
- **Qt5/Qt6:** integracja GTK3, Kvantum Mocha Pink, konfiguracje qt5ct/qt6ct
  oraz dekoracje Qt na Waylandzie.
- **Zasoby GNOME:** ikony Tela Pink, kursor MyCursor-GNOME51, tapeta,
  Adwaita Sans/Mono i ustawienia fontconfig.
- **Terminal:** Kitty z Maple Mono NF, Fish z promptem, Fastfetch z obrazkiem
  oraz Micro z tłem terminala i kolorowaniem składni.
- **Vicinae:** motyw Mocha Pink, konfiguracja launchera, FiraCode Nerd Font
  i skróty wywołujące launcher oraz schowek.
- **Equicord:** System24 Catppuccin Mocha z różowym akcentem. Zapisujemy także
  wybór włączonego motywu. Pakiet `equicord-installer-bin` dostarcza instalator;
  wstrzyknięcie do wybranego Discorda wykonaj w jego GUI. System24 importuje
  arkusz upstream przez HTTPS, więc do jego pobrania potrzebna jest sieć.
- **Steam:** pakiet Steam, Millennium i lokalny port stylistyki System24 Mocha Pink.

Wygląd Equicorda i Millennium jest **scalany** z plikami ustawień. Dane kont,
wtyczki, proxy i pozostałe ustawienia pozostają zachowane. Poprzedni plik
trafia do kopii przed zmianą.

## Steam — System24 Mocha Pink

Domyślny motyw w `themes/steam/System24-Mocha-Pink/` adaptuje stylistykę
[system24 refact0ra](https://github.com/refact0r/system24) do Steama:
monospace DM Mono, ramki paneli, etykiety ASCII, tekstowa nawigacja i paleta
Mocha Pink jak w Equicordzie. Jest to niezależna, nieoficjalna adaptacja
selektorów i układu. Arkusz Discorda nie jest wstrzykiwany do Steama.

DM Mono jest dołączony lokalnie w `home/.local/share/fonts/DMMono/`,
z licencją OFL i informacją o źródle. Odtwarzanie aktualizuje cache fontconfig.
Motyw nie wymaga pobierania CSS ani fontów podczas działania klienta.
Poprzedni GNOME Mocha Pink pozostaje do wyboru jako prostsza alternatywa.
Oba warianty mają proste krawędzie i jednolite tła; bez skryptów, rozmycia
oraz własnych animacji. Okładki gier i grafiki aktualności zostają widoczne.

Nie ładuje Adwaita-for-Steam. Nie kopiuje katalogu instalacji Steama, bibliotek
gier ani danych konta. Millennium pochodzi z AUR; odtwarzanie tworzy też jego
dwa standardowe linki bootstrapu w katalogach użytkownika, jeżeli biblioteki
pakietu są zainstalowane. Dzięki temu nie zależy od uruchomienia Steama przed
instalowaniem Millennium.

Steam musi być zamknięty podczas `--home`; skrypt sprawdza to przed zmianami.
Po aktualizacji klienta można sprawdzić klasy używane przez układ:

```bash
python scripts/check-steam-theme.py
```

Motyw ma sprawdzoną strukturę, obecność klas w zainstalowanym kliencie i render
na reprezentatywnej makiecie. Nie jest to benchmark ani pełny test wszystkich
widoków działającego Steama. Płynność biblioteki, sklepu i czatu trzeba ocenić
w kliencie po uruchomieniu nowego motywu.

## Rozszerzenia GNOME, tiling i skróty

`gnome/extensions.json` opisuje obecne rozszerzenia, wersje i stan włączenia.
Eksport z 2026-11-05 zawiera 10 rozszerzeń, w tym Tiling Shell 18.0. Pięć starych
wpisów, których plików nie ma w systemie, pominięto w liście do odtworzenia.

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
Eksport nie zawiera historii konsoli ani wartości kluczy z danymi prywatnymi.

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
są osobno w czytelnym `gnome/settings.json`, a źródła motywu Steama w `themes/`.

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
python scripts/check-steam-theme.py
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
