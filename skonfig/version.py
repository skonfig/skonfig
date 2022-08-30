def __silent_check_output(cmd, cwd):
    import os
    import subprocess
    try:
        # NOTE: subprocess.DEVNULL was added with Python 3.3
        devnull = os.open(os.devnull, os.O_RDONLY)
        return subprocess.check_output(
            cmd, cwd=cwd, stderr=devnull,
            shell=False).decode().rstrip()
    except InterruptedError:
        # retry
        return run(cmd)
    finally:
        os.close(devnull)


def __guess_git_version():
    import os

    project_dir = os.path.dirname(os.path.dirname(__file__))

    # If .git exists (could be a directory or a file in case of a submodule) it
    # could be a Git repo, so try to generate version number from Git metadata.
    if os.path.exists(os.path.join(project_dir, ".git")):
        import re

        # Try to use Git to generate the version
        try:
            git_match = re.match(
                r"^(.*?)(?:-([0-9]+)-g([0-9a-f]{7}))?(-dirty)?$",
                __silent_check_output(
                    ["git", "describe", "--tags", "--dirty",
                     "--abbrev=7", "--match=[0-9]*"], project_dir))

            version = git_match.group(1)

            if any(git_match.group(3, 4)):
                # NOTE: this complex logic is to always produce
                #       a "+commit[.dirty]" suffix if HEAD is either not a
                #       tag/release or dirty.
                version += "+"

                # get commit id
                if git_match.group(3):
                    version += git_match.group(3)
                else:
                    # git didn't produce a commit id, probably because it is a
                    # tag with dirty changes.
                    version += __silent_check_output(
                        ["git", "rev-parse", "--short=7", "HEAD"], project_dir)

                if git_match.group(4):
                    version += "." + git_match.group(4)[1:]

            return version
        except Exception:
            pass

    return "unknown version"


VERSION = __guess_git_version()
