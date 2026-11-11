# Historical GNOME setup

**Retired after moving to Umbriel + Noctalia.** The current setup is on
[`main`](https://github.com/ajsem1337/dotfiles/tree/main).

This branch is a small reference, not a supported desktop installer. It keeps:

- the GNOME extension list from the last snapshot;
- my GTK4/libadwaita color overrides;
- my Equicord System24 adjustments (based on the upstream theme imported in the CSS).

The old desktop used Catppuccin Mocha Pink, a Catppuccin GTK/GNOME theme with
local tweaks, Tela Pink icons, Kitty, Fish and Vicinae. Making all applications
match required many toolkit-specific overrides. Noctalia now provides the
official/community template system I need, so I do not maintain that stack.

Bundled themes, icon packs, extension code, full settings dumps, system/audio
profiles and the old restore machinery have been removed from this branch's
current tree. Earlier commits still contain the original snapshot; they are
history, not recommended installation instructions.

Useful upstreams: [Catppuccin](https://github.com/catppuccin/catppuccin),
[Catppuccin GTK](https://github.com/catppuccin/gtk),
[System24](https://github.com/refact0r/system24).

If I return to GNOME, I will start with maintained upstream tools rather than
revive this collection of workarounds.
