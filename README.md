# skonfig

This is [skonfig](https://skonfig.li), a streamlined and compartmentalized version of
[ungleich](https://github.com/ungleich)'s [cdist](https://github.com/ungleich/cdist)
(forked after [f061fb1](https://github.com/ungleich/cdist/commit/f061fb168ddacc894cb6e9882ff5c8ba002fadd8)).

Work is mostly split between three main repositories:

* **skonfig** - implementation of the **skonfig tool** and quick **getting started** bits,
* [base](https://github.com/skonfig/base) - **base** explorers and types,
* [extra](https://github.com/skonfig/extra) - **extra** types (community contributions).

Our chat room is `#skonfig:matrix.org` (you need [Matrix client](https://matrix.org/docs/projects/try-matrix-now/)).

## Getting Started

There will be no versioned releases fow now - everything is expected to be used from the repositories.

We are currently targeting (`cdist`) power users, so expect some rough edges.

### Step 1: Install `skonfig`

```sh
git clone https://github.com/skonfig/skonfig
ln -s "$PWD/skonfig/bin/skonfig" "$HOME/.local/bin/skonfig"
```

### Step 2: Create configuration directory and initial manifest

```sh
mkdir -p "$HOME/.skonfig/manifest"
cp "$PWD/skonfig/docs/examples/init-manifest" "$HOME/.skonfig/manifest/init"
```

### Step 3: Clone base and extra sets repositories

```sh
mkdir "$HOME/.skonfig/set"
cd "$HOME/.skonfig/set"
git clone https://github.com/skonfig/base
git clone https://github.com/skonfig/extra
```
