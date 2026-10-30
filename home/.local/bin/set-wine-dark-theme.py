#!/usr/bin/env python3
"""Set winecfg's native dark appearance while all Wine servers are stopped."""
from pathlib import Path
from datetime import datetime
import os
import re
import shutil
import stat
import tempfile

SECTION = r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize"
VALUES = {"AppsUseLightTheme": "dword:00000000", "SystemUsesLightTheme": "dword:00000000"}


def dark_registry(text):
    """Change only two appearance values in Wine's registry-file format."""
    if not text.startswith("WINE REGISTRY Version 2"):
        raise ValueError("Nieznany format rejestru Wine")
    newline = "\r\n" if "\r\n" in text else "\n"
    header = "[" + SECTION + "]"
    pattern = re.compile(r"^" + re.escape(header) + r"[^\r\n]*\r?\n(.*?)(?=^\[|\Z)", re.M | re.S)
    match = pattern.search(text)
    if match:
        body = match.group(1)
        for key, value in VALUES.items():
            line = '"' + key + '"=' + value
            value_pattern = re.compile(r'^"' + re.escape(key) + r'"=[^\r\n]*', re.M)
            if value_pattern.search(body):
                body = value_pattern.sub(line, body)
            else:
                body = body.rstrip("\r\n") + newline + line + newline + newline
        return text[:match.start(1)] + body + text[match.end(1):]
    block = header + newline + newline.join('"' + k + '"=' + v for k, v in VALUES.items())
    return text.rstrip("\r\n") + newline + newline + block + newline


def wine_servers():
    found = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            if proc.stat().st_uid != os.getuid():
                continue
            name = (proc / "comm").read_text().strip().lower()
            if name.startswith("wineserver") or name in {"wine", "wine64", "wine-preloader", "wine64-preloade", "wineboot.exe"}:
                found.append(proc.name + ": " + name)
        except (FileNotFoundError, ProcessLookupError):
            pass
        except PermissionError:
            raise SystemExit("Nie można sprawdzić procesu. Niczego nie zmieniono.")
    return found


def main():
    active = wine_servers()
    if active:
        raise SystemExit("Zamknij gry i launchery Wine/Proton, a potem uruchom ponownie. Aktywne: " + ", ".join(active))
    home = Path.home()
    prefixes = [home / ".wine"]
    root = Path("/games/lutris")
    if root.is_dir():
        prefixes.extend(sorted(root.iterdir()))
    changes = []
    for prefix in prefixes:
        registry = prefix / "user.reg"
        if not registry.is_file():
            continue
        before = registry.read_bytes()
        after = dark_registry(before.decode("utf-8")).encode("utf-8")
        if after != before:
            if not os.access(registry, os.W_OK) or not os.access(prefix, os.W_OK):
                raise SystemExit("Brak prawa zapisu: " + str(registry) + ". Niczego nie zmieniono.")
            changes.append((registry, before, after))
    if not changes:
        print("Brak zmian: odnalezione prefixy mają już ustawiony ciemny wygląd.")
        return
    backup = home / ".local/share/config-backups" / datetime.now().strftime("%Y%m%d-%H%M%S-wine-dark")
    for registry, before, after in changes:
        dest = backup / registry.relative_to("/")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(registry, dest)
    if wine_servers() or any(p.read_bytes() != before for p, before, _ in changes):
        raise SystemExit("Wine uruchomiło się lub rejestr zmienił się w trakcie sprawdzania. Nie zapisano zmian.")
    written = []
    try:
        for registry, before, after in changes:
            mode = stat.S_IMODE(registry.stat().st_mode)
            with tempfile.NamedTemporaryFile(dir=registry.parent, prefix=".dark-theme-", delete=False) as temp:
                temp.write(after)
                name = Path(temp.name)
            try:
                name.chmod(mode)
                if registry.read_bytes() != before or wine_servers():
                    raise RuntimeError("Rejestr lub stan Wine zmienił się przed zapisem")
                os.replace(name, registry)
                written.append(registry)
                assert registry.read_bytes() == after
            finally:
                name.unlink(missing_ok=True)
            print("Ciemny wygląd:", registry.parent)
    except Exception:
        for registry in written:
            shutil.copy2(backup / registry.relative_to("/"), registry)
        raise
    print("Kopie rejestrów:", backup)
    print("Gotowe. Wygląd zostanie odczytany przy następnym uruchomieniu Wine. Aplikacje z własnym UI mogą go ignorować.")


if __name__ == "__main__":
    main()
