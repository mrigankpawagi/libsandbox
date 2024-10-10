import os

# get the absolute path of the script
script_dir = os.path.dirname(os.path.realpath(__file__))

plugin_path = f"{script_dir}/../build/LibraryCallPass/LibraryCallPass.so"

os.system(f"CC=clang CFLAGS='-Wno-everything -fpass-plugin={plugin_path} -O0' cmake ..")
os.system("make")
