#!/usr/bin/env python3
"""Privileged, explicit allowlist. Never restore boot/device/user identity."""
from datetime import datetime
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FINGERPRINT = '40DFB630FF42BCFFB047046CF0134EE680CAC571'
FILES = (
    'etc/nftables.conf', 'etc/sysctl.d/99-network-hardening.conf',
    'etc/udev/rules.d/70-lc87.rules', 'etc/udev/rules.d/99-powercap.rules',
    'etc/systemd/resolved.conf.d/20-avahi-mdns.conf',
    'etc/systemd/system/nftables.service.d/override.conf',
    'etc/scx_loader/config.toml',
)

def run(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, **kwargs)

def repository_config(text):
    matches = list(re.finditer(r'(?m)^\[([^\]]+)\]\s*$', text))
    prefix = text[:matches[0].start()] if matches else ''
    sections = []
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        if match.group(1) != 'omarchy':
            sections.append((match.group(1), text[match.start():end].rstrip() + '\n\n'))
    cachy = [s for name, s in sections if name.startswith('cachyos')]
    if not cachy:
        raise RuntimeError('Brak repozytoriów CachyOS. Ten profil systemowy jest przeznaczony dla CachyOS.')
    options = [s for name, s in sections if name == 'options']
    remaining = [s for name, s in sections if name != 'options' and not name.startswith('cachyos')]
    omarchy = '[omarchy]\nSigLevel = Required DatabaseOptional\nServer = https://pkgs.omarchy.org/stable/$arch\nUsage = All\n\n'
    return prefix + ''.join(options + cachy + [omarchy] + remaining)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--prepare-repos', action='store_true')
    p.add_argument('--apply', action='store_true')
    args = p.parse_args()
    if os.geteuid() != 0:
        p.error('Ten etap wymaga sudo.')
    backup = Path('/var/backups') / ('dotfiles-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True, mode=0o700)

    def save(path):
        if path.exists() or path.is_symlink():
            dest = backup / str(path).lstrip('/')
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest, follow_symlinks=False)

    if args.prepare_repos:
        path = Path('/etc/pacman.conf')
        new = repository_config(path.read_text())
        save(path)
        path.write_text(new)
        known = subprocess.run(['pacman-key', '--list-keys', FINGERPRINT], capture_output=True).returncode == 0
        if not known:
            run('pacman-key', '--keyserver', 'hkps://keys.openpgp.org', '--recv-keys', FINGERPRINT)
        run('pacman-key', '--lsign-key', FINGERPRINT)
    if args.apply:
        for package in ('nftables', 'nss-mdns', 'avahi'):
            run('pacman', '-Q', package, stdout=subprocess.DEVNULL)
        tables = json.loads(subprocess.check_output(['nft', '-j', 'list', 'tables'], text=True))['nftables']
        allowed = {('ip', 'filter'), ('ip6', 'filter'), ('inet', 'filter')}
        for item in tables:
            if 'table' in item:
                t = item['table']
                if (t['family'], t['name']) not in allowed:
                    raise RuntimeError('Istnieją dodatkowe reguły zapory. Obejrzyj nft list ruleset przed odtworzeniem profilu.')
        old_ufw = []
        for family in ('ip', 'ip6'):
            r = subprocess.run(['nft', '-j', 'list', 'table', family, 'filter'], capture_output=True, text=True)
            if r.returncode:
                continue
            items = json.loads(r.stdout)['nftables']
            for item in items:
                if 'chain' in item:
                    name = item['chain']['name']
                    if name not in ('INPUT', 'OUTPUT', 'FORWARD') and not name.startswith('ufw'):
                        raise RuntimeError('Tabela filter zawiera reguły inne niż UFW; zachowano je bez zmian.')
                if 'rule' in item:
                    rule = item['rule']
                    if not rule['chain'].startswith('ufw') and not any(expr.get('jump', {}).get('target', '').startswith('ufw') for expr in rule['expr']):
                        raise RuntimeError('Własne reguły iptables wymagają ręcznego przeglądu.')
            old_ufw.append(family)
        (backup / 'nft-ruleset.txt').write_text(subprocess.check_output(['nft', 'list', 'ruleset'], text=True))
        for cmd in ('iptables-save', 'ip6tables-save'):
            if shutil.which(cmd):
                (backup / (cmd + '.rules')).write_text(subprocess.check_output([cmd], text=True))
        for relative in FILES:
            src, dest = ROOT / 'system' / relative, Path('/') / relative
            assert src.is_file() and not src.is_symlink(), src
            save(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
            dest.chmod(0o644)
        path = Path('/etc/nsswitch.conf')
        save(path)
        text = re.sub(r'(?m)^hosts:.*$', 'hosts: mymachines mdns_minimal [NOTFOUND=return] resolve [!UNAVAIL=return] files myhostname dns', path.read_text())
        path.write_text(text)
        run('udevadm', 'verify', '/etc/udev/rules.d/99-powercap.rules')
        run('udevadm', 'control', '--reload-rules')
        run('systemctl', 'daemon-reload')
        run('nft', '--check', '--file', '/etc/nftables.conf')
        run('nft', '--file', '/etc/nftables.conf')
        run('systemctl', 'enable', '--now', 'nftables.service')
        # New filtering is in place before the old UFW stack is stopped.
        if subprocess.run(['systemctl', 'cat', 'ufw.service'], capture_output=True).returncode == 0:
            run('systemctl', 'disable', '--now', 'ufw.service')
        for family in old_ufw:
            run('nft', 'delete', 'table', family, 'filter')
        installed = [name for name in ('ufw-extras', 'ufw') if subprocess.run(['pacman', '-Q', name], capture_output=True).returncode == 0]
        if installed:
            run('pacman', '-Rns', '--noconfirm', '--', *installed)
        for unit in ('NetworkManager.service', 'systemd-resolved.service', 'avahi-daemon.service', 'gdm.service', 'power-profiles-daemon.service', 'scx_loader.service'):
            if subprocess.run(['systemctl', 'cat', unit], capture_output=True).returncode == 0:
                run('systemctl', 'enable', unit)
        run('systemctl', 'start', 'avahi-daemon.service', 'systemd-resolved.service')
        run('systemctl', 'reload', 'systemd-resolved.service')
        run('getent', 'ahostsv4', 'archlinux.org')
        print('Nie przełączano aktywnego menedżera logowania ani schedulera; nowe ustawienia zostaną użyte przy kolejnym logowaniu/starcie.')
    print('Kopie systemowe:', backup)

if __name__ == '__main__':
    main()
