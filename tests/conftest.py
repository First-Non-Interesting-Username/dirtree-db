import pytest


@pytest.fixture
def db_root(tmp_path):
    config_path = tmp_path / "config.toml"

    config_string = """
        [store]
        data_dir = "data"
        name = "test"

        [[entity]]
        name = "language-model"
        path_template = "model/{lab}/{family}/{slug}"
        slug_template = "{lab}-{family}-{model}.json"
        """

    config_path.write_text(config_string, encoding="utf-8")
    return tmp_path
