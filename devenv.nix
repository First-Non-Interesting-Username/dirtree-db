{ pkgs, ... }:

let
  pythonEnv = pkgs.python3.withPackages (ps: with ps; [
    jsonschema
    pytest
  ]);
in
{
  packages = [
    pythonEnv
  ];

  enterShell = ''
    export PYTHONPATH="${toString ./src}:''${PYTHONPATH:-}"
  '';
}
