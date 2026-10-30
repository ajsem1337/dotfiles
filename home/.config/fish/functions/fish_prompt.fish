function fish_prompt
    set -l last_status $status

    set_color -o f38ba8
    echo -n "♥ "
    set_color normal

    set_color -o f5c2e7
    echo -n "$USER "
    set_color normal

    if set -q SSH_CONNECTION
        set_color bac2de
        echo -n "@"(hostname -s)" "
        set_color normal
    end

    set_color -o 89b4fa
    echo -n (prompt_pwd)" "
    set_color normal

    set -l git_info (__fish_git_prompt "%s")
    if test -n "$git_info"
        set_color -o fab387
        echo -n " $git_info "
        set_color normal
    end

    set_color b4befe
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
            set_color fab387
            echo -n "$duration_str "
            set_color normal
        end
    end

    if test $last_status -eq 0
        set_color -o a6e3a1
        echo -n "➜ "
    else
        set_color -o f38ba8
        echo -n "✗ "
    end

    set_color normal
end
