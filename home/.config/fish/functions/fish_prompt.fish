function fish_prompt
    set -l last_status $status

    # Nazwane kolory ANSI pochodzą z palety Kitty generowanej przez Noctalię.
    set_color -o red
    echo -n "♥ "
    set_color normal

    set_color -o magenta
    echo -n "$USER "
    set_color normal

    if set -q SSH_CONNECTION
        set_color white
        echo -n "@"(hostname -s)" "
        set_color normal
    end

    set_color -o blue
    echo -n (prompt_pwd)" "
    set_color normal

    set -l git_info (__fish_git_prompt "%s")
    if test -n "$git_info"
        set_color -o yellow
        echo -n " $git_info "
        set_color normal
    end

    set_color cyan
    echo -n (date "+%H:%M")" "
    set_color normal

    if set -q CMD_DURATION
        set -l duration_ms $CMD_DURATION
        if test $duration_ms -ge 500
            set -l duration_str ""
            if test $duration_ms -lt 1000
                set duration_str "$duration_ms""ms"
            else if test $duration_ms -lt 60000
                set duration_str (printf "%.1fs" (math "$duration_ms/1000"))
            else
                set -l minutes (math -s0 "$duration_ms/60000")
                set -l seconds (math -s0 "($duration_ms%60000)/1000")
                set duration_str "$minutes""m""$seconds""s"
            end
            set_color yellow
            echo -n "$duration_str "
            set_color normal
        end
    end

    if test $last_status -eq 0
        set_color -o green
        echo -n "➜ "
    else
        set_color -o red
        echo -n "✗ "
    end

    set_color normal
end
