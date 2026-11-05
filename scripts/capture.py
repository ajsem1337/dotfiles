#!/usr/bin/env python3
"""Explicit allowlist: configuration, not application profiles or credentials."""
from pathlib import Path
from datetime import datetime
import json
import os
import pwd
import re
import shlex
import shutil
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

def command(*args):
    return subprocess.check_output(args, text=True).strip()

def excluded(_directory, names):
    return {n for n in names if n in {'.git', '__pycache__', 'Logs', 'logs', 'Cache', 'cache'} or '.bak' in n or '.backup' in n or n.endswith('~')}

def copy(source, destination):
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, symlinks=True, ignore=excluded, dirs_exist_ok=True)
    else:
        shutil.copy2(source, destination, follow_symlinks=False)

def main():
    if os.geteuid() == 0:
        raise RuntimeError('Uruchom capture.py jako użytkownik sesji GNOME, nie root.')
    target = ROOT / 'home'
    if target.exists():
        shutil.rmtree(target)
    paths = [
        '.bashrc', '.bash_profile', '.config/fish/config.fish', '.config/fish/functions',
        '.config/kitty/kitty.conf', '.config/kitty/current-theme.conf',
        '.config/fastfetch', '.config/environment.d', '.config/fontconfig/conf.d',
        '.config/gtk-4.0/gtk.css', '.config/Kvantum', '.config/qt5ct', '.config/qt6ct',
        '.config/micro/settings.json', '.config/micro/bindings.json', '.config/micro/colorschemes',
        '.config/vicinae/settings.json', '.config/vicinae/themes', '.config/mimeapps.list',
        '.config/pipewire/pipewire.conf.d', '.config/easyeffectsrc', '.config/easyeffects/db', '.local/share/easyeffects',
        '.config/scopebuddy/scb.conf', '.config/scopebuddy/AppID',
        '.config/OpenTabletDriver/settings.json', '.config/OpenTabletDriver/Plugins',
        '.config/OpenTabletDriver/Presets', '.config/Equicord/themes',
        '.config/Equicord/settings/quickCss.css', '.config/millennium/quick.css',
        '.config/autostart/Nextcloud.desktop', '.config/autostart/com.github.wwmm.easyeffects.desktop',
        '.local/bin/apply-soft-blur', '.local/bin/game-performance-powersave',
        '.local/bin/scopebuddygui', '.local/bin/set-wine-dark-theme.py',
        '.local/opt/scopebuddy-gui/src', '.local/opt/scopebuddy-gui/LICENSE.txt',
        '.local/opt/scopebuddy-gui/README.md',
        '.local/share/applications', '.local/share/backgrounds',
    ]
    for relative in paths:
        copy(HOME / relative, target / relative)
    omitted_launchers = []
    omitted_ids = set()
    appdir = target / '.local/share/applications'
    for launcher in appdir.rglob('*.desktop'):
        text = launcher.read_text()
        exec_line = next((x[5:] for x in text.splitlines() if x.startswith('Exec=')), '')
        args = shlex.split(exec_line)
        if args and args[0] == 'env':
            args = args[1:]
            while args and ('=' in args[0] or args[0].startswith('-')):
                args = args[1:]
        private_prefix = 'WINEPREFIX=' in text or 'wine' in launcher.relative_to(appdir).parts[:-1]
        missing_local_binary = bool(args and args[0].startswith(str(HOME) + '/') and not (target / Path(args[0]).relative_to(HOME)).exists())
        if private_prefix or missing_local_binary:
            omitted_launchers.append(str(launcher.relative_to(appdir)))
            omitted_ids.add(str(launcher.relative_to(appdir)).replace('/', '-'))
            launcher.unlink()
    mime = target / '.config/mimeapps.list'
    if mime.exists():
        cleaned = []
        for line in mime.read_text().splitlines(keepends=True):
            if '=' in line and not line.lstrip().startswith('#'):
                key, value = line.rstrip('\n').split('=', 1)
                apps = [x for x in value.split(';') if x]
                if any(x in omitted_ids for x in apps):
                    apps = [x for x in apps if x not in omitted_ids]
                    if not apps:
                        continue
                    line = key + '=' + ';'.join(apps) + '\n'
            cleaned.append(line)
        mime.write_text(''.join(cleaned))
    fish_colors = r'''for name in (set -Un)
if string match -qr '^fish_(color_|pager_color_|key_bindings$)' -- $name
printf 'set -g %s' $name
for value in $$name
printf ' %s' (string escape -- $value)
end
printf '\n'
end
end'''
    result = subprocess.run(['fish', '-c', fish_colors], capture_output=True, text=True, check=True)
    if result.stdout.strip():
        dest = target / '.config/fish/conf.d/99-dotfiles-colors.fish'
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text('# Exported appearance variables only; no fish history or private variables.\n' + result.stdout)
    # Portable text references. Keep binaries and pictures byte-for-byte.
    for p in target.rglob('*'):
        if p.is_file() and not p.is_symlink():
            try:
                text = p.read_text()
            except (UnicodeError, OSError):
                continue
            text = text.replace(str(HOME), '@HOME@')
            if p.name == 'config.jsonc' and 'fastfetch' in p.parts:
                text = text.replace('1787423429', '@INSTALL_EPOCH@')
            p.write_text(text)

    system = ROOT / 'system'
    for relative in (
        'etc/nftables.conf', 'etc/sysctl.d/99-network-hardening.conf',
        'etc/udev/rules.d/70-lc87.rules', 'etc/udev/rules.d/99-powercap.rules',
        'etc/systemd/resolved.conf.d/20-avahi-mdns.conf',
        'etc/systemd/system/nftables.service.d/override.conf',
        'etc/scx_loader/config.toml',
    ):
        copy(Path('/') / relative, system / relative)
    reference = system / 'reference'
    reference.mkdir(parents=True, exist_ok=True)
    shutil.copy2('/etc/pacman.conf', reference / 'pacman.conf')
    shutil.copy2('/etc/nsswitch.conf', reference / 'nsswitch.conf')
    # NSS and pacman are patched on restore, never replaced wholesale.

    packages = ROOT / 'packages'
    packages.mkdir(exist_ok=True)
    (packages / 'manual-launchers-not-restored.txt').write_text('\n'.join(sorted(omitted_launchers)) + '\n')
    # AUR libcanberra-gtk2 provides the core and both GTK modules. Never
    # request the conflicting repository package during a later restore.
    replaced = {'libcanberra', 'libcanberra-gtk2-compat'}
    for name, args in [('repo.txt', ('pacman', '-Qqen')), ('aur.txt', ('pacman', '-Qqem'))]:
        names = sorted(set(command(*args).splitlines()) - replaced)
        (packages / name).write_text('\n'.join(names) + '\n')
    required = '''fish kitty fastfetch eza bat zoxide atuin micro gnome-shell gdm
gnome-control-center gnome-shell-extensions gnome-settings-daemon gnome-keyring
gtk2 gtk-engine-murrine gtk3 gtk4 libadwaita evolution-data-server
qt5-base qt6-base qt5-wayland-decorations qt6-wayland kvantum kvantum-qt5 nss-mdns avahi nftables
networkmanager systemd-resolvconf pipewire pipewire-pulse wireplumber
power-profiles-daemon scx-scheds scx-tools opentabletdriver easyeffects scopebuddy pyside6 git base-devel
python python-gobject paru flatpak desktop-file-utils adwaita-fonts
'''.split()
    # Resolve only package names actually available on this installation.
    installed = set(command('pacman', '-Qq').splitlines())
    native = set(command('pacman', '-Qqn').splitlines())
    needed = set(required) & installed
    (packages / 'desktop-required.txt').write_text('\n'.join(sorted(needed & native)) + '\n')
    # Required optional features can themselves be foreign packages (Murrine).
    aur = (set((packages / 'aur.txt').read_text().splitlines()) | (needed - native)) - replaced
    aur.add('libcanberra-gtk2')
    (packages / 'aur.txt').write_text('\n'.join(sorted(aur)) + '\n')
    (packages / 'installed-versions.txt').write_text(command('pacman', '-Q') + '\n')
    refs = command('flatpak', 'list', '--app', '--columns=application,origin,branch').splitlines()
    (packages / 'flatpak-apps.tsv').write_text('\n'.join(refs) + '\n')
    (packages / 'flatpak-remotes.tsv').write_text(command('flatpak', 'remotes', '--show-disabled', '--columns=name,url,options') + '\n')
    (packages / 'repo-order.txt').write_text(command('pacman-conf', '--repo-list') + '\n')

    from gi.repository import Gio
    settings = []
    skipped = []
    source = Gio.SettingsSchemaSource.get_default()
    schema_ids = [
        'org.gnome.desktop.interface', 'org.gnome.desktop.wm.preferences',
        'org.gnome.desktop.wm.keybindings', 'org.gnome.desktop.background',
        'org.gnome.desktop.screensaver', 'org.gnome.desktop.sound',
        'org.gnome.desktop.peripherals.mouse', 'org.gnome.desktop.peripherals.touchpad',
        'org.gnome.desktop.peripherals.keyboard', 'org.gnome.mutter',
        'org.gnome.desktop.input-sources',
        'org.gnome.mutter.keybindings', 'org.gnome.mutter.wayland.keybindings',
        'org.gnome.shell', 'org.gnome.shell.keybindings',
        'org.gnome.settings-daemon.plugins.xsettings',
        'org.gnome.settings-daemon.plugins.media-keys',
    ]
    sources = [(source, schema_ids, None)]
    extroot = HOME / '.local/share/gnome-shell/extensions'
    for directory in extroot.glob('*/schemas'):
        if not (directory / 'gschemas.compiled').exists():
            continue
        sub = Gio.SettingsSchemaSource.new_from_directory(str(directory), source, False)
        normal, _ = sub.list_schemas(False)
        sources.append((sub, normal, str(directory.relative_to(HOME))))
    for src, ids, directory in sources:
        for schema_id in ids:
            schema = src.lookup(schema_id, True)
            if schema is None or schema.get_path() is None:
                continue
            obj = Gio.Settings.new_full(schema, None, None)
            for key in schema.list_keys():
                if key == 'custom-keybindings':
                    continue
                value = obj.get_value(key)
                if key == 'favorite-apps':
                    from gi.repository import GLib
                    value = GLib.Variant('as', [x for x in value.unpack() if x not in omitted_ids])
                if key in ('command-history', 'looking-glass-history') or (re.search(r'password|secret|token|api.?key|latitude|longitude|location', key, re.I) and value.get_type_string() != 'b'):
                    skipped.append(schema_id + ':' + key)
                    continue
                settings.append({'schema': schema_id, 'key': key, 'value': value.print_(True).replace(str(HOME), '@HOME@'), 'schema_dir': directory})
    media_id = 'org.gnome.settings-daemon.plugins.media-keys'
    custom_id = media_id + '.custom-keybinding'
    safe_paths = []
    for path in Gio.Settings.new(media_id).get_strv('custom-keybindings'):
        obj = Gio.Settings.new_with_path(custom_id, path)
        args = shlex.split(obj.get_string('command'))
        safe = (len(args) == 1 and args[0] == 'kitty') or (len(args) == 2 and args[0] == 'gtk-launch' and re.fullmatch(r'[\w.@+-]+', args[1]))
        if not safe:
            skipped.append('custom shortcut: ' + obj.get_string('name'))
            continue
        safe_paths.append(path)
        for key in ('name', 'command', 'binding'):
            settings.append({'schema': custom_id, 'path': path, 'key': key, 'value': obj.get_value(key).print_(True).replace(str(HOME), '@HOME@'), 'schema_dir': None})
    from gi.repository import GLib
    settings.append({'schema': media_id, 'key': 'custom-keybindings', 'value': GLib.Variant('as', safe_paths).print_(True), 'schema_dir': None})
    (ROOT / 'gnome').mkdir(exist_ok=True)
    (ROOT / 'gnome/settings.json').write_text(json.dumps(settings, indent=2, ensure_ascii=False) + '\n')
    (ROOT / 'gnome/excluded-private-keys.txt').write_text('\n'.join(skipped) + '\n')

    (ROOT / 'assets').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='dotfiles-assets-') as td:
        staging = Path(td)
        for relative in ('.themes/Catppuccin-Pink-Dark', '.local/share/icons/Tela-pink', '.local/share/icons/Tela-pink-dark', '.local/share/icons/Tela-pink-light', '.local/share/gnome-shell/extensions'):
            copy(HOME / relative, staging / relative)
        copy(Path('/usr/share/icons/MyCursor-GNOME51'), staging / '.local/share/icons/MyCursor-GNOME51')
        for p in staging.rglob('*'):
            if p.is_symlink() and Path(os.readlink(p)).is_absolute():
                dest = p.resolve()
                if not str(dest).startswith('/usr/share/icons/'):
                    raise ValueError(f'Unexpected absolute asset link: {p}')
                p.unlink()
                shutil.copy2(dest, p)
        with tarfile.open(ROOT / 'assets/desktop.tar.gz', 'w:gz') as archive:
            for p in sorted(staging.iterdir()):
                archive.add(p, arcname=p.name)
    manifest = {'created': datetime.now().astimezone().isoformat(), 'format': 1, 'home_placeholder': '@HOME@', 'login_shell': pwd.getpwuid(os.getuid()).pw_shell, 'home_files': sum(p.is_file() for p in target.rglob('*')), 'gnome_keys': len(settings), 'private_keys_excluded': len(skipped)}
    (ROOT / 'snapshot.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest))

if __name__ == '__main__':
    main()
