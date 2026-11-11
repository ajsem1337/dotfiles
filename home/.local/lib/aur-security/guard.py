"""Pre-execution Traur gate for makepkg. This is a scanner, not a sandbox."""

import getopt
import configparser
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import time

HOME = Path.home()
INSTALL = HOME / ".local/opt/traur-security"
SCANNER = INSTALL / "bin/traur"
REPORTS = HOME / ".local/state/aur-security/reports"
PROVENANCE = HOME / ".local/state/aur-security/provenance"
REAL_MAKEPKG = "/usr/bin/makepkg"
SHORT_OPTIONS = "AcCdD:efFghiLmop:rRsSV"
LONG_OPTIONS = [
    "allsource", "check", "clean", "cleanbuild", "config=", "dir=", "force", "geninteg",
    "help", "holdver", "ignorearch", "install", "key=", "log", "noarchive", "nobuild",
    "nocolor", "nocheck", "nodeps", "noextract", "noprepare", "nosign", "packagelist",
    "printsrcinfo", "repackage", "rmdeps", "sign", "skipchecksums", "skipinteg",
    "skippgpcheck", "source", "syncdeps", "verifysource", "version", "asdeps",
    "noconfirm", "needed", "noprogressbar",
]
ALLOWED = {"Trusted", "Ok"}


class Blocked(Exception):
    pass


def safe_text(value):
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "?", str(value))[:800]


def request_directory(argv, cwd):
    """Parse options without sourcing the PKGBUILD, including metadata calls."""
    try:
        options, trailing = getopt.gnu_getopt(argv, SHORT_OPTIONS, LONG_OPTIONS)
    except getopt.GetoptError as error:
        raise Blocked(f"Unsupported makepkg arguments: {error}") from error
    if any(option in ("-h", "--help", "-V", "--version") for option, _ in options):
        return None
    directory = Path(cwd)
    script = "PKGBUILD"
    fakeroot = any(option == "-F" for option, _ in options)
    for option, value in options:
        if option in ("-D", "--dir"):
            if not fakeroot:
                directory = Path(value) if Path(value).is_absolute() else Path(cwd) / value
        elif option == "-p":
            script = value
        elif option in ("--skipchecksums", "--skipinteg", "--skippgpcheck"):
            raise Blocked("Source integrity/signature checks must not be disabled.")
    # makepkg accepts environment overrides after options. Do not accept overrides
    # that can select a different input file or executable after the scan.
    allowed_overrides = {"CFLAGS", "CXXFLAGS", "CPPFLAGS", "LDFLAGS", "MAKEFLAGS", "RUSTFLAGS", "CC", "CXX"}
    for argument in trailing:
        name, separator, _ = argument.partition("=")
        if not separator or name.rstrip("+") not in allowed_overrides:
            raise Blocked(f"Unsupported makepkg environment override: {safe_text(name)}")
    directory = directory.resolve(strict=True)
    candidate = directory / script
    if candidate.absolute() != directory / "PKGBUILD":
        raise Blocked("Alternate build scripts are not covered; use the standard PKGBUILD filename.")
    if not candidate.exists():
        raise Blocked(f"No PKGBUILD in {safe_text(directory)}")
    if candidate.is_symlink() or not candidate.is_file():
        raise Blocked("PKGBUILD must be a regular, non-symlink file.")
    return directory


def fingerprint(directory):
    """Detect input edits during scanning; never cache an approval by package name."""
    digest = hashlib.sha256()
    count = 0
    for parent, dirs, files in os.walk(directory, followlinks=False):
        # Generated build outputs are not AUR recipes. They are NOT claimed to
        # have been audited by this gate; downloaded/upstream code is a limitation.
        if Path(parent) == directory:
            dirs[:] = [name for name in dirs if name not in {".git", "src", "pkg"}]
        dirs.sort()
        for name in sorted(dirs + files):
            path = Path(parent) / name
            relative = str(path.relative_to(directory))
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode):
                raise Blocked(f"Recipe symlinks require review: {safe_text(relative)}")
            if stat.S_ISDIR(info.st_mode):
                continue
            if not stat.S_ISREG(info.st_mode):
                raise Blocked(f"Non-regular recipe input: {safe_text(relative)}")
            count += 1
            if count > 4096:
                raise Blocked("Too many local inputs to check automatically.")
            digest.update(relative.encode() + b"\0")
            digest.update(f"{info.st_size}:{info.st_mtime_ns}:{info.st_ctime_ns}".encode())
            if info.st_size <= 1024 * 1024:
                with path.open("rb") as source:
                    digest.update(source.read(1024 * 1024 + 1))
    return digest.hexdigest()


def scanner_environment():
    # No caller-controlled ignore list, whitelist, loader or Python environment.
    return {
        "PATH": "/usr/bin:/bin", "HOME": str(HOME), "LANG": "C.UTF-8",
        "XDG_CONFIG_HOME": str(INSTALL / "guard-config"),
        "XDG_CACHE_HOME": str(HOME / ".cache"),
        "NO_COLOR": "1",
    }


def verdict_allowed(result, returncode=0):
    return (
        isinstance(result, dict) and result.get("schema_version") == 2
        and result.get("status") == "complete" and result.get("tier") in ALLOWED
        and type(result.get("score")) is int and 0 <= result["score"] <= 100
        and isinstance(result.get("signals"), list)
        and result.get("override_gate_fired") is None and returncode == 0
    )


def run_scan(directory, scanner=SCANNER, timeout=45, package=None):
    if not scanner.is_file() or not os.access(scanner, os.X_OK):
        raise Blocked("Traur is unavailable; nothing was checked.")
    arguments = [package] if package else ["--dir", str(directory)]
    process = subprocess.Popen(
        [str(scanner), "scan", *arguments, "--json"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        env=scanner_environment(), start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise Blocked("Traur timed out; nothing has been approved.") from None
    try:
        result = json.loads(stdout)
    except (ValueError, TypeError):
        raise Blocked(f"Traur returned no valid report: {safe_text(stderr)}") from None
    if not isinstance(result, dict) or result.get("schema_version") != 2:
        raise Blocked("Unrecognized Traur report format.")
    return result, verdict_allowed(result, process.returncode)


def aur_package(directory):
    """Read static metadata, never shell-evaluate it (split packages included)."""
    in_helper_cache = any(directory.is_relative_to(cache) for cache in (
        HOME / ".cache/paru/clone", HOME / ".cache/yay",
    ))
    origin = ""
    config = directory / ".git/config"
    if config.is_file() and not config.is_symlink():
        parser = configparser.ConfigParser(interpolation=None, strict=False)
        try:
            parser.read_string(config.read_text())
            origin = parser.get('remote "origin"', "url", fallback="")
        except (OSError, UnicodeError, configparser.Error):
            raise Blocked("Cannot read the recipe's repository identity.") from None
    match = re.fullmatch(r"(?:https://aur\.archlinux\.org/|ssh://aur@aur\.archlinux\.org/|aur@aur\.archlinux\.org:)([A-Za-z0-9@._+-]+?)(?:\.git)?", origin)
    if not in_helper_cache and not match:
        return None
    base = match.group(1) if match else directory.name
    package = base
    srcinfo = directory / ".SRCINFO"
    if srcinfo.is_file():
        for line in srcinfo.read_text().splitlines():
            key, separator, value = line.strip().partition(" = ")
            if separator and key == "pkgname":
                package = value
                break
    if not re.fullmatch(r"[A-Za-z0-9@._+-]+", package) or ".." in package or package.startswith("-"):
        raise Blocked("Invalid package identity in AUR metadata.")
    return package


def provenance_check(directory, fingerprint_value, package, scanner=SCANNER, cache=PROVENANCE):
    """Short content-bound cache for network checks; local code is ALWAYS rescanned."""
    scanner_hash = hashlib.sha256(scanner.read_bytes()).hexdigest()
    key = hashlib.sha256(f"{package}:{fingerprint_value}:{scanner_hash}:v1".encode()).hexdigest()
    cache.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = cache / f"{key}.json"
    try:
        cached = json.loads(path.read_text())
        if 0 <= time.time() - cached["checked_at"] < 600 and verdict_allowed(cached["result"]):
            return cached["result"], True
    except (OSError, ValueError, KeyError, TypeError):
        pass
    print(f"[AUR protection] Checking AUR identity/history for {safe_text(package)}…", file=sys.stderr)
    result, allowed = run_scan(directory, scanner=scanner, timeout=90, package=package)
    if allowed:
        temporary = cache / f".{key}.{time.time_ns()}.{os.getpid()}.tmp"
        with open(temporary, "x", opener=lambda name, flags: os.open(name, flags, 0o600)) as destination:
            json.dump({"checked_at": int(time.time()), "result": result}, destination)
        temporary.replace(path)
    return result, allowed


def save_report(directory, fingerprint_value, result, reports=REPORTS):
    reports.mkdir(mode=0o700, parents=True, exist_ok=True)
    record = {"checked_at": int(time.time()), "directory": str(directory), "input_fingerprint": fingerprint_value, "result": result}
    path = reports / f"{time.time_ns()}-{os.getpid()}.json"
    with open(path, "x", opener=lambda name, flags: os.open(name, flags, 0o600)) as destination:
        json.dump(record, destination, ensure_ascii=True, indent=2)
    return path


def inconclusive(directory, error):
    return {"schema_version": 2, "package": directory.name, "status": "incomplete",
            "tier": "Unknown", "score": 0, "signals": [], "override_gate_fired": None,
            "reason": str(error)}


def gate(directory, scanner=SCANNER, reports=REPORTS):
    before = fingerprint(directory)
    try:
        result, allowed = run_scan(directory, scanner=scanner)
    except Blocked as error:
        result, allowed = inconclusive(directory, error), False
    report = save_report(directory, before, result, reports=reports)
    package = aur_package(directory)
    if allowed and package:
        try:
            result, allowed = provenance_check(directory, before, package, scanner=scanner)
        except Blocked as error:
            result, allowed = inconclusive(directory, error), False
        report = save_report(directory, before, result, reports=reports)
    if before != fingerprint(directory):
        raise Blocked("Recipe inputs changed during the scan. Run the command again.")
    if not allowed:
        print(f"[AUR protection] STOP: {safe_text(result.get('tier', 'Unknown'))}", file=sys.stderr)
        findings = result.get("signals", [])
        for finding in (findings if isinstance(findings, list) else [])[:12]:
            if isinstance(finding, dict) and finding.get("role") not in ("Fact", "Provenance"):
                print(f"  {safe_text(finding.get('id'))}: {safe_text(finding.get('description'))}", file=sys.stderr)
        if result.get("reason"):
            print(f"  {safe_text(result['reason'])}", file=sys.stderr)
        raise Blocked(f"Build stopped. Report: {report}\nThere is no Enter-to-continue override; review the report first.")
    # stdout is reserved for makepkg: paru parses --printsrcinfo/--packagelist.
    print(f"[AUR protection] {safe_text(result.get('package', directory.name))}: local recipe scan passed (not a safety guarantee).", file=sys.stderr)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        directory = request_directory(argv, Path.cwd())
        if directory is not None:
            gate(directory)
        # This is the original system binary, not this PATH wrapper again.
        environment = dict(os.environ)
        for name in list(environment):
            if name in {"BUILDFILE", "CHDIR", "BASH_ENV", "ENV", "LD_PRELOAD", "LD_LIBRARY_PATH"} or name.startswith("BASH_FUNC_"):
                environment.pop(name)
        os.execve(REAL_MAKEPKG, [REAL_MAKEPKG, *argv], environment)
    except (Blocked, OSError, ValueError, UnicodeError, subprocess.SubprocessError) as error:
        for index, line in enumerate(str(error).splitlines()[:8]):
            prefix = "[AUR protection] BLOCKED: " if index == 0 else "  "
            print(prefix + safe_text(line), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
