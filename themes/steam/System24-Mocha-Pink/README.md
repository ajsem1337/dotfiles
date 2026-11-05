# System24 for Steam — Mocha Pink

Nieoficjalna adaptacja stylistyki [system24](https://github.com/refact0r/system24)
refact0ra do Millennium. Selektory i układ są dostosowane do Steama; nie jest
to arkusz Discorda ani oficjalny port autora.

- DM Mono w wagach Light/Regular/Medium, dołączony lokalnie z licencją OFL.
- Catppuccin Mocha Pink jak w zapisanym motywie Equicorda.
- Kanciaste panele, obramowania, etykiety ASCII i tekstowa nawigacja.
- Jednolite tła bez gradientów, skryptów, rozmycia i importów sieciowych.
- Okładki, aktualności, pobieranie oraz sterowanie oknem pozostają dostępne.
- Strona konkretnej gry: płaskie tła Mocha, DM Mono, panele aktywności,
  znajomych, osiągnięć i dodatkowej zawartości. „Graj” pozostaje zielone,
  „Zainstaluj” ma różowy akcent, a przycisk niedostępny jest przygaszony.
- Grafika gry, wysokość nagłówka i natywny układ kolumn pozostają zachowane.

`restore.sh --home` instaluje font, kopiuje motyw do
`~/.local/share/Steam/millennium/themes/System24-Mocha-Pink` i scala jego wybór
z konfiguracją Millennium. Przed tym krokiem zamknij Steama.
Poprzedni GNOME Mocha Pink pozostaje alternatywą w liście motywów.
Po aktualizacji CSS wybierz **Steam → Zakończ** i uruchom klienta ponownie.
Samo zamknięcie okna może zostawić Steama w zasobniku z poprzednim arkuszem.

Kontrola klas zainstalowanego klienta: `python scripts/check-steam-theme.py`.
Test renderowania obejmuje makietę z rzeczywistymi klasami i regułami Steama;
nie zastępuje sprawdzenia wszystkich ekranów działającej aplikacji.

Inspiracja: system24, MIT, copyright 2025 refact0r.
Paleta: Catppuccin Mocha. Adaptacja układu Steama: ajsem dotfiles.
Font: DM Mono Project Authors, SIL Open Font License 1.1; licencja i źródło
w `home/.local/share/fonts/DMMono/`.

Wirtualizowana siatka gier zachowuje marginesy, padding i rozmiary sterowane
przez Steama. Ramka i etykieta biblioteki są na nagłówku, nie na opakowaniu
całej półki. Nawigacja obsługuje blokowy tytuł zakładki bez zawijania nawiasów.
