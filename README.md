# CachyOS GNOME — przepis na mój pulpit

Odtwarza Catppuccin Mocha Pink, ustawienia GNOME i skonfigurowane aplikacje
na gotowej instalacji **CachyOS GNOME**. Pakiety są dobrane do zapisanych
ustawień. Nie ma tu spisu wszystkich pakietów ani ich wersji z komputera.

## Po świeżej instalacji CachyOS GNOME

1. Skonfiguruj użytkownika, dyski, rozruch, sterowniki i internet w instalatorze.
2. Pobierz to prywatne repozytorium lub przenieś jego kopię. Otwórz terminal
   jako zwykły użytkownik w lokalnej sesji GNOME.
3. Uruchom:

   ```bash
   cd ~/dotfiles
   ./restore.sh --plan
   ./restore.sh --all
   ```

4. Przejrzyj pytania pacmana i recepty AUR. Wyloguj się i zaloguj ponownie.

`--all` instaluje zależności konfiguracji, kopiuje pliki, ustawia GNOME
oraz motyw Micro dla roota. Skrypt sam wywołuje `sudo` w potrzebnych miejscach;
nie uruchamiaj całego `restore.sh` jako root. Potrzebuje internetu do repo i AUR.

## Co jest potrzebne i po co

| Element konfiguracji | Pakiety i zasoby |
| --- | --- |
| GTK2/3/4 i libadwaita | `gtk2`, `gtk3`, `gtk4`, `libadwaita`, `gtk-engine-murrine`, `libcanberra-gtk2` |
| Qt5/Qt6 | `qt5-base`, `qt6-base`, `qt6-wayland`, `qt5ct`, `qt6ct`, `kvantum`, `kvantum-qt5`, dekoracje Waylanda z listy AUR |
| Motyw, ikony, kursor i fonty | Catppuccin, Tela Pink i MyCursor w `assets/desktop.tar.gz`; `adwaita-fonts` i `maplemono-nf` |
| GNOME i rozszerzenia | Gotowa sesja CachyOS GNOME, `gnome-shell-extensions`, `libgweather-4`; lokalne rozszerzenia są w archiwum |
| Terminal, powłoka i edytor | `kitty`, `fish`, `fastfetch`, `micro`, `bat`; motywy i ustawienia są w `home/` |
| Audio | PipeWire, WirePlumber, `easyeffects`, `calf`, `lsp-plugins-lv2`, `deepfilternet-plus-bin`; presety i autoload w `home/` |
| ScopeBuddy i lokalne GUI | `scopebuddy`, `gamescope`, `pyside6`; zapisane profile oraz źródła GUI z licencją LGPL-3.0-only |
| Pozostałe zapisane ustawienia | `vicinae-bin`, `opentabletdriver`, `flatpak`; profil zasilania używa `power-profiles-daemon` i `game-performance` z `cachyos-settings` |
| Uruchomienie odtwarzania | Python, PyGObject, `desktop-file-utils`, Git, `base-devel` i `paru` |

Dokładny przepis, z komentarzami do każdej grupy, znajduje się w:

- [`packages/repo.txt`](packages/repo.txt) — pakiety z repozytoriów;
- [`packages/aur.txt`](packages/aur.txt) — pakiety budowane z AUR.

Pacman dobiera ich zależności. Nie dopisujemy ręcznie wszystkich bibliotek
z systemu. Nie odtwarzamy listy kerneli, firmware, sterowników, przeglądarek,
gier, pakietów deweloperskich ani wszystkich aplikacji AUR i Flatpak.
`pacman -Syu` zachowuje spójność wersji podczas instalowania wskazanych pakietów.

Przepis używa repozytoriów skonfigurowanych na nowej instalacji CachyOS.
Nie importuje starego `pacman.conf` i nie dodaje automatycznie Omarchy.
Listy są utrzymywane ręcznie; `capture.py` zbiera konfigurację i nie zastępuje
ich wynikiem `pacman -Q`.

Fish używa `bat`, a pozostałe opcjonalne dodatki w jego pliku sprawdza przez
`type -q`. Nie trzeba instalować `eza`, `zoxide` ani `atuin`, aby odtworzyć
obecnie działający profil — nie były zainstalowane podczas tego sprawdzenia.

## Poszczególne kroki

```bash
./restore.sh --packages      # tylko pakiety z przepisu repo/AUR
./restore.sh --home          # pliki, motywy, presety i rozszerzenia
./restore.sh --gnome         # ustawienia GNOME w bieżącej sesji
./restore.sh --root-micro    # wygląd i składnia w sudo micro
```

Przed nadpisaniem pliki użytkownika trafiają do
`~/.local/state/dotfiles-backups/`. Powtórne `--home` pomija pliki o tej samej
treści i uprawnieniach. `--gnome` zapisuje poprzednie wartości w
`gnome-before.json` w katalogu kopii. Można je przywrócić przez:

```bash
python scripts/revert-gnome.py /ścieżka/do/gnome-before.json
```

Profil ustawia Fish jako powłokę logowania; `chsh` może poprosić o hasło.
Presety audio, nazwy urządzeń, geometria tabletu i rozdzielczości w profilach
ScopeBuddy mogą wymagać dopasowania do nowego sprzętu.

Bezpieczna próba odtworzenia plików do pustego katalogu:

```bash
./restore.sh --home --target-home /tmp/proba-dotfiles
```

## Opcjonalne ustawienia systemowe

Dawne ustawienia nftables, mDNS, sysctl, udev i schedulera pozostają osobnym
krokiem. **`--all` ich nie stosuje i nie instaluje ich pakietów.** Jeśli chcesz
je również odtworzyć, przejrzyj `system/` i [`packages/system.txt`](packages/system.txt),
a potem uruchom lokalnie:

```bash
./restore.sh --packages --system
```

Ten krok zmienia zaporę i usługi, tworząc kopie w `/var/backups/dotfiles-*`.
Nie instaluje kernela ani sterowników. Zapisane `pacman.conf` i `nsswitch.conf`
są materiałem referencyjnym, nie plikami do podmiany w całości.

## GTK, Qt i dźwięki

GTK4/libadwaita dostają kolory i akcenty przez małą nakładkę CSS.
GTK2/3 korzystają z dołączonego Catppuccin, a Qt Widgets z Kvantum.
`QT_QPA_PLATFORMTHEME=gtk3` zapewnia integrację Qt z GNOME;
`qt5ct` i `qt6ct` zachowujemy razem z ich konfiguracją.

[libcanberra-gtk2 z AUR](https://aur.archlinux.org/packages/libcanberra-gtk2)
dostarcza rdzeń, backendy, nagłówki oraz moduły GTK2 i GTK3. Zastępuje
systemowe `libcanberra` i dawny lokalny `libcanberra-gtk2-compat`.
Nie instaluj ich równolegle. Ręczna instalacja lub migracja:

```bash
paru -S --needed --aur libcanberra-gtk2
pacman -T libcanberra libcanberra.so=0-64 libcanberra-gtk.so=0-64 libcanberra-gtk3.so=0-64
pacman -Dk
pacman -Qkk libcanberra-gtk2
python scripts/check-gtk2.py
```

Zaakceptuj zastąpienie starych pakietów w transakcji pacmana. Test GTK wymaga
sesji graficznej; ładuje oba moduły i otwiera kontekst audio bez grania dźwięku.

## Micro, również przez sudo

Motyw `simple` używa tła terminala i koloruje składnię. W Kitty zachowuje
przezroczystość z `background_opacity`. Root ma osobną konfigurację, dlatego
`--all` i `--root-micro` ustawiają mu ten sam wbudowany motyw oraz `syntax: true`.
Można też uruchomić bezpośrednio:

```bash
sudo python scripts/configure-root-micro.py
```

Skrypt zachowuje inne ustawienia roota i kopię zmienianego pliku w
`/var/backups/dotfiles/`. Nie uruchamia wtyczek użytkownika jako root.

## Ustawienia pozostałych aplikacji

Zapisane CSS Equicorda i Millennium, skróty menu, skojarzenia plików oraz
autostart Nextcloud są dodatkami dla aplikacji, które zainstalujesz osobno.
Nie powodują instalacji Discorda, Steama, Nextcloud, przeglądarek ani edytorów.
Skróty i skojarzenia zaczną działać po zainstalowaniu odpowiednich programów.
Lokalny [scopebuddy-gui](https://github.com/rfrench3/scopebuddy-gui) ma dołączone
źródła i licencję, więc jego zapisany launcher ma komplet plików do startu.

Kopie kont, haseł, tokenów, SSH/GPG/AWS/OCI, keyringów, profili przeglądarek,
historii, gier, Wine i dokumentów trzeba wykonać osobno. To samo dotyczy
AppImage i ręcznie pobranych instalatorów Flatpak.
Nie kopiujemy `fstab`, UUID, machine-id, bootloadera ani list mirrorów.

## Aktualizacja i sprawdzenie przepisu

```bash
python scripts/capture.py
python scripts/seal.py
python scripts/verify.py
python -m unittest discover -s tests -v
```

`capture.py` zbiera pliki z jawnej listy i ustawienia GNOME. Pakiet dodaj do
`repo.txt` lub `aur.txt` tylko wtedy, gdy jest potrzebny zapisanej konfiguracji;
komentarz powinien wyjaśniać jego rolę. Nie generujemy pełnych spisów pakietów,
wersji ani zainstalowanych Flatpaków. `verify.py` sprawdza sumy, przenośność
ścieżek, archiwum i wzorce sekretów. Przed zachowaniem zmian obejrzyj `git diff`.

Prywatne repozytorium: [ajsem1337/dotfiles](https://github.com/ajsem1337/dotfiles).
Kopię przenieś poza dysk, który zamierzasz formatować.
