# skonfig

This is [skonfig](https://skonfig.li), a streamlined and compartmentalized
version of ungleich's [cdist](https://www.cdi.st/)
(forked after [e250024](https://code.ungleich.ch/ungleich-public/cdist/commit/e2500248f2ddc83129e77f2e6b8dffb64904dbae)).

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

### Step 2: Clone sets repositories

Clone the sets you are planning to use. To get started installing the `base` and
`extra` sets is recommended, because they provide the most frequently used types.
Also, most other sets depend on the types provided by the `base` set.
```sh
mkdir -p ~/.skonfig/set
git clone https://github.com/skonfig/base ~/.skonfig/set/base
git clone https://github.com/skonfig/extra ~/.skonfig/set/extra
```

### Step 3: Create initial manifest

```sh
mkdir -p ~/.skonfig/manifest
cp "$(pip3 show skonfig | sed -n -e 's;^Location: \(.*\)/lib.*$;\1;p')/share/doc/skonfig/examples/init-manifest" ~/.skonfig/manifest/init
```
