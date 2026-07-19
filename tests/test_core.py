import json
import random
import re
import string
import tomllib
from pathlib import Path

import pytest
from dirtree_db import (
    Database,
    UnknownEntityError,
    PathKeyError,
    StoreNotFoundError,
    ValidationError,
    CorruptRecordError,
)
from jsf import JSF


@pytest.fixture
def db_config(db_root):
    db = Database(db_root)
    config_path = db_root / "config.toml"
    with config_path.open("rb") as file:
        config = tomllib.load(file)
    return db, config


def resolve_entity_params(db, entity):
    path_template = entity["path_template"]
    slug_template = entity["slug_template"]

    segments = path_template.split("/")
    path_str = ""
    kwargs_dict = {}

    for segment in segments:
        if segment.startswith("{"):
            segment = segment[1:-1]
        if segment != "slug":
            path_str += segment + "/"
            kwargs_dict.setdefault(segment, segment)

    slug_segments = re.findall(r"\{(.*?)\}", slug_template)
    slug = slug_template.replace("{", "").replace("}", "")
    path_str += slug

    resolved_path = (db.data_dir / path_str).resolve()

    for segment in slug_segments:
        kwargs_dict.setdefault(segment, segment)

    return resolved_path, kwargs_dict


def test_init(db_root, db_config):
    db, config = db_config
    store_config = config.get("store", {})
    data_dir_str = store_config.get("data_dir", "data")
    entities_list = config.get("entity", [])

    assert isinstance(db, Database)
    assert db.data_dir == db_root / data_dir_str

    for entity in entities_list:
        assert entity["name"] in db.entities


def test_read_write(db_config):
    db, config = db_config
    for entity in config.get("entity", []):
        if entity.get("schema") is not None:
            break

        path, kwargs_dict = resolve_entity_params(db, entity)
        entity_name = entity["name"]
        data = {"example": "example"}

        assert db.write(entity_name, **kwargs_dict, data=data) == path
        assert db.read(entity_name, **kwargs_dict) == data


def test_errors(db_config):
    db, config = db_config
    entities_list = config.get("entity", [])

    entity_names = {entity["name"] for entity in entities_list}
    fake_entity_name = "".join(random.choices(string.ascii_lowercase, k=20))
    while fake_entity_name in entity_names:
        fake_entity_name += "x"

    with pytest.raises(UnknownEntityError):
        db.read(fake_entity_name)

    for entity in entities_list:
        path_template = entity["path_template"]
        slug_template = entity["slug_template"]
        entity_name = entity["name"]

        if (
            path_template.count("{") == 4
            and path_template.count("}") == 4
            and slug_template.count("{") == 0
            and slug_template.count("}") == 0
            and entity.get("schema") is None
        ):
            with pytest.raises(PathKeyError):
                db.write(entity_name, data={"example": "example"})

        path, kwargs_dict = resolve_entity_params(db, entity)

        with pytest.raises(FileNotFoundError):
            db.read(entity_name, **kwargs_dict)

        with pytest.raises(FileNotFoundError):
            db.delete(entity_name, **kwargs_dict)


def test_no_config(tmp_path):
    with pytest.raises(StoreNotFoundError):
        Database(tmp_path)


def test_schema(db_root, db_config):
    db, config = db_config
    for entity in config.get("entity", []):
        schema = entity.get("schema")
        if schema is not None:
            path, kwargs_dict = resolve_entity_params(db, entity)
            entity_name = entity["name"]

            schema_path = (db_root / schema).resolve()
            with schema_path.open("rb") as file:
                schema_dict = json.load(file)

            faker = JSF(schema_dict)
            fake_order = faker.generate()

            db.write(entity_name, **kwargs_dict, data=fake_order)

            with pytest.raises(ValidationError):
                db.write(entity_name, **kwargs_dict, data={"example": "example"})

            with pytest.raises(CorruptRecordError):
                wrong_string = '{"example": "example"}'
                path.write_text(wrong_string, encoding="utf-8")
                db.read(entity_name, **kwargs_dict)

def test_list(db_root, db_config):
    db, config = db_config
    for entity in config.get("entity", []):
        schema = entity.get("schema")
        path_template = entity["path_template"]
        slug_template = entity["slug_template"]
        entity_name = entity["name"]
        if schema is not None:
            break
        path, kwargs_dict = resolve_entity_params(db, entity)
        record_string = '{"example": "example"}'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(record_string, encoding="utf-8")
        result = db.list(entity_name)
        assert len(result) > 0 and all(item == path for item in result)

        path.unlink()
        result = db.list(entity_name)
        assert len(result) == 0

def test_delete(db_root, db_config):
    db, config = db_config
    for entity in config.get("entity", []):
        schema = entity.get("schema")
        path_template = entity["path_template"]
        slug_template = entity["slug_template"]
        entity_name = entity["name"]
        path, kwargs_dict = resolve_entity_params(db, entity)
        record_string = '{"example": "example"}'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(record_string, encoding="utf-8")

        db.delete(entity_name, prune=True, **kwargs_dict)
        assert not path.parent.exists() and not path.exists()

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(record_string, encoding="utf-8")
        db.delete(entity_name, prune=False, **kwargs_dict)
        assert path.parent.exists() and not path.exists()
