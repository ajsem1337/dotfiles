#!/usr/bin/env python3
"""Apply a local gnome-before.json without printing its possibly private values."""
import json
from pathlib import Path
import subprocess
import sys

if len(sys.argv) != 2:
    sys.exit('Użycie: python scripts/revert-gnome.py /ścieżka/do/gnome-before.json')
commands = json.loads(Path(sys.argv[1]).read_text())
for args in commands:
    if not isinstance(args, list) or args[0] != 'gsettings' or 'set' not in args:
        sys.exit('Nieprawidłowy format kopii GNOME.')
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)
print('Przywrócono ustawienia GNOME z lokalnej kopii.')
