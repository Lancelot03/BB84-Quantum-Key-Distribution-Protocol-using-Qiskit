{ pkgs }: {
  deps = [
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.python3Packages.qiskit
    pkgs.python3Packages.matplotlib
  ];
}
