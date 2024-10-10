import argparse
import subprocess
import os
from utils.reduce import removeEpsilonTransitions, removeUnreachableStates
from utils.render import createDot, render

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
subprocess.run(['clang', path_without_extension + '.ll', '-o', path_without_extension + ".out"])

# read the generated ".policy" file and create an NFA
with open(path_without_extension + '.policy', 'r') as f:
    policy = f.readlines()

startState = policy[0].strip()
transitions = {}
states = {startState}

for i in range(1, len(policy)):
    state, symbol, nextState = policy[i].split()
    if symbol == "0":
        symbol = ""
    if state not in transitions:
        transitions[state] = {}
    if symbol not in transitions[state]:
        transitions[state][symbol] = set()
    transitions[state][symbol].add(nextState)
    states.add(state)
    states.add(nextState)

# if a state is missing, add it with no transitions
for state in states:
    if state not in transitions:
        transitions[state] = {}

# remove epsilon transitions
transitions = removeEpsilonTransitions(transitions)

# remove unreachable states
transitions = removeUnreachableStates(transitions, startState)

# create a dot file from the NFA transitions and also render it
with open(path_without_extension + '.dot', 'w') as f:
    f.write(createDot(transitions, startState))

render(path_without_extension + '.dot', path_without_extension + '.png')
