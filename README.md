# My terminal layer on Umbriel + Noctalia

CachyOS · Wayland · [Umbriel](https://github.com/noctalia-dev/umbriel) ·
[Noctalia](https://github.com/noctalia-dev/noctalia) · Kitty · Fish

I moved away from GNOME. Noctalia already does most of the cross-application
theming I used to maintain myself, so this is **not another full desktop rice**.
It is my small layer on top: terminal configuration, a few helpers and the
wallpaper I use. Generated themes and third-party template collections do not
belong here.

The retired GNOME setup is reduced to a few references on the
[`gnome` branch](https://github.com/ajsem1337/dotfiles/tree/gnome).
Old commits remain available, but neither that branch nor `main` is a GNOME
restore toolkit anymore.

## Palette and upstream sources

The active palette is **[Catppuccin Mocha Mauve-Lavender](https://github.com/noctalia-dev/community-palettes/tree/main/Catppuccin%20Mocha%20Mauve-Lavender)**,
in dark mode: Mocha background, Mauve primary accent, Lavender secondary accent.
[Catppuccin](https://github.com/catppuccin/catppuccin) and the Noctalia palette/template
authors deserve the theme credit; these are not my themes.

Select that community palette in Noctalia, then enable the integrations you use.
The generated application files are intentionally excluded from this repository.

### Official / built-in templates

[Noctalia's built-in templates](https://github.com/noctalia-dev/noctalia/tree/main/assets/templates)
are the source of truth for my enabled `gtk3`, `gtk4`, `kcolorscheme`, `kitty`,
`qt`, `umbriel` and `btop` integrations. GTK3 uses `adw-gtk3-dark`; icons are
[Papirus-Dark](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme).

### Community templates

These are the enabled community integrations in my setup. Install them through
Noctalia from [community-templates](https://github.com/noctalia-dev/community-templates),
not by copying their generated output from this repo:

| Application | Upstream template |
| --- | --- |
| OpenCode | [opencode](https://github.com/noctalia-dev/community-templates/tree/main/opencode) |
| Pear Desktop / YouTube Music | [pear-desktop](https://github.com/noctalia-dev/community-templates/tree/main/pear-desktop) |
| Brave Origin | [brave-origin](https://github.com/noctalia-dev/community-templates/tree/main/brave-origin) |
| Discord / Equicord | [discord](https://github.com/noctalia-dev/community-templates/tree/main/discord) |
| LibreOffice | [libreoffice](https://github.com/noctalia-dev/community-templates/tree/main/libreoffice) |
| VS Code | [vscode](https://github.com/noctalia-dev/community-templates/tree/main/vscode) |
| Prism Launcher | [prismlauncher](https://github.com/noctalia-dev/community-templates/tree/main/prismlauncher) |
| Steam / Millennium | [steam](https://github.com/noctalia-dev/community-templates/tree/main/steam) |
| Micro | [micro](https://github.com/noctalia-dev/community-templates/tree/main/micro) |
| Fastfetch colors | [fastfetch](https://github.com/noctalia-dev/community-templates/tree/main/fastfetch) |
| Thunderbird | [thunderbird](https://github.com/noctalia-dev/community-templates/tree/main/thunderbird) |
| Papirus folder colors | [papirus-icons](https://github.com/noctalia-dev/community-templates/tree/main/papirus-icons) |
| bat | [bat](https://github.com/noctalia-dev/community-templates/tree/main/bat) |
| fzf | [fzf](https://github.com/noctalia-dev/community-templates/tree/main/fzf) |

Micro uses the community **Noctalia** colorscheme, not a theme of my own. The
template supplies syntax and UI colors while leaving the main editor background
to the terminal. My settings only keep the small terminal/background and wrapping
preferences; `softwrap` and `wordwrap` stay enabled. The template's hook selects
`noctalia` without replacing those preferences. Floorp is not automatically
recolored by Noctalia in my setup.

## What is actually mine here

| Files | Personal layer |
| --- | --- |
| `home/.config/kitty/kitty.conf` | Font, transparency, tabs, clipboard behavior and shortcuts. X11 rendering is intentional in this snapshot. |
| `home/.config/noctalia/templates/kitty-details.conf` | Small template filling the tab/bell/mark colors not covered by the built-in Kitty template; no generated palette. |
| `home/.config/fish/` | Heart prompt, Git/status/duration display, aliases, selection/copy bindings and an fzf-history shortcut. The fzf loader only sources Noctalia's output. |
| `home/.config/micro/` | Small wrapping/terminal preferences and selection of the upstream Noctalia theme; no custom theme or vendored syntax/colorscheme packs. |
| `home/.config/fastfetch/` | Module layout and the image I use, without generated hex colors. Noctalia's community hook adds the colors after installation. |
| `home/.config/btop/`, `home/.config/bat/` | Behavior and references to generated Noctalia themes. |
| `home/.local/bin/{makepkg,traur}`, `home/.local/lib/aur-security/` | My pre-execution integration around the upstream Traur scanner, plus tests. |
| `aur/traur/` | Patch and lockfile needed to reproduce the local scanner build; no binary or vendored upstream source. |
| `wallpapers/mvGhYEJ.jpeg` | The wallpaper I use, not a claim that I created the artwork. The Fastfetch image has the same distinction. |

### System Menu

I also use my **[System Menu](https://github.com/ajsem1337/system-menu)** Noctalia
plugin: an Arch package browser, terminal/btop launcher and system information.
It lives in its own repository. At the time of this snapshot it is not in either
the official or community plugin catalog; add that repository as a custom Git
plugin source in Noctalia. Do not copy the plugin into these dotfiles.

## Using the files

This is a reference for my setup, not an unattended installer. Back up your
existing files and review each configuration before copying it. `home/` mirrors
`$HOME`; it does not contain a complete user profile.

1. Install the tools you actually want: Kitty, Maple Mono NF, Fish, Micro,
   Fastfetch, bat, eza, fzf and btop. This is not a system package inventory.
2. Copy the selected `.config` directories into your own `$XDG_CONFIG_HOME`
   (normally `~/.config`). For Fastfetch, keep the `images/` directory beside
   `config.jsonc`. Its photo path uses the default `~/.config` location; adjust
   it if you use a custom config directory.
3. Select the palette and official/community templates above in Noctalia.
   In particular, generate the Kitty, Micro, btop, bat and fzf theme files before using
   the corresponding configurations. Fastfetch's config is strict JSON so the
   community template's `jq` hook can update it; it deliberately has no saved
   machine-specific OS installation date.
4. Merge the Kitty extension from
   [`noctalia-kitty.toml`](noctalia-kitty.toml) into your existing
   `~/.config/noctalia/config.toml`. Do not replace unrelated Noctalia settings.
   Apply the templates to generate `kitty/themes/noctalia-details.conf`.
5. Pick `wallpapers/mvGhYEJ.jpeg` in Noctalia and add System Menu separately.
6. The Traur integration is **optional and separate**: read
   [the build/integration instructions](docs/aur-security.md) before installing
   any files under `.local/`. A stock upstream binary is not the documented
   patched scanner. This is a heuristic check, **not a sandbox or a safety guarantee**.

No Noctalia runtime state, location, clipboard/history, plugin cache, generated
theme outputs, scanner reports, binaries, account data or system/audio profiles
are captured. Third-party projects and artwork retain their original rights;
this repository does not relicense them as my work.

## Checks

```sh
python3 -B -m unittest discover -s home/.local/lib/aur-security -p 'test_*.py' -v
find home/.config/fish -name '*.fish' -exec fish --no-execute {} \;
git diff --check
```
