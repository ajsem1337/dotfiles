import importlib.util
from pathlib import Path
import io
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

restore = load('restore')
system = load('system')

class RestoreTests(unittest.TestCase):
    def fixture(self, root):
        source = root / 'profile'
        (source / 'home/.config').mkdir(parents=True)
        (source / 'home/.config/example.conf').write_text('home=@HOME@\n')
        (source / 'home/.config/binary').write_bytes(b'\x00\xff@HOME@')
        (source / 'assets').mkdir()
        with tarfile.open(source / 'assets/desktop.tar.gz', 'w:gz') as tar:
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
            with tarfile.open(source / 'assets/desktop.tar.gz', 'w:gz') as tar:
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
