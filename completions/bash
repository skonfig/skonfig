_comp_cmd_skonfig()
{
    cur="${COMP_WORDS[COMP_CWORD]}"

    prev="${COMP_WORDS[COMP_CWORD-1]}"

    case "$cur" in
        -*)
            COMPREPLY=( $( compgen -W '-h -V -d -i -n -v' -- "$cur" ) )
        ;;
        *)
            case "$prev" in
                -i)
                    compopt -o filenames
                    COMPREPLY=( $( compgen -f -- "$cur" ) )
                ;;
                *)
                    if hash _comp_compgen_known_hosts 2>/dev/null
                    then
                        _comp_compgen_known_hosts -a -- "$cur"
                    fi

                    COMPREPLY+=( $( compgen -W "$( skonfig -d )" -- "$cur" ) )
                ;;
            esac
        ;;
    esac

    return 0
}

complete -F _comp_cmd_skonfig skonfig
