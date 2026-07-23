{
  lib,
  python3Packages,
  fetchFromGitHub,
}:

python3Packages.buildPythonApplication (finalAttrs: {
  pname = "dirtree-db";
  version = "0.1.2-unstable-2026-07-23";
  pyproject = true;
  __structuredAttrs = true;

  src = fetchFromGitHub {
    owner = "First-Non-Interesting-Username";
    repo = "dirtree-db";
    rev = "053245597a1a58f24ffaab4d62e8f392f92432f2";
    hash = "sha256-VQu/B3mJdogOCqSPqYKliD6Z7VbEDwLNRj40bNGGhn0=";
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
