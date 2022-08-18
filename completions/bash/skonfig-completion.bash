_skonfig()
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
                    COMPREPLY=( $( compgen -f -- "$cur" ) )
                ;;
                *)
                    COMPREPLY=( $( compgen -W "$( skonfig -d )" -- "$cur" ) )
                ;;
            esac
        ;;
    esac

    return 0
}

complete -F _skonfig skonfig
