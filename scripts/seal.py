#!/usr/bin/env python3
"""Rebuild checksums of portable payload, not build caches or Git internals."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
checksums = {}
for name in ('home', 'system', 'gnome', 'packages', 'assets', 'themes'):
    for p in sorted((root / name).rglob('*')):
        if p.is_file() and not p.is_symlink():
            checksums[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
for p in [root / 'restore.sh', root / 'snapshot.json', *sorted((root / 'scripts').glob('*.py'))]:
    checksums[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
(root / 'checksums.json').write_text(json.dumps(checksums, indent=2) + '\n')
print('Sealed files:', len(checksums))
