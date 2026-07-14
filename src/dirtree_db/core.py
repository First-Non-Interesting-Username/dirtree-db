from pathlib import Path
import tomllib
import json
from typing import Any

class StoreNotFoundError(FileNotFoundError):
    pass

class UnknownEntityError(KeyError):
    pass

class PathKeyError(KeyError):
    pass

class ValidationError(Exception):
    pass

class CorruptRecordError(Exception):
   pass


class Database:
    def __init__(self, root: Path) -> None:
        self.root = root.expanduser().resolve()

        self.config_path = self.root / "config.toml"

        if not self.config_path.exists():
            raise StoreNotFoundError(f"config.toml not found at {self.config_path}")

        with self.config_path.open("rb") as file:
            config = tomllib.load(file)

        store = config.get("store", {})
        data_dir_str = store.get("data_dir", "data")

        self.data_dir = self.root / data_dir_str

        self.data_dir.mkdir(parents=True, exist_ok=True)

        entities_list = config.get("entity", [])

        self.entities: dict[str, dict[str, Any]]  = {}

        for entity in entities_list:
            name = entity["name"]

            if name in self.entities:
                raise ValueError(f"Duplicate entity name in config.toml: {name!r}")

            schema = entity.get("schema", None)

            if schema is not None:
                schema_path = self.root / schema

                if not schema_path.exists():
                    raise FileNotFoundError(f"Declared schema file for {name!r} does not exist."
                        f"Expected path: {schema_path}")

                try:
                    with schema_path.open("r", encoding="utf-8") as file:
                        schema_content = json.load(file)
                except json.JSONDecodeError as error:
                        raise ValueError(f"Schema file {schema_path} contains incorrect JSON") from error

                entity["schema"] = schema_content



            self.entities[name] = entity
