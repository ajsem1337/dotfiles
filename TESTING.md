# Sprawdzenie konfiguracji — 2026-11-05

Bieżący eksport: `snapshot.json` i `assets/manifest.json` z 17:29 CET.

- Wygląd: 27 pakietów repo i 6 AUR. `pacman -T` potwierdził obecność
  wszystkich zależności przepisu w bieżącej instalacji. Opcjonalny profil
  systemowy nadal ma 23 pakiety repo i 3 AUR.
- Eksport zawiera 33 pliki w `home/`, 582 ustawienia wyglądu i skrótów GNOME,
  43 ustawienia systemowe GNOME oraz 62 pliki w `system/home/`.
- Archiwum wyglądu zebrano ponownie z bieżących zasobów. Zawiera motyw
  GTK/GNOME Shell, ikony, kursor i kod 11 rozszerzeń z licencjami.
- Dodane Rounded Window Corners Native: wersja 5, nazwa wersji 51.0,
  UUID `rounded-window-corners@ztrahmet.github.io`. `gnome-extensions info`
  potwierdza Enabled: Yes i State: ACTIVE. Rozszerzenie nie ma własnego
  schematu ustawień ani skrótów; czyta wygląd z libadwaity i użytkowego GTK4 CSS.
- Zapisany i bieżący profil: 148 efektywnych skrótów, brak kolizji.
  Super + strzałki należą do Tiling Shell; natywne odpowiedniki są wyłączone.
- Pięć nieobecnych rozszerzeń pominięto w liście do włączenia. Cache pozycji
  całej siatki aplikacji nie jest eksportowany; układ porządkuje zapisane
  Alphabetical App Grid. Pomijana jest też historia konsoli i dane prywatne.
- Odtwarzanie wyglądu do pustego katalogu: 47 088 zmian, drugie uruchomienie:
  0 zmian. Nowe rozszerzenie i jego licencja są na miejscu. Nie powstają
  katalogi ani konfiguracje usuniętych z profilu aplikacji.
- Osobne odtwarzanie systemowych plików użytkownika: 63 zmiany, drugie
  uruchomienie: 0 zmian. Ustawienia EasyEffects/PipeWire, ScopeBuddy i tabletu
  są w `system/`; `--all` nie stosuje tej części.
- Dziesięć testów jednostkowych: OK. Obejmują rozdział zakresów i pakietów,
  zachowanie ustawień konta przy scalaniu wyglądu, kopie, idempotencję,
  odrzucanie błędnego JSON i niebezpiecznych ścieżek oraz konfigurację Micro roota.
- `verify.py`: sumy kontrolne, przenośne ścieżki, układ archiwum i wzorce
  danych uwierzytelniających — OK. Składnia Pythona i kontrola diff — OK.
- `--all --plan` pokazuje aktualny przepis wyglądu. Nie wykonywano ponownej
  instalacji całego zestawu na świeżym systemie ani zmian zapory i schedulera.

Wcześniejsza migracja libcanberra z tego samego dnia pozostaje zweryfikowana:
73 pliki paczki `libcanberra-gtk2`, 0 zmienionych; komplet SONAME, brak błędów
bazy pacmana; GTK2 i GTK3 ładują moduły, oba konteksty audio zwracają 0.
