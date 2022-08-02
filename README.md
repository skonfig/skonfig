# skonfig

This is [skonfig](https://skonfig.li), a fork of [ungleich](https://github.com/ungleich)'s [cdist](https://github.com/ungleich/cdist) (after [f061fb1](https://github.com/ungleich/cdist/commit/f061fb168ddacc894cb6e9882ff5c8ba002fadd8)).

Work is mostly split between three main repositories:

* **skonfig** - implementation of the **skonfig tool** and quick **getting started** bits,
* [base](https://github.com/skonfig/base) - **base** explorers and types,
* [extra](https://github.com/skonfig/extra) - **extra** types (community contributions).
 
## Getting Started

There will be no versioned releases fow now - everything is expected to be used from the repositories.

We are currently targeting existing `cdist` power users, so expect some rough edges.

### Step 1: Clone repositories

```sh
cd ~/Where/YOU/keep/your_repos/
git clone https://github.com/skonfig/skonfig
git clone https://github.com/skonfig/base
git clone https://github.com/skonfig/extra
```

### Step 2: Add `skonfig` to `$PATH`

```sh
ln -s "$PWD/skonfig/bin/skonfig" "$HOME/.local/bin/skonfig"
```

### Step 3: Create configuration directory and file

```sh
mkdir "$HOME/.skonfig"
cat > "$HOME/.skonfig/config" <<EOF
[GLOBAL]
conf_dir = $HOME/.skonfig:$PWD/extra:$PWD/base
EOF
```
