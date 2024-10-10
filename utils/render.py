import pydot
import argparse
import signal

def render(graph_path,png_path, t=15):
    """
    Save the graph as a png file at the given path.
    Gracefully timeout in t seconds.
    """    
    # read the dot file
    graphs = pydot.graph_from_dot_file(graph_path)
    graph = graphs[0]

    for node in graph.get_nodes():
        if node.get_name() == "\"\\n\"":
            # remove this node
            graph.del_node(node)

    def handler(signum, frame):
        raise Exception("timeout")

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(15)
    try:
        graph.write_png(png_path)
    except Exception as e:
        pass

def createDot(transitions: dict[str, dict[str, set[str]]], startState: str) -> str:
    """
    Create a dot file from the NFA transitions.
    """
    dot = "\n".join([
        "digraph NFA {",
        "\trankdir=LR;",
        "\tsplines=true;",
        "\toverlap=false;",
        "\tnode [shape=circle];",
        "\tnode [label=\"\"];"
    ]) + "\n"
    
    for state in transitions:
        for symbol, nextStates in transitions[state].items():
            for nextState in nextStates:
                dot += f"\t{state} -> {nextState} [label=\"{symbol}\"];\n"

    dot += f"\tempty [shape=none];\n"
    dot += f"\tempty -> {startState};\n"
    dot += "}\n"
    
    return dot

if __name__ == "__main__":
    # take the path as argument
    parser = argparse.ArgumentParser(description='Render the dot file')
    parser.add_argument('path', type=str, help='path to dot file')
    args = parser.parse_args()
    
    render(args.path, ".".join(args.path.split('.')[:-1]) + '.png')
