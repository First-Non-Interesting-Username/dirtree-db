from dirtree_db import Database
import tomllib


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
        path_template = entity["path_template"]
        slug_template = entity["slug_template"]

        segments = path_template.split('/')
        for segment in segments:
