{ pkgs, ... }:
{
  enterShell = ''
    export PYTHONPATH="${toString ./src}:''${PYTHONPATH:-}"
  '';
  languages.python = {
    enable = true;
    venv = {
      enable = true;
      requirements = ''
        jsonschema
        jsf
        pytest
        build
        twine
      '';
    };
  };
}
