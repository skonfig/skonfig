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

### Step 1: Install `skonfig`

```sh
pip3 install skonfig@git+https://github.com/skonfig/skonfig
```

### Step 2: Clone base and extra sets repositories

```sh
mkdir -p ~/.skonfig/set
git clone https://github.com/skonfig/base ~/.skonfig/set/base
git clone https://github.com/skonfig/extra ~/.skonfig/set/extra
```

### Step 3: Create configuration directory and initial manifest

```sh
mkdir -p ~/.skonfig/manifest
cp "$(pip show skonfig | sed -n -e 's;^Location: \(.*\)/lib.*$;\1;p')/share/doc/skonfig/examples/init-manifest" ~/.skonfig/manifest/init
```
