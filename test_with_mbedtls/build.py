import os
import subprocess

# get the absolute path of the script
script_dir = os.path.dirname(os.path.realpath(__file__))

plugin_path = f"{script_dir}/../build/LibraryCallPass/LibraryCallPass.so"

os.mkdir(f"{script_dir}/../mbedtls/build")
subprocess.run(["CC=clang", f"CFLAGS='-Wno-everything -fpass-plugin={plugin_path} -printEachFunction -O0'", "cmake", ".."], cwd=f"{script_dir}/../mbedtls/build")
subprocess.run(["make"], cwd=f"{script_dir}/../mbedtls/build")
