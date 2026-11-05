#!/usr/bin/env python3
"""Restore this explicit desktop profile, keeping backups of replaced files."""
import argparse
from datetime import datetime
import hashlib
import json
import os
import pwd
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def run(args, **kwargs):
    print('+', ' '.join(map(str, args)), flush=True)
    return subprocess.run(list(map(str, args)), check=True, **kwargs)

def lines(name):
    return [x.strip() for x in (ROOT / 'packages' / name).read_text().splitlines() if x.strip() and not x.startswith('#')]

def render(data, home):
    try:
        text = data.decode('utf-8')
    except UnicodeError:
        return data
    if '\x00' in text:
        return data
    epoch = subprocess.check_output(['stat', '-c', '%W', '/'], text=True).strip()
    if not epoch.isdigit() or int(epoch) <= 0:
        epoch = str(int(datetime.now().timestamp()))
    return text.replace('@HOME@', str(home)).replace('@INSTALL_EPOCH@', epoch).encode()

def restore_home(home, root=ROOT):
    home = home.resolve()
    home.mkdir(parents=True, exist_ok=True)
    backup = home / '.local/state/dotfiles-backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    count = 0

    def install_tree(source, relative, template=False):
        nonlocal count
        dest = home / relative
        if not dest.parent.resolve().is_relative_to(home):
            raise ValueError(f'Destination escapes home through a symlink: {dest}')
        if source.is_dir() and not source.is_symlink():
            if dest.exists() and not dest.is_dir():
                save(dest, relative)
                dest.unlink()
            dest.mkdir(parents=True, exist_ok=True)
            for child in sorted(source.iterdir()):
                install_tree(child, relative / child.name, template)
            return
        data = render(source.read_bytes(), home) if template and not source.is_symlink() else None
        if source.is_symlink():
            link = os.readlink(source)
            if os.path.isabs(link) or not (dest.parent / link).resolve().is_relative_to(home):
                raise ValueError(f'Unsafe symlink: {relative} -> {link}')
            if dest.is_symlink() and os.readlink(dest) == link:
                return
        elif dest.is_file() and not dest.is_symlink():
            expected = data if data is not None else source.read_bytes()
            if dest.read_bytes() == expected and stat.S_IMODE(dest.stat().st_mode) == stat.S_IMODE(source.stat().st_mode):
                return
        if dest.exists() or dest.is_symlink():
            save(dest, relative)
            if dest.is_dir() and not dest.is_symlink():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        dest.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            dest.symlink_to(os.readlink(source))
        elif data is not None:
            dest.write_bytes(data)
            dest.chmod(stat.S_IMODE(source.stat().st_mode))
        else:
            shutil.copy2(source, dest)
        count += 1

    def save(dest, relative):
        saved = backup / relative
        saved.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_dir() and not dest.is_symlink():
            shutil.copytree(dest, saved, symlinks=True)
        else:
            shutil.copy2(dest, saved, follow_symlinks=False)

    with tempfile.TemporaryDirectory(prefix='dotfiles-extract-') as td:
        with tarfile.open(root / 'assets/desktop.tar.gz') as archive:
            archive.extractall(td, filter='data')
        for source in sorted(Path(td).iterdir()):
            install_tree(source, Path(source.name))
    for source in sorted((root / 'home').iterdir()):
        install_tree(source, Path(source.name), template=True)
    if home == Path.home().resolve():
        subprocess.run(['update-desktop-database', str(home / '.local/share/applications')], check=True)
        for directory in (home / '.local/share/gnome-shell/extensions').glob('*/schemas'):
            if list(directory.glob('*.gschema.xml')):
                run(['glib-compile-schemas', directory])
        # Recreate the working native Flatpak theme visibility.
        run(['flatpak', 'override', '--user', '--filesystem=xdg-config/gtk-4.0:ro',
             f'--filesystem={home}/.themes:ro', f'--filesystem={home}/.local/share/icons:ro'])
    print(f'Home: {count} changed files. Backups: {backup}')
    return backup, count

def restore_gnome():
    if not os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
        raise RuntimeError('Uruchom --gnome w sesji GNOME jako zwykły użytkownik.')
    failed = []
    prepared = []
    previous = []
    for item in json.loads((ROOT / 'gnome/settings.json').read_text()):
        args = ['gsettings']
        if item['schema_dir']:
            directory = Path.home() / item['schema_dir']
            if not directory.exists():
                failed.append(item['schema'] + ' (brak rozszerzenia)')
                continue
            args += ['--schemadir', str(directory)]
        schema_arg = item['schema'] + (':' + item['path'] if item.get('path') else '')
        before = subprocess.run(args + ['get', schema_arg, item['key']], capture_output=True, text=True)
        if before.returncode == 0:
            previous.append(args + ['set', schema_arg, item['key'], before.stdout.strip()])
        prepared.append(args + ['set', schema_arg, item['key'], item['value'].replace('@HOME@', str(Path.home()))])
    directory = Path.home() / '.local/state/dotfiles-backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    directory.mkdir(parents=True, mode=0o700)
    (directory / 'gnome-before.json').write_text(json.dumps(previous, indent=2) + '\n')
    for args in prepared:
        result = subprocess.run(args, capture_output=True, text=True)
        if result.returncode:
            failed.append(args[-3] + ':' + args[-2])
    if failed:
        print('Nie zastosowano nieobecnych lub zmienionych ustawień:', '\n'.join(sorted(set(failed))))
    for unit in ('wireplumber.service', 'opentabletdriver.service', 'vicinae.service'):
        exists = subprocess.run(['systemctl', '--user', 'cat', unit], capture_output=True).returncode == 0
        if exists:
            run(['systemctl', '--user', 'enable', unit])
    shell = json.loads((ROOT / 'snapshot.json').read_text()).get('login_shell')
    if shell == '/usr/bin/fish' and Path(shell).is_file() and pwd.getpwuid(os.getuid()).pw_shell != shell:
        run(['chsh', '-s', shell])
    print('Kopia ustawień GNOME:', directory / 'gnome-before.json')

def install_packages():
    run(['sudo', sys.executable, ROOT / 'scripts/system.py', '--prepare-repos'])
    names = sorted(set(lines('repo.txt') + lines('desktop-required.txt')))
    run(['sudo', 'pacman', '-Syu', '--needed', '--', *names])
    aur = lines('aur.txt')
    if aur:
        if not shutil.which('paru'):
            raise RuntimeError('Zainstaluj paru z CachyOS, potem ponów --packages.')
        # Keep the normal PKGBUILD review rather than silently trusting AUR code.
        run(['paru', '-S', '--needed', '--aur', '--', *aur])
    run(['pacman', '-Q', 'libcanberra-gtk2'])
    run(['pacman', '-T', 'libcanberra', 'libcanberra.so=0-64',
         'libcanberra-gtk.so=0-64', 'libcanberra-gtk3.so=0-64'])

def main():
    parser = argparse.ArgumentParser(description='Odtworzenie konfiguracji CachyOS/GNOME. Bez flag pokazuje tylko plan.')
    for flag in ('home', 'gnome', 'system', 'packages', 'all', 'plan'):
        parser.add_argument('--' + flag, action='store_true')
    parser.add_argument('--target-home', type=Path, default=Path.home(), help='Osobny katalog do testu --home; bez operacji systemowych.')
    args = parser.parse_args()
    if os.geteuid() == 0:
        parser.error('Uruchom restore.sh jako zwykły użytkownik; skrypt sam używa sudo dla systemu.')
    if args.all:
        args.home = args.gnome = args.system = args.packages = True
    if args.target_home.resolve() != Path.home().resolve() and (args.gnome or args.system or args.packages):
        parser.error('--target-home obsługuje wyłącznie bezpieczny test --home.')
    if args.plan or not any((args.home, args.gnome, args.system, args.packages)):
        print((ROOT / 'snapshot.json').read_text())
        print('Plan: pakiety i repozytoria → pliki użytkownika → GNOME → ustawienia systemowe.')
        print('Nie kopiujemy partycji, rozruchu, haseł, kont ani profili przeglądarek. Użyj --all po świeżej instalacji CachyOS GNOME.')
        return
    run([sys.executable, ROOT / 'scripts/verify.py'])
    if args.packages:
        install_packages()
    if args.home:
        restore_home(args.target_home)
    if args.gnome:
        restore_gnome()
    if args.system:
        run(['sudo', sys.executable, ROOT / 'scripts/system.py', '--apply'])
    print('Gotowe. Wyloguj i zaloguj się ponownie, aby wszystkie aplikacje odczytały konfigurację.')

if __name__ == '__main__':
    main()
