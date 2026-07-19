import json
from pathlib import Path
from dirtree_db import *
from jsf import JSF
import tomllib
import re
import string
import random
import pytest


def test_init(db_root):
    db = Database(db_root)
    config_path = db_root / "config.toml"

    with config_path.open("rb") as file:
        config = tomllib.load(file)

    store_config = config.get("store", {})
    data_dir_str = store_config.get("data_dir", "data")

    entities_list = config.get("entity", [])

    assert isinstance(db, Database)
    assert db.data_dir == db_root / data_dir_str
    for entity in entities_list:
        assert entity["name"] in db.entities

def test_read_write(db_root):
    db = Database(db_root)
    config_path = db_root / "config.toml"

    with config_path.open("rb") as file:
        config = tomllib.load(file)
    entities_list = config.get("entity", [])

    for entity in entities_list:
        schema = entity.get("schema", None)
        if schema is not None:
            break
        path_template = entity["path_template"]
        slug_template = entity["slug_template"]

        segments = path_template.split('/')
        path = ""

        kwargs_dict = {}

        for segment in segments:
            if segment[0] == "{":
                segment = segment[1:-1]
            if segment != "slug":
                path = path + segment + '/'
                if segment not in kwargs_dict:
                    kwargs_dict[segment] = segment

        slug_segments = re.findall(r"\{(.*?)\}", slug_template)
        slug = slug_template.replace("{", "").replace("}", "")

        path = path + slug
        path = (db.data_dir / path).resolve()

        for segment in slug_segments:
            if segment not in kwargs_dict:
                kwargs_dict[segment] = segment

        entity_name = entity["name"]

        data = {"example": "example"}
        allegedly_path = db.write(entity_name, **kwargs_dict, data =data)

        assert path == allegedly_path

        allegedly_data = db.read(entity_name, **kwargs_dict)

        assert data == allegedly_data

def test_errors(db_root):
    db = Database(db_root)
    config_path = db_root / "config.toml"

    with config_path.open("rb") as file:
        config = tomllib.load(file)
    entities_list = config.get("entity", [])

    fake_entity_name = ''.join(random.choices(string.ascii_lowercase, k=20))

    while fake_entity_name in entities_list:
        length = 20
        fake_entity_name = ''.join(random.choices(string.ascii_lowercase, k=length))
        length = length + 1

    with pytest.raises(UnknownEntityError):
        db.read(fake_entity_name)

    for entity in entities_list:
        path_template = entity["path_template"]
        slug_template = entity["slug_template"]
        schema = entity.get("schema", None)
        entity_name = entity["name"]

        if path_template.count("{") == 4 and path_template.count("}") == 4 and slug_template.count("{") == 0 and slug_template.count("}") == 0 and schema is None:
            with pytest.raises(PathKeyError):
                db.write(entity_name, data ={"example": "example"})

        segments = path_template.split('/')
        path = ""

        kwargs_dict = {}

        for segment in segments:
            if segment[0] == "{":
                segment = segment[1:-1]
            if segment != "slug":
                path = path + segment + '/'
                if segment not in kwargs_dict:
                    kwargs_dict[segment] = segment

        slug_segments = re.findall(r"\{(.*?)\}", slug_template)
        slug = slug_template.replace("{", "").replace("}", "")

        path = path + slug
        path = (db.data_dir / path).resolve()

        for segment in slug_segments:
            if segment not in kwargs_dict:
                kwargs_dict[segment] = segment

        with pytest.raises(FileNotFoundError):
            db.read(entity_name, **kwargs_dict)

        with pytest.raises(FileNotFoundError):
            db.delete(entity_name, **kwargs_dict)

def test_no_config(tmp_path):
    with pytest.raises(StoreNotFoundError):
        db = Database(tmp_path)

def test_schema(db_root):
    db = Database(db_root)
    config_path = db_root / "config.toml"
    with config_path.open("rb") as file:
        config = tomllib.load(file)
    entities_list = config.get("entity", [])

    for entity in entities_list:
         schema = entity.get("schema", None)
         path_template = entity["path_template"]
         slug_template = entity["slug_template"]

         segments = path_template.split('/')
         path = ""

         kwargs_dict = {}

         for segment in segments:
             if segment[0] == "{":
                 segment = segment[1:-1]
             if segment != "slug":
                 path = path + segment + '/'
                 if segment not in kwargs_dict:
                     kwargs_dict[segment] = segment

         slug_segments = re.findall(r"\{(.*?)\}", slug_template)
         slug = slug_template.replace("{", "").replace("}", "")

         path = path + slug
         path = (db.data_dir / path).resolve()

         for segment in slug_segments:
             if segment not in kwargs_dict:
                 kwargs_dict[segment] = segment

         entity_name = entity["name"]
         if schema is not None:
             schema_path = (db_root / schema).resolve()

             with schema_path.open("rb") as file:
                 schema_dict = json.load(file)

             faker = JSF(schema_dict)
             fake_order = faker.generate()
             db.write(entity_name, **kwargs_dict, data=fake_order)
             with pytest.raises(ValidationError):
                 db.write(entity_name, **kwargs_dict, data ={"example": "example"})
             with pytest.raises(CorruptRecordError):
                 wrong_string = """
                 {"example": "example"}
                 """
                 path.write_text(wrong_string, encoding="utf-8")
                 db.read(entity_name, **kwargs_dict)
