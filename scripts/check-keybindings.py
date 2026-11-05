#!/usr/bin/env python3
"""Compare effective GNOME/extension shortcuts using GTK's accelerator parser."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, Gio, GLib, Gtk

ROOT = Path(__file__).resolve().parents[1]
CORE = ('org.gnome.desktop.wm.keybindings', 'org.gnome.mutter.keybindings',
        'org.gnome.mutter.wayland.keybindings', 'org.gnome.shell.keybindings',
        'org.gnome.settings-daemon.plugins.media-keys')
MEDIA = CORE[-1]


def live_items():
    source = Gio.SettingsSchemaSource.get_default()
    settings = []
    enabled = Gio.Settings.new('org.gnome.shell').get_strv('enabled-extensions')
    sources = [(source, CORE, None)]
    for uuid in enabled:
        for root in (Path.home() / '.local/share/gnome-shell/extensions', Path('/usr/share/gnome-shell/extensions')):
            directory = root / uuid / 'schemas'
            if (directory / 'gschemas.compiled').is_file():
                sub = Gio.SettingsSchemaSource.new_from_directory(str(directory), source, False)
                sources.append((sub, sub.list_schemas(False)[0], str(directory)))
                break
    for src, ids, directory in sources:
        for schema_id in ids:
            schema = src.lookup(schema_id, True)
            if schema is None or schema.get_path() is None:
                continue
            obj = Gio.Settings.new_full(schema, None, None)
            for key in schema.list_keys():
                settings.append({'schema': schema_id, 'key': key, 'value': obj.get_value(key).print_(True), 'schema_dir': directory})
    for path in Gio.Settings.new(MEDIA).get_strv('custom-keybindings'):
        obj = Gio.Settings.new_with_path(MEDIA + '.custom-keybinding', path)
        settings.append({'schema': MEDIA + '.custom-keybinding', 'path': path, 'key': 'binding',
                         'value': obj.get_value('binding').print_(True), 'schema_dir': None})
    return settings


def conflicts(items):
    records = {(item['schema'], item['key'], item.get('path')): item for item in items}
    enabled_record = records.get(('org.gnome.shell', 'enabled-extensions', None))
    enabled = set(GLib.Variant.parse(None, enabled_record['value'], None, None).unpack()) if enabled_record else None
    by_accelerator = defaultdict(set)
    for item in items:
        schema, key = item['schema'], item['key']
        if schema not in CORE and not schema.endswith('.custom-keybinding') and not item.get('schema_dir'):
            continue
        if item.get('schema_dir') and enabled is not None and Path(item['schema_dir']).parts[-2] not in enabled:
            continue
        # Tiling Shell stores modifier choices as numeric strings, not accelerators.
        if key.endswith('activation-key') or key == 'custom-keybindings':
            continue
        if schema == MEDIA and key.endswith('-static'):
            override = records.get((schema, key[:-7], None))
            if override and any(GLib.Variant.parse(None, override['value'], None, None).unpack()):
                continue
        value = GLib.Variant.parse(None, item['value'], None, None)
        if value.get_type_string() == 's' and key != 'binding':
            continue
        if value.get_type_string() not in ('s', 'as'):
            continue
        values = [value.unpack()] if value.get_type_string() == 's' else value.unpack()
        action = schema + ':' + key + (':' + item['path'] if item.get('path') else '')
        for accelerator in values:
            if not accelerator:
                continue
            # On Linux Primary means Control. Resolve aliases before GTK asks
            # for a display keymap, so the exported profile is checkable offline.
            accelerator = accelerator.replace('<Primary>', '<Control>').replace('<Ctrl>', '<Control>')
            keyval, modifiers = Gtk.accelerator_parse(accelerator)
            if keyval:
                # accelerator_name() consults a display keymap even for a
                # stored profile. Keep canonical modifier masks without it.
                tags = [(Gdk.ModifierType.CONTROL_MASK, 'Control'),
                        (Gdk.ModifierType.SHIFT_MASK, 'Shift'),
                        (Gdk.ModifierType.MOD1_MASK, 'Alt'),
                        (Gdk.ModifierType.SUPER_MASK, 'Super'),
                        (Gdk.ModifierType.META_MASK, 'Meta'),
                        (Gdk.ModifierType.HYPER_MASK, 'Hyper')]
                name = ''.join('<' + tag + '>' for mask, tag in tags if modifiers & mask)
                name += Gdk.keyval_name(keyval)
                by_accelerator[name].add(action)
    return {key: sorted(actions) for key, actions in sorted(by_accelerator.items()) if len(actions) > 1}, len(by_accelerator)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true', help='Read current session instead of the exported profile.')
    args = parser.parse_args()
    items = live_items() if args.live else json.loads((ROOT / 'gnome/settings.json').read_text())
    collisions, count = conflicts(items)
    for accelerator, actions in collisions.items():
        print(accelerator + ': ' + ' / '.join(actions))
    if collisions:
        return 1
    print(f'OK: {count} effective GNOME/extension/custom shortcuts; no duplicate accelerators.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
