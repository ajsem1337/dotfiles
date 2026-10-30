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

function fish_user_key_bindings
    bind ctrl-a __select_all
    bind ctrl-c __copy_or_cancel
end
