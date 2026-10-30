if status is-interactive
    # Cisza na wejściu.
    set -g fish_greeting

    # Lokalne programy użytkownika; fish_add_path usuwa duplikaty.
    fish_add_path -g $HOME/.local/bin

    # Kitty SSH zachowuje integrację terminala na zdalnej maszynie.
    alias kssh="kitty +kitten ssh"

    # Edytor terminalowy. Nie podmieniamy nano na program z inną składnią.
    if type -q micro
        set -gx EDITOR micro
        set -gx VISUAL micro
    end

    # Czytelne listowanie z ikonami. Oryginalne ls nadal: command ls.
    if type -q eza
        alias ls="eza --icons --group-directories-first"
        alias ll="eza -l --icons --group-directories-first"
        alias la="eza -la --icons --group-directories-first"
        alias tree="eza --tree --level=2 --icons --group-directories-first"
    end

    # Czytelny podgląd plików. Surowe cat nadal: command cat.
    if type -q bat
        alias cat="bat --paging=never"
    end

    # Szybsze cd z pamięcią często używanych katalogów.
    if type -q zoxide
        zoxide init fish --cmd cd | source
    end

    # Przeszukiwalna historia poleceń.
    if type -q atuin
        atuin init fish | source
    end

    # Ustawienia własnego prompta.
    set -g fish_prompt_pwd_dir_length 3
    set -g __fish_git_prompt_showdirtystate 1
    set -g __fish_git_prompt_showupstream informative
    set -g __fish_git_prompt_showstashstate 1
    set -g __fish_git_prompt_showuntrackedfiles 1
end

# Kosmetyka tylko dla lokalnej interaktywnej sesji logowania.
if status is-interactive; and status is-login; and not set -q SSH_CONNECTION; and type -q fastfetch
    fastfetch
end

# pnpm
set -gx PNPM_HOME '@HOME@/.local/share/pnpm'
if not string match -q -- "$PNPM_HOME/bin" $PATH
  set -gx PATH "$PNPM_HOME/bin" $PATH
end
# pnpm end
