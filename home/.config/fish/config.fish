if status is-interactive
    # Cisza na wejściu.
    set -g fish_greeting

    # Lokalne programy użytkownika; fish_add_path usuwa duplikaty.
    fish_add_path -g $HOME/.local/bin

    # SSH Kitty dostarcza terminfo na serwer; nie podmieniamy zwykłego ssh.
    alias kssh="kitten ssh"

    # Edytor terminalowy. Nie podmieniamy nano na program z inną składnią.
    if type -q micro
        set -gx EDITOR micro
        set -gx VISUAL micro
    end

    # Czytelny podgląd plików. Surowe cat nadal: command cat.
    if type -q bat
        alias cat="bat --paging=never"
    end

    # Czytelne listowanie. Oryginalne ls nadal dostępne jako: command ls.
    if type -q eza
        alias ls="eza --icons=auto --group-directories-first"
        alias ll="eza --long --all --icons=auto --group-directories-first"
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
set -gx PNPM_HOME "$HOME/.local/share/pnpm"
if not string match -q -- "$PNPM_HOME/bin" $PATH
  set -gx PATH "$PNPM_HOME/bin" $PATH
end
# pnpm end
