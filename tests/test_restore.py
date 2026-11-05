import importlib.util
from pathlib import Path
import io
import json
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

restore = load('restore')
system = load('system')
root_micro = load('configure-root-micro')
keybindings = load('check-keybindings')

class RestoreTests(unittest.TestCase):
    def test_default_package_restore_excludes_optional_system_packages(self):
        recipes = {'repo.txt': ['kitty'], 'aur.txt': ['millennium'],
                   'system.txt': ['nftables'], 'system-aur.txt': ['libcanberra-gtk2']}
        for include_system in (False, True):
            with self.subTest(include_system=include_system), \
                 patch.object(restore, 'lines', side_effect=recipes.__getitem__), \
                 patch.object(restore.shutil, 'which', return_value='/usr/bin/paru'), \
                 patch.object(restore, 'run') as run:
                restore.install_packages(include_system=include_system)
                commands = [call.args[0] for call in run.call_args_list]
                repo_command = next(cmd for cmd in commands if cmd[:2] == ['sudo', 'pacman'])
                self.assertIn('kitty', repo_command)
                self.assertEqual('nftables' in repo_command, include_system)
                self.assertFalse(any('--prepare-repos' in cmd for cmd in commands))
                self.assertTrue(any('millennium' in cmd and cmd[0] == 'paru' for cmd in commands))
                self.assertEqual(any('libcanberra-gtk2' in cmd for cmd in commands), include_system)
        with patch.object(restore, 'lines', side_effect=recipes.__getitem__), \
             patch.object(restore.shutil, 'which', return_value='/usr/bin/paru'), \
             patch.object(restore, 'run') as run:
            restore.install_packages(include_system=True, include_appearance=False)
            commands = [call.args[0] for call in run.call_args_list]
            self.assertFalse(any('kitty' in cmd or 'millennium' in cmd for cmd in commands))
            self.assertTrue(any('nftables' in cmd for cmd in commands))

    def test_shortcut_aliases_and_media_override(self):
        def item(schema, key, value):
            return {'schema': schema, 'key': key, 'value': value, 'schema_dir': None}
        records = [item('org.gnome.desktop.wm.keybindings', 'test-a', "['<Primary><Alt>t']"),
                   item('org.gnome.shell.keybindings', 'test-b', "['<Control><Alt>t']")]
        self.assertEqual(len(keybindings.conflicts(records)[0]), 1)
        records = [item(keybindings.MEDIA, 'volume-up', "['<Control>KP_Add']"),
                   item(keybindings.MEDIA, 'volume-up-static', "['XF86AudioRaiseVolume']"),
                   item('org.gnome.shell.keybindings', 'other', "['XF86AudioRaiseVolume']")]
        self.assertEqual(keybindings.conflicts(records)[0], {})

    def test_appearance_merge_preserves_account_and_plugin_settings(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = self.fixture(base)
            patches = source / 'themes/apps'
            patches.mkdir(parents=True)
            (patches / 'client.json').write_text(json.dumps({'path': '.config/client.json',
                'merge': {'themes': {'activeTheme': 'new'}, 'enabledThemes': ['system24']}}))
            home = base / 'home'
            settings = home / '.config/client.json'
            settings.parent.mkdir(parents=True)
            original = {'themes': {'activeTheme': 'old', 'other': 1}, 'plugins': {'keep': True}, 'account': 'untouched'}
            settings.write_text(json.dumps(original))
            backup, _ = restore.restore_home(home, source)
            result = json.loads(settings.read_text())
            self.assertEqual(result['plugins'], original['plugins'])
            self.assertEqual(result['account'], original['account'])
            self.assertEqual(result['themes'], {'activeTheme': 'new', 'other': 1})
            self.assertEqual(json.loads((backup / '.config/client.json').read_text()), original)
            self.assertEqual(restore.restore_home(home, source)[1], 0)
            settings.write_text('broken json')
            with self.assertRaises(json.JSONDecodeError):
                restore.restore_home(home, source)
            self.assertEqual(settings.read_text(), 'broken json')
            (patches / 'client.json').write_text(json.dumps({'path': '../escape.json', 'merge': {'x': 1}}))
            with self.assertRaises(ValueError):
                restore.restore_home(home, source)
            self.assertFalse((base / 'escape.json').exists())

    def test_system_payload_needs_no_appearance_archive(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = base / 'system'
            payload = source / 'home/.config/easyeffectsrc'
            payload.parent.mkdir(parents=True)
            payload.write_text('[UiSettings]\nColorScheme=CatppuccinMochaPink\n')
            home = base / 'home'
            self.assertEqual(restore.restore_home(home, source)[1], 1)
            self.assertEqual(restore.restore_home(home, source)[1], 0)
            self.assertFalse((home / '.themes').exists())

    def test_all_restores_desktop_and_root_micro_without_system_changes(self):
        with patch.object(restore.sys, 'argv', ['restore.py', '--all']), \
             patch.object(restore, 'install_packages') as packages, \
             patch.object(restore, 'restore_home') as home, \
             patch.object(restore, 'restore_gnome') as gnome, \
             patch.object(restore, 'run') as run:
            restore.main()
        packages.assert_called_once_with(include_system=False, include_appearance=True)
        home.assert_called_once()
        gnome.assert_called_once()
        commands = [list(map(str, call.args[0])) for call in run.call_args_list]
        self.assertTrue(any(cmd[-1].endswith('/configure-root-micro.py') for cmd in commands))
        self.assertFalse(any('--apply' in cmd or '--prepare-repos' in cmd for cmd in commands))

    def test_root_micro_preserves_settings_backups_and_idempotence(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            config, backups = base / 'micro', base / 'backups'
            config.mkdir()
            settings = config / 'settings.json'
            previous = '{"colorscheme": "default", "tabsize": 2}\n'
            settings.write_text(previous)
            root_micro.configure(config, backups)
            self.assertEqual(json.loads(settings.read_text()),
                             {'colorscheme': 'simple', 'syntax': True, 'tabsize': 2})
            self.assertEqual(next(backups.glob('*/settings.json')).read_text(), previous)
            changed = settings.stat().st_mtime_ns
            root_micro.configure(config, backups)
            self.assertEqual(settings.stat().st_mtime_ns, changed)
            self.assertEqual(len(list(backups.glob('*/settings.json'))), 1)
            settings.write_text('invalid json')
            with self.assertRaises(json.JSONDecodeError):
                root_micro.configure(config, backups)
            self.assertEqual(settings.read_text(), 'invalid json')

    def fixture(self, root):
        source = root / 'profile'
        (source / 'home/.config').mkdir(parents=True)
        (source / 'home/.config/example.conf').write_text('home=@HOME@\n')
        (source / 'home/.config/binary').write_bytes(b'\x00\xff@HOME@')
        (source / 'assets').mkdir()
        with tarfile.open(source / 'assets/appearance.tar.gz', 'w:gz') as tar:
            data = b'/* palette */\n'
            item = tarfile.TarInfo('.themes/Test/gtk.css')
            item.size = len(data)
            tar.addfile(item, io.BytesIO(data))
            item = tarfile.TarInfo('.themes/Test/gtk-dark.css')
            item.type = tarfile.SYMTYPE
            item.linkname = 'gtk.css'
            tar.addfile(item)
        return source

    def test_portability_idempotence_and_backup(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = self.fixture(base)
            home = base / 'different-user'
            _, count = restore.restore_home(home, source)
            self.assertGreater(count, 0)
            self.assertEqual((home / '.config/example.conf').read_text(), f'home={home}\n')
            self.assertEqual((home / '.config/binary').read_bytes(), b'\x00\xff@HOME@')
            self.assertEqual((home / '.themes/Test/gtk-dark.css').readlink(), Path('gtk.css'))
            self.assertEqual(restore.restore_home(home, source)[1], 0)
            (home / '.config/example.conf').write_text('local edit')
            backup, _ = restore.restore_home(home, source)
            self.assertEqual((backup / '.config/example.conf').read_text(), 'local edit')

    def test_archive_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = self.fixture(base)
            with tarfile.open(source / 'assets/appearance.tar.gz', 'w:gz') as tar:
                item = tarfile.TarInfo('../escape')
                item.size = 1
                tar.addfile(item, io.BytesIO(b'x'))
            with self.assertRaises(tarfile.FilterError):
                restore.restore_home(base / 'home', source)
            self.assertFalse((base / 'escape').exists())

    def test_destination_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = self.fixture(base)
            home, outside = base / 'home', base / 'outside'
            home.mkdir(); outside.mkdir()
            (home / '.config').symlink_to(outside)
            with self.assertRaises(ValueError):
                restore.restore_home(home, source)
            self.assertFalse((outside / 'example.conf').exists())

    def test_repo_priority_is_stable_and_preserves_mirrors(self):
        initial = '# local\n[options]\nSigLevel = Required DatabaseOptional\n[core]\nInclude = /etc/pacman.d/mirrorlist\n[cachyos-v3]\nInclude = /etc/pacman.d/cachyos-v3-mirrorlist\n[omarchy]\nUsage = Sync Search\n[extra]\nInclude = /etc/pacman.d/mirrorlist\n'
        result = system.repository_config(initial)
        self.assertLess(result.index('[cachyos-v3]'), result.index('[omarchy]'))
        self.assertLess(result.index('[omarchy]'), result.index('[core]'))
        self.assertIn('Usage = All', result)
        self.assertEqual(result.count('[omarchy]'), 1)
        self.assertEqual(system.repository_config(result), result)
        self.assertIn('/etc/pacman.d/cachyos-v3-mirrorlist', result)

if __name__ == '__main__':
    unittest.main()
