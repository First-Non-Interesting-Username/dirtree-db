{
  lib,
  python3Packages,
  fetchFromGitHub,
}:

python3Packages.buildPythonApplication (finalAttrs: {
  pname = "dirtree-db";
  version = "0.2.0-unstable-2026-08-21";
  pyproject = true;
  __structuredAttrs = true;

  src = fetchFromGitHub {
    owner = "First-Non-Interesting-Username";
    repo = "dirtree-db";
    rev = "d50fcbc305be0dabe747ea8199a9e830097360cb";
    hash = "sha256-ft2b4tbQw9IJUYnVOzgxTqvWbcrx4hjH23oMK7xu9z4=";
  };

  build-system = [
    python3Packages.hatchling
  ];

  dependencies = with python3Packages; [
    jsonschema
  ];

  pythonImportsCheck = [
    "dirtree_db"
  ];

  meta = {
    description = "Plain file hierarchical database made in python";
    homepage = "https://github.com/First-Non-Interesting-Username/dirtree-db";
    license = lib.licenses.lgpl3Plus;
    # I'm not in lib.maintainers
    # maintainers = with lib.maintainers; [ ];
    mainProgram = "dirtree-db";
  };
})
