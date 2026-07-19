# Usage

Each database lives in a directory on your filesystem. Records are stored as individual JSON files, and you define entities — blueprints that map logical record types to paths on disk.

## Quick start

Create a directory with a `config.toml`:

```toml
[store]
name = "my-store"

[[entity]]
name = "note"
path_template = "notes/{slug}"
slug_template = "{title}.json"
```

Initialise the database:

```python
from dirtree_db import Database

db = Database("path/to/db")
```

Write a record:

```python
db.write("note", title="hello", data={
    "body": "Hello, world!",
})
```

Read it back:

```python
note = db.read("note", title="hello")
print(note["body"])  # Hello, world!
```

Behind the scenes, this created a file at `<data_dir>/notes/hello.json`.

## How entities work

An entity tells dirtree-db how to translate logical parameters into a file path. Every entity has a `path_template` and a `slug_template`.

- `path_template` — the directory structure (must end with `{slug}`)
- `slug_template` — the filename (must end with `.json`)

Any `{placeholder}` in either template becomes a required keyword argument when you call `read`, `write`, `delete`, or `exists`.

### Example: blog posts with categories

```toml
[[entity]]
name = "post"
path_template = "posts/{category}/{slug}"
slug_template = "{filename}.json"
```

```python
db.write("post", category="tech", filename="hello-world", data={
    "title": "Hello World",
    "content": "...",
})
```

Produces: `data/posts/tech/hello-world.json`

The `data/` prefix comes from the `data_dir` setting (`"data"` by default).

## Listing records

`db.list(entity_name)` returns every existing record file for an entity.

```python
for path in db.list("note"):
    print(path)
```

## Checking existence

```python
if db.exists("note", title="hello"):
    print("exists")
```

## Deleting records

```python
db.delete("note", title="hello")
```

By default, empty parent directories are cleaned up automatically. Pass `prune=False` to keep them:

```python
db.delete("note", title="hello", prune=False)
```

## Validating data

### On write (schema validation)

Point to a JSON Schema file in your config:

```toml
[[entity]]
name = "user"
path_template = "users/{slug}"
slug_template = "{username}.json"
schema = "schemas/user.json"
```

Now `db.write("user", ...)` will reject data that doesn't match the schema:

```python
from dirtree_db import ValidationError

try:
    db.write("user", username="alice", data={"name": "Alice"})
except ValidationError as e:
    print(e)  # 'age' is a required property
```

### Bulk validation

```python
errors = db.validate_all()
# Returns a list of error strings; empty means everything is fine
```

This checks every record for valid JSON and schema conformance.

## Error handling

| Exception            | When it happens                                           |
| -------------------- | --------------------------------------------------------- |
| `StoreNotFoundError` | The `config.toml` file doesn't exist                      |
| `UnknownEntityError` | You referenced an entity that isn't in the config         |
| `PathKeyError`       | You forgot a required template parameter                  |
| `ValidationError`    | Data you tried to write failed schema validation          |
| `CorruptRecordError` | A record file has bad JSON or violates its schema on read |

All are importable from `dirtree_db`.
