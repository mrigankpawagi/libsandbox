import pydot
import argparse

# take the path as argument
parser = argparse.ArgumentParser(description='Render the dot file')
parser.add_argument('path', type=str, help='path to dot file')
args = parser.parse_args()

# read the dot file
graphs = pydot.graph_from_dot_file(args.path)
graph = graphs[0]

# render but gracefully timeout in 15 seconds
import signal
import time

def handler(signum, frame):
    raise Exception("timeout")

signal.signal(signal.SIGALRM, handler)
signal.alarm(15)
try:
    # render the graph and save it as png at the same location
    graph.write_png(".".join(args.path.split('.')[:-1]) + '.png')
except Exception as e:
    pass
