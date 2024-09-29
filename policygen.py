import argparse
import subprocess

parser = argparse.ArgumentParser(description='Library Call Policy Extractor')
parser.add_argument('path', type=str, help='path to C-file')
args = parser.parse_args()

path = args.path
path_without_extension = '.'.join(path.split('.')[:-1])

# check if the library call pass is built
try:
    with open('build/LibraryCallPass/LibraryCallPass.so', 'r') as f:
        pass
except FileNotFoundError:
    print('LibraryCallPass not built. Building LibraryCallPass...')
    subprocess.run(['mkdir', '-p', 'build'])
    subprocess.run(['cmake', '..'], cwd='build', stdout=subprocess.PIPE)
    subprocess.run(['make'], cwd='build', stdout=subprocess.PIPE)

output = subprocess.run(
    [
        'clang', '-fpass-plugin=build/LibraryCallPass/LibraryCallPass.so', '-O0', path,
        '-emit-llvm', '-S'
    ],
    capture_output=True
)
dot_contents, policy_contents = output.stdout.decode('utf-8').split('-------------------')
dot_contents = dot_contents.strip()
policy_contents = policy_contents.strip()

# compile the ll file to executable
subprocess.run(['clang', path_without_extension + '.ll'])

with open(path_without_extension + '.dot', 'w') as f:
    f.write(dot_contents)
with open(path_without_extension + '.policy', 'w') as f:
    f.write(policy_contents)

subprocess.run([
    'dot', '-Tpng', path_without_extension + '.dot', '-o', path_without_extension + '.png'
])
