import pydot
import argparse
import multiprocessing

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

    p = multiprocessing.Process(target=graph.write_png, args=(png_path,))
    p.start()
    p.join(t)
    if p.is_alive():
        p.terminate()
        p.join()

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

def createPolicy(transitions: dict[str, dict[str, set[str]]], startState: str) -> str:
    """
    Create a policy file from the NFA transitions.
    """
    policy = [startState]
    
    for state in transitions:
        for symbol, nextStates in transitions[state].items():
            for nextState in nextStates:
                if symbol == "":
                    symbol = "0"
                policy.append(f"{state} {symbol} {nextState}")
    
    return "\n".join(policy)

if __name__ == "__main__":
    # take the path as argument
    parser = argparse.ArgumentParser(description='Render the dot file')
    parser.add_argument('path', type=str, help='path to dot file')
    args = parser.parse_args()
    
    render(args.path, ".".join(args.path.split('.')[:-1]) + '.png')
