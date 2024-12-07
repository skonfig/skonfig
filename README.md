# skonfig

[skonfig](https://skonfig.li) is a configuration management system forked from [cdist](https://cdi.st)
(after [e250024](https://code.ungleich.ch/ungleich-public/cdist/commit/e2500248f2ddc83129e77f2e6b8dffb64904dbae)).

We have three main repositories:

* **skonfig** - implementation of the **skonfig tool** and quick **getting started** bits,
* [base](https://github.com/skonfig/base) - explorer and types for **general use**,
* [extra](https://github.com/skonfig/extra) - **special purpose** types and incubator for new types.

You can find us in `#skonfig:matrix.org` ([matrix?](https://matrix.org/faq/)).

## Documentation

Most parts of [cdist documentation](https://www.cdi.st/manual/latest/) apply, but there are differences:

* `skonfig` does only `config` (see `skonfig -h`),
* types are managed in sets,
* type manifest can be directory of manifests,
* some types behave differently and it's recommended to consult manuals in *base* and *extra*.

## Split between *base* and *extra*

**Base** explorers and types are used to change the state of the operating
system or core components of it and are not for some specific piece of
software. Furthermore, the quality requirements for inclusion in base are
higher than for extra.

**Extra** contains types for specific purposes like configuring software or
services which don't belong to the operating system and also serves as an
incubator for new types.

## Getting Started

### Step 1: Install `skonfig`

```sh
pip3 install skonfig@git+https://github.com/skonfig/skonfig
```

Note: if you run Python 3.12 or later, you need to have
[setuptools](https://setuptools.pypa.io/) installed.

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
