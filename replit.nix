{ pkgs }: {
  deps = [
    pkgs.libsodium
  ];
  env = {
  
  PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
    pkgs.libsodium
  ];};
}