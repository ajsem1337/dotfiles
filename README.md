# CachyOS GNOME — mój pulpit

Lokalny zapis konfiguracji po porządkach systemu i ujednoliceniu Catppuccin
Mocha Pink. Przeznaczony do świeżej instalacji **CachyOS z GNOME**.

## Po formacie

1. Zainstaluj CachyOS GNOME normalnym instalatorem. Partycje, użytkownika,
   hasło, rozruch i połączenie z internetem skonfiguruj w instalatorze.
2. Skopiuj ten katalog z zewnętrznej kopii. Otwórz terminal jako zwykły
   użytkownik w zalogowanej, lokalnej sesji GNOME.
   Jeśli masz gotowe archiwum, rozpakuj je w katalogu domowym:

   ```bash
   tar --zstd -xf dotfiles-2026-10-30.tar.zst
   ```

3. Uruchom:

   ```bash
   cd ~/dotfiles
   ./restore.sh --plan
   ./restore.sh --all
   ```

4. Przejrzyj normalne pytania pacmana i PKGBUILD-y AUR. Na końcu wyloguj się
   i zaloguj ponownie; restart uruchomi też wybrany scheduler i usługi.

Skrypt sam używa `sudo` przy zmianach systemowych. **Nie uruchamiaj całego
restore.sh jako root.** Potrzebny jest internet do repozytoriów/AUR,
także do budowania `libcanberra-gtk2`.

Listy pakietów instalują aktualne wersje z repozytoriów. `installed-versions.txt`
jest punktem odniesienia, nie zamrożeniem starego systemu rolling release.

## Co jest zapisane

- GNOME: motyw, kolory, fonty, kursor, ikony, tapeta, zachowanie pulpitu,
  skróty systemowe i ustawienia zainstalowanych rozszerzeń.
- Zasoby: Catppuccin GTK2/3/Shell, mała nakładka GTK4/libadwaita, Kvantum,
  Tela Pink, MyCursor-GNOME51 i lokalne rozszerzenia GNOME.
- Fish, Kitty, Fastfetch z obrazkiem, Micro, Vicinae i konfiguracja monospace.
  Kitty, Fish, Fastfetch, Micro i EasyEffects są na listach repozytoriów;
  ScopeBuddy oraz `libcanberra-gtk2` są na liście AUR.
- PipeWire, EasyEffects z presetami/autoloadem oraz OpenTabletDriver
  z ustawieniami i wtyczkami. Nazwy urządzeń audio i geometria tabletu mogą
  wymagać dopasowania po zmianie sprzętu.
- ScopeBuddy: konfiguracja globalna i profile AppID oraz lokalny interfejs
  [scopebuddy-gui](https://github.com/rfrench3/scopebuddy-gui) z licencją
  LGPL-3.0-only i zależnością PySide6. Zachowane ustawienia rozdzielczości
  Gamescope mogą wymagać dopasowania do monitora.
- Domyślne aplikacje, niesekretne skrypty pomocnicze i wybrane autostarty.
- System: natywne nftables, ustawienia sieciowe sysctl, mDNS przez Avahi,
  nss-mdns, lokalne reguły udev i P2DQ/PowerSave w scx_loader.
- Listy jawnie zainstalowanych pakietów repo/AUR i pełna lista wersji.

Kolejność źródeł pacmana: **CachyOS → Omarchy → Arch**. AUR jest kolejnym
źródłem, gdy pakiet nie występuje w repozytoriach. Flatpak i AppImage są
osobnymi sposobami instalacji.

## Zakresy zamiast pełnego odtworzenia

```bash
./restore.sh --packages      # repozytoria i pakiety, w tym libcanberra-gtk2 z AUR
./restore.sh --home          # pliki, motywy, presety i rozszerzenia
./restore.sh --gnome         # zapisane ustawienia GNOME w bieżącej sesji
./restore.sh --system        # wybrane pliki /etc i usługi
```

Te etapy można uruchamiać osobno w podanej kolejności. `--system` zakłada,
że zależności są już zainstalowane. Zmienia zaporę na profil blokujący nowe
połączenia przychodzące — wykonuj ten etap lokalnie.

Przed nadpisaniem pliki użytkownika trafiają do
`~/.local/state/dotfiles-backups/`, a pliki systemowe do
`/var/backups/dotfiles-*`. Powtórne `--home` pomija pliki o identycznej treści
i uprawnieniach. Nie czyści innych ustawień użytkownika.

`--gnome` zapisuje poprzednie wartości w `gnome-before.json` w katalogu kopii.
Można je odtworzyć przez `python scripts/revert-gnome.py /ścieżka/do/gnome-before.json`.
Profil ustawia Fish jako powłokę logowania; jeśli świeża instalacja ma inną
powłokę, standardowy `chsh` poprosi o hasło użytkownika.

Bezpieczna próba odtworzenia samych plików w pustym katalogu:

```bash
./restore.sh --home --target-home /tmp/proba-dotfiles
```

Ten wariant nie zmienia ustawień działającej sesji, pakietów ani `/etc`.

## GTK4 i GTK2

GTK4/libadwaita dostają **kolory i akcenty**, a biblioteki aplikacji dostarczają
kształty, rozmiary i odstępy. Globalny arkusz ma około 3 KB zamiast starej
pełnej skórki około 250 KB. Zwykły GTK4 używa natywnego arkusza GTK i małej
nakładki kolorów. Qt Widgets korzysta z Kvantum; aplikacje Qt Quick i programy
z własnym interfejsem mogą mieć dodatkowe, osobne ustawienia wyglądu.

Pakiet [libcanberra-gtk2 z AUR](https://aur.archlinux.org/packages/libcanberra-gtk2)
dostarcza rdzeń libcanberra, backendy, nagłówki i moduły GTK2/GTK3. Zastępuje
systemowe `libcanberra` oraz dawny lokalny `libcanberra-gtk2-compat`.
Nie należy instalować ich równolegle ani dodawać `libcanberra` do listy repo.
Pozostałe aplikacje korzystają z dostarczanych przez paczkę zależności
`libcanberra` i bibliotek z tym samym SONAME.

Ręczna instalacja lub migracja (zaakceptuj usunięcie obu starych pakietów
w transakcji pacmana, bez `-Rdd` i bez `--overwrite`):

```bash
paru -S --needed --aur libcanberra-gtk2
pacman -Q libcanberra-gtk2
pacman -T libcanberra libcanberra.so=0-64 libcanberra-gtk.so=0-64 libcanberra-gtk3.so=0-64
pacman -Dk
pacman -Qkk libcanberra-gtk2
python scripts/check-gtk2.py
```

Test GTK uruchom w lokalnej sesji graficznej. Sprawdza załadowanie rzeczywistych
modułów GTK2 i GTK3 oraz otwarcie kontekstu audio, bez odtwarzania dźwięku.

## Micro, również przez sudo

Motyw `simple` używa tła terminala i koloruje składnię. W Kitty zachowuje
przezroczystość ustawioną przez `background_opacity`. Konto root ma osobny
plik ustawień, dlatego sam motyw użytkownika nie zmienia `sudo micro`.
Etap `--system` ustawia rootowi ten sam wbudowany motyw i włącza składnię.
Można zastosować tylko tę zmianę:

```bash
sudo python scripts/configure-root-micro.py
sudo micro /etc/example.conf
```

Skrypt zachowuje pozostałe ustawienia roota i tworzy kopię zmienianego pliku
w `/var/backups/dotfiles/`. Nie udostępnia rootowi wtyczek użytkownika.

## Co wymaga oddzielnej kopii

To dotfiles, nie obraz całego komputera. Nie zawiera:

- haseł, tokenów, SSH/GPG/AWS/OCI, keyringów i kont online;
- profili przeglądarek, sesji Discorda/Equicorda, ciasteczek i historii;
- konfiguracji kont Nextcloud, sieci Wi-Fi/VPN i prywatnych narzędzi Oracle;
- dokumentów, gier, zapisów gier, bibliotek Steam i Wine;
- plików AppImage i ręcznie pobranych pakietów Flatpak.

Własne AppImage zachowaj oddzielnie, zwłaszcza
`~/.local/bin/statlocker-companion_amd64.AppImage`. Deadlock Mod Manager jest
obecnie instalacją z ręcznego pliku `.flatpak`, z origin bez adresu aktualizacji;
zachowaj instalator lub pobierz go ponownie z oficjalnego projektu. Informacje
o Flatpaku są w `packages/flatpak-*.tsv`; puste adresy nie są używane jako
repozytoria przez skrypt.

Skróty do tych ręcznych aplikacji i prywatnych prefixów Wine nie są
odtwarzane jako martwe pozycje menu. Lista pominiętych skrótów jest w
`packages/manual-launchers-not-restored.txt`; dotyczy to tylko kopii,
nie usuwa skrótów z działającego komputera. Zainstalowana ponownie
aplikacja lub launcher utworzy właściwe skróty.

Nie kopiujemy `/etc/fstab`, identyfikatorów UUID, machine-id, haseł, bootloadera
ani starych list mirrorów. Referencyjne pacman.conf i nsswitch.conf są zapisane
do wglądu, ale nie zastępują w całości konfiguracji świeżego systemu.
Monitory, firmware i sterowniki pozostają po stronie nowej instalacji.

## Kontrola i aktualizacja kopii

```bash
python scripts/verify.py
python -m unittest discover -s tests -v
```

`verify.py` sprawdza sumy kontrolne, układ archiwum, przenośne ścieżki i wzorce
sekretów. Zbieranie używa jawnej listy plików, nie całego `~/.config`.

Ponowne zebranie konfiguracji na działającym pulpicie:

```bash
python scripts/capture.py
python scripts/seal.py
python scripts/verify.py
```

Przed zachowaniem nowej wersji obejrzyj `git diff`. Ustawienia zawierające
klucze API, położenie i historię konsoli GNOME są pomijane; lista pominiętych
kluczy jest w `gnome/excluded-private-keys.txt`.

Katalog oraz archiwum trzeba przenieść poza formatowany dysk. Prywatne
repozytorium kopii: [ajsem1337/dotfiles](https://github.com/ajsem1337/dotfiles).
