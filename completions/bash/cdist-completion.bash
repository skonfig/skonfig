_cdist()
{
    local cur prev prevprev opts cmds projects
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    prevprev="${COMP_WORDS[COMP_CWORD-2]}"
    opts="-h --help -q --quiet -v --verbose -V --version"
    cmds="config"

    case "${prev}" in
        -*)
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        config)
            opts="-h --help -q --quiet -v --verbose \
                -C --cache-path-pattern -c --conf-dir \
                -f --file -i --initial-manifest \
                -j --jobs -n --dry-run -o --out-dir -p --parallel \
                -r --remote-out-dir \
                -s --sequential --remote-copy --remote-exec"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac

    if [[ ${cur} == -* ]]; then
    	COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    	return 0
    fi

    COMPREPLY=( $(compgen -W "${cmds}" -- ${cur}) )
    return 0
}

complete -F _cdist cdist
