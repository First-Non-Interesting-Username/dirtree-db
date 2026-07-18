from pathlib import Path
from dirtree_db import Database
import tomllib
import re


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
