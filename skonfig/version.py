def __guess_git_version():
    import os

    project_dir = os.path.dirname(os.path.dirname(__file__))

    # If .git exists (could be a directory or a file in case of a submodule) it
    # could be a Git repo, so try to generate version number from Git metadata.
    if os.path.exists(os.path.join(project_dir, ".git")):
        import re
        import subprocess

        # Try to use Git to generate the version
        try:
            def run(cmd):
                return subprocess.check_output(
                    cmd, cwd=project_dir, shell=False).decode().rstrip()

            return re.sub(
                r"(?:-([0-9]+)-g([0-9a-f]{7}))?(-dirty)?$",
                # NOTE: this complex lambda is to always produce
                #       a "+commit[.dirty]" if HEAD is either not a tag or
                #       dirty.
                lambda m:
                    "+"
                    + (m.group(2) if m.group(2) else run(
                        ["git", "rev-parse", "--short=7", "HEAD"]))
                    + ("."+m.group(3)[1:] if m.group(3) else "")
                    if any(m.group(2, 3))
                    else "",
                run(["git", "describe", "--tags", "--dirty", "--abbrev=7"]))
        except e:
            print(e)
            pass

    return "unknown version"


VERSION = __guess_git_version()
