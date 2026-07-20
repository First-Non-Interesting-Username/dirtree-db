{
  lib,
  python3Packages,
  fetchFromGitHub,
}:

python3Packages.buildPythonApplication (finalAttrs: {
  pname = "dirtree-db";
  version = "0.1,1";
  pyproject = true;
  __structuredAttrs = true;

  src = fetchFromGitHub {
    owner = "First-Non-Interesting-Username";
    repo = "dirtree-db";
    rev = "ebb9120c3183481cf066cef4cb720f0573e377b0";
    hash = "sha256-gwndUefe5w74fK6nqekLSUpu85pVii3wFY9XF4QEsBg=";
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
