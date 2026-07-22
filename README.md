> [!IMPORTANT]
> This is a learning project. The code quality is poor, tests are sparse and there're countless mistakes. I'm well aware of that.
> Please don't use this thing in prod (as if anyone were considering that in the first place).

# Dirtree DB

Hierarchical, plain file database-like python library.

![Hackatime Badge](https://hackatime-badge.hackclub.com/@janekmusin/dirtree-db)

> "Wow, this thing is stupid." - myself, 2026

The main use case for this library is colaborative data collection in a git repo. 
It's terrible at that, but not as much as using it for things a database would be used for normally.

## Installation & Usage

Installation:

```bash
# Requires python 3.11 or newer
pip install dirtree-db
```

Usage:

```python
from dirtree_db import Database

db = Database("path/to/directory/containing/config/toml")
```

You will need a `config.toml` file in the path selected when defining the database, this is a minimal functional example:

```toml
[store]
name = "name"
```

Usage of functions of the `Database` class and syntax of `config.toml` are explained in a [separate document](https://github.com/First-Non-Interesting-Username/dirtree-db/blob/main/usage.md)

### Nix

If for some reason you want to use nix for this library, add this flake input to your flake:

```nix
dirtree-db.url = "github:first-non-interesting-username/dirtree-db";
```

You can then access this package in your flake as:

```nix
inputs.dirtree-db.packages.${pkgs.stdenv.hostPlatform.system}.dirtree-db
```

If the build is too demanding for you, cachix cache is available, paste that into your configuration:

```nix
nix.settings = {
  extra-substituters = ["https://dirtree-db.cachix.org"];
  extra-trusted-public-keys = [
    "dirtree-db.cachix.org-1:geR/eeJBzFUNhj3mwjHm1EK/mzXIG/PF3Bg48YlF1ys="
  ];
};
```

## Tech stack

This library is made using almost only Python standard libraries, [jsonschema](https://pypi.org/project/jsonschema/) is the only exception.
