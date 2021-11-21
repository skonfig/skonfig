# cdist

This is the [community maintained](https://github.com/cdist-community)
fork of ungleich's [cdist](https://github.com/ungleich/cdist)
(after [f061fb1](https://github.com/ungleich/cdist/commit/f061fb168ddacc894cb6e9882ff5c8ba002fadd8)).

Work is split between three repositories:

* **cdist** - implementation of the **cdist core** (this repository).
* [cdist-conf](https://github.com/cdist-community/cdist-conf) - **essential** explorers and types.
* [cdist-extra](https://github.com/cdist-community/cdist-extra) - **non-essential** explorers, types, scripts, tools etc.

Difference between essential and non-essential? Explorers and types which are
used to manage state of the operating system (modify files and directories,
install packages, manage services, etc.) and are not strictly related to some
specific piece of software are considered essential.

## Getting Started

Since this fork is still in early stages, there will be no versioned releases
for now.

Everything is expected to be used straight from the repositories.

We are currently targetting cdist power users who already know what they are
doing, so expect some rough edges.

### Get core with essentials

```sh
git clone --recurse-submodules https://github.com/cdist-community/cdist
ln -s "$PWD/cdist/bin/cdist" "$HOME/.local/bin/cdist"
```

**NB** Your `PATH` may not contain `$HOME/.local/bin/`, so modify this line accordingly.

To update `cdist/conf` submodule later:

```sh
git submodule update --remote cdist/conf
```

### Get everything

**NB** Don't copy-paste following lines carelessly into your terminal - existing `~/.cdist.cfg` will be overwritten.

```sh
git clone https://github.com/cdist-community/cdist
git clone https://github.com/cdist-community/cdist-conf
git clone https://github.com/cdist-community/cdist-extra
ln -s "$PWD/cdist/bin/cdist" "$HOME/.local/bin/cdist"
cat > "$HOME/.cdist.cfg" << EOF
[GLOBAL]
conf_dir = $HOME/.cdist:$PWD/cdist-extra:$PWD/cdist-conf
EOF
```
