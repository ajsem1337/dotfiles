#!/usr/bin/env python3
"""Validate local Millennium patches and the Steam classes used by the layout."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
THEMES = ROOT / 'themes/steam'


def check_theme(theme):
    skin = json.loads((theme / 'skin.json').read_text())
    css = (theme / 'theme.css').read_text()
    assert skin['UseDefaultPatches'] is False
    for patch in skin['Patches']:
        assert 'TargetJs' not in patch
        path = (theme / patch['TargetCss']).resolve()
        assert path.is_relative_to(theme.resolve()) and path.is_file()
    assert not re.search(r'@import|https?://|backdrop-filter|:has\(|animation\s*:', css)
    classes = {name for name in re.findall(r'\.([A-Za-z_][A-Za-z0-9_-]*)', css)
               if name.startswith('_') or (len(name) >= 20 and not name.startswith('Dialog'))}
    steam = Path.home() / '.local/share/Steam/steamui'
    if not steam.is_dir():
        print(f'OK: {theme.name}: local CSS-only package. Steam is not installed; class check skipped.')
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
    print(f'OK: {theme.name}: CSS-only ({len(css.encode())} bytes), {len(classes)} Steam classes found.')
    return 0


def main():
    return max((check_theme(theme) for theme in sorted(THEMES.iterdir()) if (theme / 'skin.json').is_file()), default=0)


if __name__ == '__main__':
    sys.exit(main())
