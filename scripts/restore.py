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
    if home == Path.home().resolve() and (root / 'themes/apps/millennium.json').is_file():
        if subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', 'steam'], capture_output=True).returncode == 0:
            raise RuntimeError('Zamknij Steama przed odtwarzaniem jego motywu i ustawień Millennium.')
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

    archive_path = root / 'assets/appearance.tar.gz'
    if archive_path.is_file():
        with tempfile.TemporaryDirectory(prefix='dotfiles-extract-') as td:
            with tarfile.open(archive_path) as archive:
                archive.extractall(td, filter='data')
            for source in sorted(Path(td).iterdir()):
                install_tree(source, Path(source.name))
    for source in sorted((root / 'home').iterdir()):
        install_tree(source, Path(source.name), template=True)
    for source in sorted((root / 'themes/steam').glob('*')):
        install_tree(source, Path('.local/share/Steam/millennium/themes') / source.name)
    if (root / 'themes/steam').is_dir():
        # The AUR post-install hook cannot link Millennium before Steam has
        # created its per-user directories. Reproduce its two fixed links.
        for arch, library in (('ubuntu12_32', 'libmillennium_bootstrap_x86.so'),
                              ('ubuntu12_64', 'libmillennium_bootstrap_hhx64.so')):
            backend = Path('/usr/lib/millennium') / library
            if not backend.is_file():
                continue
            relative = Path('.local/share/Steam') / arch / 'libXtst.so.6'
            dest = home / relative
            if not dest.parent.resolve().is_relative_to(home):
                raise ValueError('Steam path escapes home: ' + str(dest))
            if dest.is_symlink() and os.readlink(dest) == str(backend):
                continue
            if dest.exists() or dest.is_symlink():
                save(dest, relative)
                dest.unlink()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.symlink_to(backend)
            count += 1
    # Merge appearance switches without replacing account/plugin/proxy settings.
    for patch in sorted((root / 'themes/apps').glob('*.json')):
        payload = json.loads(patch.read_text())
        relative = Path(payload['path'])
        dest = home / relative
        if relative.is_absolute() or not dest.resolve().is_relative_to(home):
            raise ValueError('Unsafe appearance patch path: ' + str(relative))
        settings = json.loads(dest.read_text()) if dest.exists() else {}
        def merge(current, updates):
            result = dict(current)
            for key, value in updates.items():
                result[key] = merge(result.get(key, {}), value) if isinstance(value, dict) else value
            return result
        updated = merge(settings, payload['merge'])
        if updated != settings:
            if dest.exists():
                save(dest, relative)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps(updated, indent=4) + '\n')
            count += 1
    if home == Path.home().resolve():
        if (root / 'home/.local/share/fonts').is_dir():
            run(['fc-cache', '-f', home / '.local/share/fonts'])
        if (root / 'home/.local/share/applications').is_dir():
            subprocess.run(['update-desktop-database', str(home / '.local/share/applications')], check=True)
        if archive_path.is_file():
            for directory in (home / '.local/share/gnome-shell/extensions').glob('*/schemas'):
                if list(directory.glob('*.gschema.xml')):
                    run(['glib-compile-schemas', directory])
        # Recreate the working native Flatpak theme visibility.
        if archive_path.is_file():
            run(['flatpak', 'override', '--user', '--filesystem=xdg-config/gtk-4.0:ro',
                 f'--filesystem={home}/.themes:ro', f'--filesystem={home}/.local/share/icons:ro'])
    print(f'Home: {count} changed files. Backups: {backup}')
    return backup, count

def restore_gnome(settings_path=None, units=('vicinae.service',), set_shell=True):
    if not os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
        raise RuntimeError('Uruchom --gnome w sesji GNOME jako zwykły użytkownik.')
    failed = []
    prepared = []
    previous = []
    items = json.loads((settings_path or ROOT / 'gnome/settings.json').read_text())
    # Extension preferences and native keybindings must precede enabling extensions.
    items.sort(key=lambda item: item['schema'] == 'org.gnome.shell' and item['key'] == 'enabled-extensions')
    for item in items:
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
    for unit in units:
        exists = subprocess.run(['systemctl', '--user', 'cat', unit], capture_output=True).returncode == 0
        if exists:
            run(['systemctl', '--user', 'enable', unit])
    shell = json.loads((ROOT / 'snapshot.json').read_text()).get('login_shell')
    if set_shell and shell == '/usr/bin/fish' and Path(shell).is_file() and pwd.getpwuid(os.getuid()).pw_shell != shell:
        run(['chsh', '-s', shell])
    print('Kopia ustawień GNOME:', directory / 'gnome-before.json')

def install_packages(include_system=False, include_appearance=True):
    names = sorted(set((lines('repo.txt') if include_appearance else []) +
                       (lines('system.txt') if include_system else [])))
    run(['sudo', 'pacman', '-Syu', '--needed', '--', *names])
    aur = (lines('aur.txt') if include_appearance else []) + (lines('system-aur.txt') if include_system else [])
    if aur:
        if not shutil.which('paru'):
            raise RuntimeError('Zainstaluj paru z CachyOS, potem ponów --packages.')
        # Keep the normal PKGBUILD review rather than silently trusting AUR code.
        run(['paru', '-S', '--needed', '--aur', '--', *aur])
    if include_system:
        run(['pacman', '-Q', 'libcanberra-gtk2'])
        run(['pacman', '-T', 'libcanberra', 'libcanberra.so=0-64',
             'libcanberra-gtk.so=0-64', 'libcanberra-gtk3.so=0-64'])

def main():
    parser = argparse.ArgumentParser(description='Odtworzenie konfiguracji CachyOS/GNOME. Bez flag pokazuje tylko plan.')
    for flag in ('home', 'gnome', 'root-micro', 'system', 'packages', 'all', 'plan'):
        parser.add_argument('--' + flag, action='store_true')
    parser.add_argument('--target-home', type=Path, default=Path.home(), help='Osobny katalog do testu --home; bez operacji systemowych.')
    args = parser.parse_args()
    if os.geteuid() == 0:
        parser.error('Uruchom restore.sh jako zwykły użytkownik; skrypt sam używa sudo dla systemu.')
    if args.all:
        args.home = args.gnome = args.root_micro = args.packages = True
    include_appearance = not args.system or args.home or args.gnome or args.root_micro
    if args.target_home.resolve() != Path.home().resolve() and (args.gnome or args.root_micro or args.system or args.packages):
        parser.error('--target-home obsługuje wyłącznie bezpieczny test --home.')
    if args.plan or not any((args.home, args.gnome, args.root_micro, args.system, args.packages)):
        print((ROOT / 'snapshot.json').read_text())
        if include_appearance:
            print('Wygląd: zależności → pliki i motywy → GNOME → Micro roota.')
            print('Repo:', ' '.join(lines('repo.txt')))
            print('AUR:', ' '.join(lines('aur.txt')))
        if args.system:
            print('Dodatkowe pakiety --system:', ' '.join(lines('system.txt')))
            print('Dodatkowe AUR --system:', ' '.join(lines('system-aur.txt')))
        print('Audio, ScopeBuddy, tablet, zapora, sieć i scheduler należą do --system. Bazą jest CachyOS GNOME.')
        return
    run([sys.executable, ROOT / 'scripts/verify.py'])
    if args.packages:
        install_packages(include_system=args.system, include_appearance=bool(include_appearance))
    if args.home:
        restore_home(args.target_home)
    if args.gnome:
        run([sys.executable, ROOT / 'scripts/check-keybindings.py'])
        restore_gnome()
    if args.root_micro:
        run(['sudo', sys.executable, ROOT / 'scripts/configure-root-micro.py'])
    if args.system:
        restore_home(args.target_home, ROOT / 'system')
        restore_gnome(ROOT / 'system/gnome/settings.json',
                      units=('wireplumber.service', 'opentabletdriver.service'), set_shell=False)
        run(['sudo', sys.executable, ROOT / 'scripts/system.py', '--apply'])
    print('Gotowe. Wyloguj i zaloguj się ponownie, aby wszystkie aplikacje odczytały konfigurację.')

if __name__ == '__main__':
    main()
