# AUR pre-execution gate

This documents my local integration, not upstream Traur behavior. The source in
`home/.local/lib/aur-security/` is portable to the installing user's home;
no generated scan reports or installed binaries are included.

## Reproducing the scanner

Install the Rust toolchain and normal build dependencies first. Review the
upstream revision and the patch before building. From the root of this repo:

```sh
git clone https://github.com/Sohimaster/traur "$HOME/.local/src/traur-security"
git -C "$HOME/.local/src/traur-security" switch --detach 2ae91ec0a5029c734398f47e35b09fed1d4faf6d
git -C "$HOME/.local/src/traur-security" apply "$PWD/aur/traur/local-policy.patch"
cp aur/traur/Cargo.lock "$HOME/.local/src/traur-security/Cargo.lock"
cargo test --locked --manifest-path "$HOME/.local/src/traur-security/Cargo.toml"
cargo build --release --locked --bin traur --manifest-path "$HOME/.local/src/traur-security/Cargo.toml"
install -Dm755 "$HOME/.local/src/traur-security/target/release/traur" "$HOME/.local/opt/traur-security/bin/traur"
```

Use an unused source directory; do not overwrite a checkout with local changes.
Copy `home/.local/lib/aur-security/` to `~/.local/lib/aur-security/`, and install
the two reviewed wrappers under `~/.local/bin/` as executable files. Ensure that
directory precedes `/usr/bin` in PATH. This does not install the upstream ALPM
hook or its makepkg wrapper.

For paru, back up and edit your own `~/.config/paru/paru.conf`. Keep your existing
options (on CachyOS mine include `Include = /etc/paru.conf` under `[options]`).
Under `[bin]`, set `Makepkg` to the **absolute path** of your installed wrapper,
for example `/home/YOUR_USER/.local/bin/makepkg`. Do not paste `YOUR_USER`
literally or rely on shell-variable expansion in paru's config. Other helpers
need their own equivalent integration.

Run the included Python tests before enabling the gate. An unavailable scanner
must block a build, not silently fall back to unscanned execution. The included
Python tests exercise the installed scanner when available; rebuilding the
scanner requires the Rust toolchain, and updates still need review.

Traur is an additional heuristic scanner, **not a sandbox or a guarantee that
software is safe**. The integration covers normal `paru` calls (including those
from Pacseek) through an explicit `[bin] Makepkg` path, plus manual `makepkg`
commands resolved through `~/.local/bin`. `/usr/bin/makepkg`, a helper with an
explicit different Makepkg setting, and direct installation of package archives
can bypass it. It does not claim to enforce a system-wide security boundary.

## Policy

- Scan the local PKGBUILD directory **before every makepkg invocation** that
  reads a recipe, including `--printsrcinfo`, `--packagelist`, source downloads
  and fakeroot packaging. Never `source` or evaluate it to obtain its name.
- Allow only complete `Trusted`/`Ok` reports. Stop for Sketchy, Suspicious,
  Malicious, Unknown, a missing/crashed scanner, timeout, invalid JSON or input
  changes while checking. No interactive bypass or package-name whitelist.
- For recipes identified as AUR clones, also run the scanner's remote
  identity/history analysis. A missing report or connection error blocks the
  operation. Successful remote reports are cached for 10 minutes, bound to the
  input fingerprint and scanner binary. Local code is rescanned on every call.
- Guard scans use their own default scanner configuration, not user ignore
  rules. They do not disable PGP checks or checksums.
- Preserve makepkg stdout for the helper's metadata parsing; messages go to
  stderr. Private JSON reports are in `~/.local/state/aur-security/reports/`.
- All existing repo preferences remain unchanged. No repos, mirror tools,
  sudo policy, antivirus suites, timers or VirusTotal uploads are added.

## Scanner build

Upstream: https://github.com/Sohimaster/traur

Base commit: `2ae91ec0a5029c734398f47e35b09fed1d4faf6d` (Traur 0.6.0).
Local source and lockfile: `~/.local/src/traur-security`.
Installed binary: `~/.local/opt/traur-security/bin/traur`.

Three local changes are intentional:

1. Reqwest uses Rustls and system certificate roots instead of native OpenSSL,
   because the upstream locked openssl-sys version does not build with OpenSSL 4.
2. The local-directory CLI marks skipped/capped sources and an unreadable
   declared install script as an incomplete JSON report instead of hiding those
   warnings in JSON mode. The guard blocks such reports. Renamed remote
   downloads (`filename::https://...`) are classified by their URL, so an
   already downloaded binary is not mistaken for an oversized committed script.
3. A failed refresh of Traur's cached AUR Git checkout returns an error rather
   than silently analysing its stale copy as if it had been refreshed.

The upstream ALPM hook and makepkg wrapper are **not installed**. The former is
too late to prevent build-time code execution; the latter sources PKGBUILD
before scanning and skips metadata calls.

## Limits

The automatic gate uses local code analysis, with additional remote checks for
AUR-origin recipes and paru/yay cache directories. A local project outside those
locations gets local analysis only. The scanner's historical incident list is supplementary:
upstream can silently use stale data or omit it when fetching fails. It is not
a complete, continuously authoritative malware registry.

Dynamic shell behavior, downloaded source code, compiler/build dependencies,
and the installed program can evade static checks. A clean recipe can still
build malicious upstream code. Build outputs (`src/`, `pkg/`) are not audited
by the input fingerprint, and concurrent changes cannot be excluded atomically
between checking and execution. No source-build isolation is enabled here.

Scanner/rules updates are manual, not managed by pacman: review upstream changes,
reapply the local patches, test and rebuild with the recorded Cargo.lock before
replacing the binary. Do not assume the local 0.6.0 build updates automatically.

## Tests

```sh
python3 -B -m unittest discover -s ~/.local/lib/aur-security -p 'test_*.py' -v
```
