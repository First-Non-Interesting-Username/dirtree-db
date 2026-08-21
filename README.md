> [!IMPORTANT]
> This is a learning project. The code quality is poor, tests are sparse and there're countless mistakes. I'm well aware of that.
> Please don't use this thing in prod (as if anyone were considering that in the first place).

# Dirtree DB

Hierarchical, plain file database-like python library.

![Hackatime Badge](https://hackatime.hackclub.com/api/v1/badge/U0A9Y38B28H/First-Non-Interesting-Username/dirtree-db)

<img width="2560" height="1405" alt="basic usage showcase" src="https://github.com/user-attachments/assets/06697cfd-a866-4997-8666-1a132866c4c0" />

> "Wow, this thing is stupid." - myself, 2026

The main use case for this library is collaborative data collection in a git repo.
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
from pathlib import Path

db = Database(Path("path/to/directory/containing/config/toml"))
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

## Tech stack

This library is made using almost only Python standard libraries, [jsonschema](https://pypi.org/project/jsonschema/) is the only exception.

## Contributing

If you want to contribute for some reason, make sure to read [CONTRIBUTING.md](/CONTRIBUTING.md)
