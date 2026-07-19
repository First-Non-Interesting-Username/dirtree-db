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

        [[entity]]
        name = "file"
        path_template = "file/{definitely-wont-end-up-empty}/{slug}"
        slug_template = "static.json"

        [[entity]]
        name = "schema-test"
        path_template = "schema/{version}/{slug}"
        slug_template = "{version}-{dummy}.json"
        schema = "schemas/schema-text.json"
        """

    config_path.write_text(config_string, encoding="utf-8")

    schema_path = tmp_path / "schemas/schema-text.json"
    schema_string = """
    {
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "$id": "https://example.com/user-profile.schema.json",
      "title": "UserProfile",
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "The user's full name."
        },
        "email": {
          "type": "string",
          "format": "email",
          "description": "A valid email address."
        },
        "age": {
          "type": "integer",
          "minimum": 18,
          "description": "Age must be an integer and at least 18."
        },
        "tags": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "uniqueItems": true
        }
      },
      "required": ["name", "email", "age"]
    }
    """
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_text(schema_string, encoding="utf-8")
    return tmp_path
