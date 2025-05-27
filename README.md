# skonfig

[skonfig](https://skonfig.li) is a system configuration and automation framework
designed to work with all systems, from your toaster to the data centre.

skonfig uses three main repositories:

* **skonfig** - implementation of the **skonfig** executable,
* [base](https://github.com/skonfig/base) - explorer and types for **general use**,
* [extra](https://github.com/skonfig/extra) - **special purpose** types and incubator for new types.

**Need support?** You can find us in `#skonfig:matrix.org` ([matrix?](https://matrix.org/faq/)).

## Documentation

Most parts of the [cdist documentation](https://www.cdi.st/manual/latest/) still
apply, but there are some differences:

* `skonfig` does only `config` (see `skonfig -h`),
* types are managed in sets (base, extra, etc.),
* type manifests can be a directory of scripts,
* `gencode-*` can be a directory of scripts,
* some types behave differently and it's recommended to consult the `man.rst`
  files in *base* and *extra*.

## What are *base* and *extra*?

**Base** explorers and types are used to change the state of the operating
system or core components of it and are not for some specific piece of
software. Furthermore, the quality requirements for inclusion in base are
higher than for extra.

**Extra** contains types for specific purposes like configuring software or
services which don't belong to the operating system and also serves as an
incubator for new types.

Even more types can be found in sets specialised in helping you configure a
specific piece of software. Some of these sets can be found in this organization.

And being a fork of [cdist](https://cdis.st/) originally, your cdist manifests
and types will continue to work with skonfig with no or minimal adjustments.

## Getting Started

```sh
# clone skonfig itself
git clone \
    https://github.com/skonfig/skonfig \
    ~/.skonfig/skonfig

# get base types and explorers
git clone \
    https://github.com/skonfig/base \
    ~/.skonfig/set/base

# and extra goodies
git clone \
    https://github.com/skonfig/extra \
    ~/.skonfig/set/extra

# add skonfig to path
ln -s ~/.skonfig/skonfig/bin/skonfig \
    ~/.local/bin/skonfig

# place for your own files, types and manifests
mkdir -p \
    ~/.skonfig/files \
    ~/.skonfig/type \
    ~/.skonfig/manifest

# copy example initial manifest
cp ~/.skonfig/skonfig/docs/examples/init-manifest \
    ~/.skonfig/manifest/init
```
