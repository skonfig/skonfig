# cdist-core

This is the [community maintained](https://github.com/cdist-community)
fork of [ungleich](https://github.com/ungleich)'s [cdist](https://github.com/ungleich/cdist)
(after [f061fb1](https://github.com/ungleich/cdist/commit/f061fb168ddacc894cb6e9882ff5c8ba002fadd8)).

Work is mostly split between three main repositories:

* **cdist-core** - implementation of the **cdist core** and quick **getting started** bits (this repository).
* [cdist-conf](https://github.com/cdist-community/cdist-conf) - **essential** explorers and types.
* [cdist-extra](https://github.com/cdist-community/cdist-extra) - **non-essential** explorers, types, scripts, tools etc.

## Getting Started

There will be no versioned releases fow now - everything is expected to be used from the repositories.

We are currently targeting `cdist` power users, so expect some rough edges.

### Step 1: Clone repositories

```sh
cd ~/Where/YOU/keep/your_repos/
git clone https://github.com/cdist-community/cdist-core
git clone https://github.com/cdist-community/cdist-conf
git clone https://github.com/cdist-community/cdist-extra
```

### Step 2: Add `cdist` to `$PATH`

```sh
ln -s "$PWD/cdist-core/bin/cdist" "$HOME/.local/bin/cdist"
```

### Step 3: Create configuration directory and file

```sh
mkdir "$HOME/.cdist"
cat > "$HOME/.cdist.cfg" << EOF
[GLOBAL]
conf_dir = $HOME/.cdist:$PWD/cdist-extra:$PWD/cdist-conf
EOF
```
