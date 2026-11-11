function __copy_or_cancel
    if string length -q -- (commandline --current-selection)
        fish_clipboard_copy
        commandline -f end-selection repaint
    else
        commandline -f cancel-commandline
    end
end

function __select_all
    commandline -f end-selection beginning-of-buffer begin-selection end-of-buffer
end

function __history_up
    set -l buffer (commandline --current-buffer | string collect)
    if commandline --paging-mode; or test -n "$buffer"; or not functions -q fzf-history-widget
        commandline -f up-or-search
    else
        fzf-history-widget
    end
end

function fish_user_key_bindings
    if command -q fzf
        # Tylko historia: nie włączamy dodatkowych skrótów Ctrl+T ani Alt+C.
        set -lx FZF_CTRL_T_COMMAND ""
        set -lx FZF_ALT_C_COMMAND ""
        fzf_key_bindings
        bind up __history_up
        bind -M insert up __history_up
    end
    bind ctrl-a __select_all
    bind ctrl-c __copy_or_cancel
end
