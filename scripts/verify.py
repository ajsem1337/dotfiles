#!/usr/bin/env python3
"""Verify manifest, paths, checksums, and common credential formats."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {'.aws', '.ssh', '.gnupg', 'hosts.yml', 'cookies.sqlite', 'cookies0.db', 'login.keyring', 'Login Data', 'fish_history'}
PATTERNS = [
    re.compile(r'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----'),
    re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),
    re.compile(r'(?i)(?:password|access_token|api_key|client_secret)\s*[=:]\s*["\']([^"\'\n]{12,})["\']'),
    re.compile(r'https?://[^/\s:@]+:[^/\s@]+@'),
]

def main():
    errors = []
    manifest = ROOT / 'checksums.json'
    if manifest.exists():
        for relative, expected in json.loads(manifest.read_text()).items():
            p = ROOT / relative
            if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != expected:
                errors.append('Checksum: ' + relative)
    paths = list((ROOT / 'home').rglob('*')) + list((ROOT / 'system').rglob('*')) + list((ROOT / 'gnome').rglob('*'))
    for p in paths:
        if any(part in FORBIDDEN for part in p.relative_to(ROOT).parts):
            errors.append('Forbidden path: ' + str(p.relative_to(ROOT)))
        if p.is_file() and not p.is_symlink():
            try:
                text = p.read_text()
            except UnicodeError:
                continue
            if any(pattern.search(text) for pattern in PATTERNS):
                errors.append('Possible credential: ' + str(p.relative_to(ROOT)))
            if '/home/ajsem' in text:
                errors.append('Non-portable home: ' + str(p.relative_to(ROOT)))
    with tarfile.open(ROOT / 'assets/desktop.tar.gz') as archive:
        for item in archive:
            name = PurePosixPath(item.name)
            if name.is_absolute() or '..' in name.parts or any(part in FORBIDDEN or part == '.git' for part in name.parts):
                errors.append('Unsafe archive path: ' + item.name)
            if item.islnk() or item.issym():
                if PurePosixPath(item.linkname).is_absolute():
                    errors.append('Absolute archive link: ' + item.name)
            if item.isfile() and item.size < 5_000_000 and Path(item.name).suffix in ('.js', '.json', '.xml', '.conf', '.ini', '.txt'):
                raw = archive.extractfile(item).read()
                try:
                    text = raw.decode('utf-8')
                except UnicodeError:
                    continue
                if any(pattern.search(text) for pattern in PATTERNS):
                    errors.append('Possible credential in asset: ' + item.name)
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print('OK: checksums, portable paths, archive layout and credential patterns.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
