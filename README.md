# Umbriel + Noctalia dotfiles

CachyOS · Wayland · [Umbriel](https://github.com/noctalia-dev/umbriel) ·
[Noctalia](https://github.com/noctalia-dev/noctalia) · Kitty · Fish

My terminal configs, a few local helpers and a wallpaper I like. Desktop and
application styling comes from Noctalia's
[built-in](https://github.com/noctalia-dev/noctalia/tree/main/assets/templates)
and [community templates](https://github.com/noctalia-dev/community-templates),
not a theme stack I maintain myself. Only my additions belong in this repo;
generated themes stay out.

## Look and feel

- **Theme:** [Catppuccin](https://github.com/catppuccin/catppuccin), almost always
  Mocha. The accent may change; the current palette is
  [Mocha Mauve-Lavender](https://github.com/noctalia-dev/community-palettes/tree/main/Catppuccin%20Mocha%20Mauve-Lavender).
- **Wallpaper:** a fixed favorite, not a palette generator. Colors come from
  the selected theme, independently of the wallpaper.
- **Application integration:** a shared palette across GTK3, GTK4/libadwaita
  and Qt5/Qt6, with theme and icon access configured for Flatpak applications.
  Qt currently uses Noctalia's generated palettes with Fusion, not a separate
  Kvantum theme.
- **Icons:** patched [Papirus-Dark](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme),
  including recolored folders to match the accent.

Enable the relevant Noctalia templates for your applications. Any small custom
additions are included with the configs below.

## My files

| Path | Contents |
| --- | --- |
| `home/.config/kitty/` | Terminal layout, font, transparency and shortcuts. |
| `home/.config/fish/` | Prompt, aliases and key bindings. |
| `home/.config/{micro,fastfetch,btop,bat}/` | Small terminal-tool preferences and the Fastfetch layout/image. |
| `home/.config/noctalia/templates/kitty-details.conf` | Extra Kitty color bindings, rendered by Noctalia. |
| `home/.local/bin/`, `home/.local/lib/aur-security/`, `aur/traur/` | My Traur/makepkg integration, tests and reproducible scanner patch. |
| `wallpapers/` | The wallpaper I use. |

My **[System Menu](https://github.com/ajsem1337/system-menu)** Noctalia plugin
lives in its own repository. Add it as a custom Git plugin source; it is not
currently in the official or community catalog.

## Using the files

`home/` mirrors `$HOME`. Back up existing files and copy only the configs you
want; this is not an unattended desktop installer.

1. Copy the selected configs, keeping the Fastfetch image beside its config.
   Paths assume the usual `~/.config`; adjust them if yours differs.
2. Select your Catppuccin palette in Noctalia and apply the templates needed by
   those configs. Generated color files are not included here.
3. Merge [`noctalia-kitty.toml`](noctalia-kitty.toml) into your existing Noctalia
   config to enable the extra Kitty template, then apply it.
4. Pick the wallpaper separately and add System Menu from its repository.

The Traur integration is optional: read [its instructions](docs/aur-security.md)
before installing the `.local/` files. It is a heuristic check, **not a sandbox
or a safety guarantee**.

## Previous setup

I moved from GNOME to Umbriel + Noctalia. The retired setup is reduced to a few
references on the [`gnome` branch](https://github.com/ajsem1337/dotfiles/tree/gnome);
the original snapshots remain in Git history, not as a maintained restore kit.

## Checks

```sh
python3 -B -m unittest discover -s home/.local/lib/aur-security -p 'test_*.py' -v
find home/.config/fish -name '*.fish' -exec fish --no-execute {} \;
git diff --check
```

No runtime state, generated themes, reports or account data are captured.
Upstream themes, templates and artwork retain their original authorship and rights.
