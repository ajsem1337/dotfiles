#!/usr/bin/env python3
"""Validate local Millennium patches and the Steam classes used by the layout."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / 'themes/steam/Gnome-Mocha-Pink'


def main():
    skin = json.loads((THEME / 'skin.json').read_text())
    css = (THEME / 'theme.css').read_text()
    assert skin['UseDefaultPatches'] is False
    for patch in skin['Patches']:
        assert 'TargetJs' not in patch
        path = (THEME / patch['TargetCss']).resolve()
        assert path.is_relative_to(THEME.resolve()) and path.is_file()
    assert not re.search(r'@import|https?://|backdrop-filter|:has\(|animation\s*:', css)
    classes = set(re.findall(r'\.(_[A-Za-z0-9_-]+)', css))
    steam = Path.home() / '.local/share/Steam/steamui'
    if not steam.is_dir():
        print('OK: local CSS-only Millennium package. Steam is not installed; class check skipped.')
        return 0
    found = set()
    for path in [*steam.glob('*.js'), *steam.glob('css/*.css')]:
        text = path.read_text(errors='replace')
        found.update(name for name in classes - found if name in text)
        if found == classes:
            break
    missing = sorted(classes - found)
    if missing:
        print('Steam layout classes changed: ' + ', '.join(missing), file=sys.stderr)
        return 1
    print(f'OK: CSS-only theme ({len(css.encode())} bytes), {len(classes)} layout classes found in the installed Steam client.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
