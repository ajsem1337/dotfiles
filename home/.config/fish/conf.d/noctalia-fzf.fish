# Load Noctalia's generated fzf palette for interactive shells.
if status is-interactive
    set -l config_home "$HOME/.config"
    if set -q XDG_CONFIG_HOME[1]; and test -n "$XDG_CONFIG_HOME"
        set config_home "$XDG_CONFIG_HOME"
    end
    if test -r "$config_home/fzf/themes/noctalia.fish"
        source "$config_home/fzf/themes/noctalia.fish"
    end
end
