# Contributing

This is a learning project. Expect rough edges.

## Setup

```bash
# with devenv
nix devenv

# with python
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

## Running tests

```bash
hatch run test:pytest
```

## Submitting changes

1. Fork & branch
2. Make your thing
3. Make sure `pytest` passes
4. Open a PR

That's it. Thanks for helping out.
