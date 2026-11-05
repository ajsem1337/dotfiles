#!/usr/bin/env python3
"""Set Micro's built-in transparent theme for root, preserving other settings."""
from datetime import datetime
import json
import os
from pathlib import Path
import pwd
import shutil


def configure(directory, backup_root):
    path = directory / 'settings.json'
    settings = json.loads(path.read_text()) if path.exists() else {}
    updated = {**settings, 'colorscheme': 'simple', 'syntax': True}
    if updated == settings:
        print('Micro roota: motyw simple i składnia już ustawione.')
        return
    if path.exists():
        backup = backup_root / ('micro-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
        backup.mkdir(parents=True, mode=0o700)
        shutil.copy2(path, backup / 'settings.json')
        print('Kopia ustawień Micro roota:', backup)
    directory.mkdir(parents=True, mode=0o700, exist_ok=True)
    path.write_text(json.dumps(updated, indent=4) + '\n')
    path.chmod(0o600)
    print('Micro roota: motyw simple (tło terminala), składnia włączona.')


if __name__ == '__main__':
    if os.geteuid() != 0:
        raise SystemExit('Uruchom przez sudo python scripts/configure-root-micro.py.')
    root_home = Path(pwd.getpwuid(0).pw_dir)
    configure(root_home / '.config/micro', Path('/var/backups/dotfiles'))
