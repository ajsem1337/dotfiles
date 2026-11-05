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
        '.config/fish/config.fish', '.config/fish/functions',
        '.config/kitty/kitty.conf', '.config/kitty/current-theme.conf',
        '.config/fastfetch', '.config/fontconfig/conf.d',
        '.local/share/fonts/DMMono',
        '.config/environment.d/10-qt.conf', '.config/environment.d/30-default-apps.conf',
        '.config/environment.d/40-cursor.conf',
        '.config/gtk-4.0/gtk.css', '.config/Kvantum', '.config/qt5ct', '.config/qt6ct',
        '.config/micro/settings.json', '.config/micro/bindings.json', '.config/micro/colorschemes',
        '.config/vicinae/settings.json', '.config/vicinae/themes',
        '.config/Equicord/themes',
        '.local/bin/apply-soft-blur', '.local/bin/set-wine-dark-theme.py',
        '.local/share/applications/vicinae-toggle.desktop',
        '.local/share/applications/vicinae-clipboard.desktop',
        '.local/share/applications/micro.desktop', '.local/share/backgrounds',
    ]
    for relative in paths:
        copy(HOME / relative, target / relative)
    service_home = ROOT / 'system/home'
    if service_home.exists():
        shutil.rmtree(service_home)
    for relative in (
        '.config/pipewire/pipewire.conf.d', '.config/easyeffectsrc',
        '.config/easyeffects/db', '.local/share/easyeffects',
        '.config/autostart/com.github.wwmm.easyeffects.desktop',
        '.config/scopebuddy/scb.conf', '.config/scopebuddy/AppID',
        '.local/bin/scopebuddygui', '.local/share/applications/io.github.rfrench3.scopebuddy-gui.desktop',
        '.local/opt/scopebuddy-gui/src', '.local/opt/scopebuddy-gui/LICENSE.txt',
        '.local/opt/scopebuddy-gui/README.md',
        '.config/OpenTabletDriver/settings.json', '.config/OpenTabletDriver/Plugins',
        '.config/OpenTabletDriver/Presets', '.config/environment.d/20-gaming.conf',
    ):
        copy(HOME / relative, service_home / relative)
    scope = service_home / '.config/scopebuddy/scb.conf'
    if scope.exists():
        scope.write_text(scope.read_text().replace('\\"$HOME/.local/bin/game-performance-powersave\\"', '/usr/bin/game-performance'))
    # Only appearance switches are exported, never Equicord account/plugin data.
    equicord = HOME / '.config/Equicord/settings/settings.json'
    if equicord.is_file():
        appearance = json.loads(equicord.read_text())
        export = {key: appearance[key] for key in ('enabledThemes', 'useQuickCss', 'frameless', 'transparent', 'nativeTitleBar', 'winNativeTitleBar', 'noRoundCorners', 'mainWindowFrameless') if key in appearance}
        app_patch = ROOT / 'themes/apps/equicord.json'
        app_patch.parent.mkdir(parents=True, exist_ok=True)
        app_patch.write_text(json.dumps({'path': '.config/Equicord/settings/settings.json', 'merge': export}, indent=2) + '\n')
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
    for p in [*target.rglob('*'), *service_home.rglob('*')]:
        if p.is_file() and not p.is_symlink():
            try:
                text = p.read_text()
            except (UnicodeError, OSError):
                continue
            text = text.replace(str(HOME), '@HOME@')
            if p.name == 'config.jsonc' and 'fastfetch' in p.parts:
                text = text.replace('1787423429', '@INSTALL_EPOCH@')
            if p.is_relative_to(service_home / '.local/opt/scopebuddy-gui') or p.is_relative_to(service_home / '.config/scopebuddy'):
                text = '\n'.join(line.rstrip() for line in text.splitlines()).rstrip() + '\n'
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

    # Package recipes are maintained manually; capture exports no inventories.
    from gi.repository import Gio
    settings = []
    system_settings = []
    skipped = []
    extroot = HOME / '.local/share/gnome-shell/extensions'
    enabled = Gio.Settings.new('org.gnome.shell').get_strv('enabled-extensions')
    installed = {}
    for directory in (Path('/usr/share/gnome-shell/extensions'), extroot):
        for metadata in directory.glob('*/metadata.json'):
            info = json.loads(metadata.read_text())
            installed[info['uuid']] = {key: info.get(key) for key in ('uuid', 'name', 'version', 'version-name', 'settings-schema')}
            installed[info['uuid']]['source'] = 'user' if directory == extroot else 'system'
    missing = sorted(set(enabled) - installed.keys())
    active = [uuid for uuid in enabled if uuid in installed]
    system_schemas = {'org.gnome.desktop.sound', 'org.gnome.desktop.input-sources',
                      'org.gnome.desktop.peripherals.mouse', 'org.gnome.desktop.peripherals.touchpad',
                      'org.gnome.desktop.peripherals.keyboard'}

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
                if schema_id == 'org.gnome.shell' and key == 'enabled-extensions':
                    from gi.repository import GLib
                    value = GLib.Variant('as', active)
                if key in ('command-history', 'looking-glass-history') or (re.search(r'password|secret|token|api.?key|latitude|longitude|location', key, re.I) and value.get_type_string() != 'b'):
                    skipped.append(schema_id + ':' + key)
                    continue
                (system_settings if schema_id in system_schemas else settings).append({'schema': schema_id, 'key': key, 'value': value.print_(True).replace(str(HOME), '@HOME@'), 'schema_dir': directory})
    media_id = 'org.gnome.settings-daemon.plugins.media-keys'
    custom_id = media_id + '.custom-keybinding'
    safe_paths = []
    for path in Gio.Settings.new(media_id).get_strv('custom-keybindings'):
        obj = Gio.Settings.new_with_path(custom_id, path)
        args = shlex.split(obj.get_string('command'))
        safe = (len(args) == 1 and args[0] == 'kitty') or (len(args) == 2 and args[0] == 'gtk-launch' and args[1] in ('vicinae-toggle', 'vicinae-clipboard'))
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
    (ROOT / 'system/gnome').mkdir(exist_ok=True)
    (ROOT / 'system/gnome/settings.json').write_text(json.dumps(system_settings, indent=2, ensure_ascii=False) + '\n')
    records = [{**info, 'enabled': uuid in active} for uuid, info in installed.items()
               if info['source'] == 'user' or uuid in active]
    (ROOT / 'gnome/extensions.json').write_text(json.dumps({'extensions': records, 'missing_enabled_entries_removed': missing}, indent=2, ensure_ascii=False) + '\n')
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
        with tarfile.open(ROOT / 'assets/appearance.tar.gz', 'w:gz') as archive:
            for p in sorted(staging.iterdir()):
                archive.add(p, arcname=p.name)
        resources = ['.themes/Catppuccin-Pink-Dark', '.local/share/icons/Tela-pink',
                     '.local/share/icons/Tela-pink-dark', '.local/share/icons/Tela-pink-light',
                     '.local/share/icons/MyCursor-GNOME51', '.local/share/gnome-shell/extensions']
        asset_manifest = {'created': datetime.now().astimezone().isoformat(),
                          'archive': 'appearance.tar.gz',
                          'resources': [{'path': name, 'files': sum(p.is_file() for p in (staging / name).rglob('*'))}
                                        for name in resources]}
        (ROOT / 'assets/manifest.json').write_text(json.dumps(asset_manifest, indent=2) + '\n')
    manifest = {'created': datetime.now().astimezone().isoformat(), 'format': 2, 'home_placeholder': '@HOME@', 'login_shell': pwd.getpwuid(os.getuid()).pw_shell, 'home_files': sum(p.is_file() for p in target.rglob('*')), 'gnome_keys': len(settings), 'system_gnome_keys': len(system_settings), 'system_home_files': sum(p.is_file() for p in service_home.rglob('*')), 'private_keys_excluded': len(skipped)}
    def recipe_count(name):
        return sum(bool(line.strip()) and not line.lstrip().startswith('#') for line in (ROOT / 'packages' / name).read_text().splitlines())
    manifest['appearance_packages'] = {'repo': recipe_count('repo.txt'), 'aur': recipe_count('aur.txt')}
    manifest['system_packages'] = {'repo': recipe_count('system.txt'), 'aur': recipe_count('system-aur.txt')}
    (ROOT / 'snapshot.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest))

if __name__ == '__main__':
    main()
