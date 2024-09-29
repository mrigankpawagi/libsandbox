import argparse
import subprocess
import os

# get the absolute path of the script
script_dir = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(description='Library Call Policy Extractor')
parser.add_argument('path', type=str, help='path to C-file')
args = parser.parse_args()

path = args.path
path_without_extension = '.'.join(path.split('.')[:-1])

# check if the library call pass is built
try:
    with open(script_dir + '/build/LibraryCallPass/LibraryCallPass.so', 'r') as f:
        pass
except FileNotFoundError:
    print('LibraryCallPass not built. Building LibraryCallPass...')
    subprocess.run(['mkdir', '-p', 'build'], cwd=script_dir)
    subprocess.run(['cmake', '..'], cwd=script_dir + '/build', stdout=subprocess.PIPE)
    subprocess.run(['make'], cwd=script_dir + '/build', stdout=subprocess.PIPE)
output = subprocess.run(
    [
        'clang', f'-fpass-plugin={script_dir}/build/LibraryCallPass/LibraryCallPass.so', '-O0', path,
        '-emit-llvm', '-S'
    ],
    capture_output=True
)
# compile the ll file to executable
subprocess.run(['clang', path_without_extension + '.ll', '-o', path_without_extension])

# convert the dot file to png
subprocess.run([
    'dot', '-Tpng', path_without_extension + '.dot', '-o', path_without_extension + '.png'
])
