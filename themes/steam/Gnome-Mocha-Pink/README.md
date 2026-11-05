# GNOME Mocha Pink

Lokalny motyw Millennium: kompaktowy nagłówek, wyśrodkowana nawigacja,
boczny panel oraz zawartość biblioteki w zaokrąglonej ramce. Paleta odpowiada
GTK/Qt/Vicinae: Catppuccin Mocha, akcent Pink, font Adwaita Sans.

Jedna lokalna warstwa CSS, bez JavaScriptu, importów sieciowych, rozmycia
ani własnych animacji. Przycisków pobierania, statusu i sterowania oknem
nie ukrywa. Nie ładuje kodu ani arkuszy Adwaita-for-Steam.

`restore.sh --home` kopiuje ten katalog do
`~/.local/share/Steam/millennium/themes/Gnome-Mocha-Pink` i scala wybór motywu
z `~/.config/millennium/config.json`. Steam powinien być zamknięty przy
odtwarzaniu ustawień, żeby nie nadpisał ich z pamięci.

Po aktualizacji Steama: `python scripts/check-steam-theme.py`.
Sprawdza on, czy klasy używane do układu nadal występują w plikach klienta.
Test renderowania sprawdza układ na reprezentatywnym DOM; pełne widoki
biblioteki, sklepu i czatu wymagają oceny w działającym kliencie.
Mniejszy arkusz nie jest pomiarem przyspieszenia całego Steama.

Format motywu: https://docs.steambrew.app/themes/basics/config
