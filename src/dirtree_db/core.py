from multiprocessing import Value
import tomllib
import json
import os
import re
from typing import Any
from jsonschema import ValidationError as JSONSchemaValidationError
from jsonschema import validate
from pathlib import Path

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
                    raise FileNotFoundError(f"Declared schema file for {name!r} does not exist"
                        f"Expected path: {schema_path}")

                try:
                    with schema_path.open("r", encoding="utf-8") as file:
                        schema_content = json.load(file)
                except json.JSONDecodeError as error:
                        raise ValueError(f"Schema file {schema_path} contains incorrect JSON") from error

                entity["schema"] = schema_content

            path_template = entity["path_template"]
            segments = path_template.split('/')
            if len(segments) < 2:
                raise ValueError(f"Declared path_template for {name!r} must have at least 2 segments")
            if len(segments[0]) == 0:
                raise ValueError(f"Declared path_template for {name!r} is an absolute path")
            if segments[0].startswith('{'):
                raise ValueError(f"Declared path_template for {name!r} does not start with literal directory")
            if segments[-1] != "{slug}":
                raise ValueError(f"Declared path_template for {name!r} does not end with '{{slug}}'")

            slug_template = entity["slug_template"]

            if not slug_template.endswith(".json"):
                raise ValueError(f"Declared slug_template for {name!r} does not end with '.json'")



            self.entities[name] = entity

    def _get_entity(self, entity_name):
        if entity_name not in self.entities:
            raise UnknownEntityError(f"Entity {entity_name} does not exist")
        return self.entities[entity_name]

    def _route(self, entity_name, **kwargs):
        entity = self._get_entity(entity_name)

        path_template = entity["path_template"]

        slug_template = entity["slug_template"]

        try:
            slug = slug_template.format(**kwargs)
            all_vars = {**kwargs, "slug": slug}
            relative_path = path_template.format(**all_vars)
        except KeyError as error:
            raise PathKeyError(f"missing template field {error.args[0]}") from error

        full_path = self.data_dir / relative_path

        return full_path

    def write(self, entity_name: str, /, *, data: dict, **kwargs):
        entity = self._get_entity(entity_name)

        schema = entity.get("schema", None)

        if schema is not None:
            try:
                validate(data, schema)
            except JSONSchemaValidationError as error:
                raise ValidationError(error.message) from error

        path_to_file = self._route(entity_name, **kwargs)

        path_to_file.parent.mkdir(parents=True, exist_ok=True)

        json_string = json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False) + '\n'

        tmp = path_to_file.with_suffix(".json.tmp")
        tmp.write_text(json_string, encoding="utf-8")
        os.replace(tmp, path_to_file)

        return path_to_file

    def read(self, entity_name: str, /, **kwargs):
        entity = self._get_entity(entity_name)

        path_to_file = self._route(entity_name, **kwargs)

        try:
            with path_to_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise CorruptRecordError(
                f"Record at {path_to_file} is not valid JSON: {error}"
            ) from error

        schema = entity.get("schema", None)

        if schema is not None:
            try:
                validate(data, schema)
            except JSONSchemaValidationError as error:
                raise CorruptRecordError(
                    f"Record at {path_to_file} fails schema validation: {error.message}"
                ) from error

        return data

    def exists(self, entity_name: str, /, **kwargs):
        path_to_file = self._route(entity_name, **kwargs)
        return path_to_file.exists()

    def list(self, entity_name: str, /):
        entity = self._get_entity(entity_name)
        escaped = re.escape(entity["path_template"])
        regex_str = re.sub(r'\\{.+?\\}', r'[^/]+', escaped)
        pattern = re.compile(regex_str)

        matched_files: list[Path] = []
        for file_path in self.data_dir.rglob("*.json"):
            if not file_path.is_file():
                continue
            relative = file_path.relative_to(self.data_dir).as_posix()
            if pattern.fullmatch(relative):
                matched_files.append(file_path)
        return matched_files

    def delete(self, entity_name: str, /, *, prune: bool = True, **kwargs):
        path_to_file = self._route(entity_name, **kwargs)
        parent = path_to_file.parent
        path_to_file.unlink()
        if prune:
            while parent != self.data_dir:
                parent_of_parent = parent.parent
                try:
                    parent.rmdir()
                except OSError:
                    break
                parent = parent_of_parent
