> [!IMPORTANT]
> This is a learning project. The code quality is poor, tests are sparse and there're countless mistakes. I'm well aware of that.
> Please don't use this thing in prod (as if anyone were considering that in the first place).

# Dirtree DB

Hierarchical, plain file database-like python library.

![Hackatime Badge](https://hackatime-badge.hackclub.com/@janekmusin/dirtree-db)

> "Wow, this thing is stupid." - myself, 2026

## Installation & Usage

Installation:

```bash
# Requires python 3.11 or newer
pip install dirtree-db
```

Usage:

```python
from dirtree-db import Database

db = Database("path/to/directory/containing/config/toml")
```

You will need a `config.toml` file in the path selected when defining the database, this is a minimal functional example:

```toml
[store]
name = "name"
```

Usage of functions of the `Database` class and syntax of `config.toml` are explained in a [separate document](usage.md)
