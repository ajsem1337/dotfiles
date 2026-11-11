if status is-interactive
    set -g fish_greeting

    fish_add_path -g $HOME/.local/bin

    alias kssh="kitten ssh"

    if type -q micro
        set -gx EDITOR micro
        set -gx VISUAL micro
    end

    if type -q bat
        alias cat="bat --paging=never"
    end

    if type -q eza
        alias ls="eza --icons=auto --group-directories-first"
        alias ll="eza --long --all --icons=auto --group-directories-first"
    end

    # Prompt
    set -g fish_prompt_pwd_dir_length 3
    set -g __fish_git_prompt_showdirtystate 1
    set -g __fish_git_prompt_showupstream informative
    set -g __fish_git_prompt_showstashstate 1
    set -g __fish_git_prompt_showuntrackedfiles 1
end

if status is-interactive; and status is-login; and not set -q SSH_CONNECTION; and type -q fastfetch
    fastfetch
end

# pnpm
set -gx PNPM_HOME "$HOME/.local/share/pnpm"
if not string match -q -- "$PNPM_HOME/bin" $PATH
  set -gx PATH "$PNPM_HOME/bin" $PATH
end
