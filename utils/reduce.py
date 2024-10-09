from copy import deepcopy

def removeEpsilonTransitions(transitions: dict[int, dict[str, set[int]]]) -> dict[int, dict[str, set[int]]]:
    """
    Create an equivalent NFA without epsilon transitions.
    """
    epsilon = ''  # Assuming epsilon transitions are represented by an empty string
    new_transitions = {state: {symbol: set(states) for symbol, states in trans.items()} for state, trans in transitions.items()}

    def epsilon_closure(state: int) -> set[int]:
        closure = {state}
        stack = [state]
        while stack:
            current = stack.pop()
            for next_state in transitions.get(current, {}).get(epsilon, []):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    closures = {state: epsilon_closure(state) for state in transitions}

    for state, trans in transitions.items():
        for symbol, states in trans.items():
            if symbol != epsilon:
                new_states = set()
                for s in states:
                    new_states.update(closures[s])
                new_transitions[state][symbol] = new_states

    for state, closure in closures.items():
        for s in closure:
            for symbol, states in transitions.get(s, {}).items():
                if symbol != epsilon:
                    if symbol not in new_transitions[state]:
                        new_transitions[state][symbol] = set()
                    new_transitions[state][symbol].update(states)

    # remove epsilon transitions
    for state in transitions:
        new_transitions[state].pop(epsilon, None)

    return new_transitions

def removeUnreachableStates(transitions: dict[int, dict[str, set[int]]], startState: int) -> dict[int, dict[str, set[int]]]:
    """
    Remove unreachable states from the NFA and return the equivalent NFA.
    """
    reachable = {startState}
    stack = [startState]
    while stack:
        current = stack.pop()
        for symbol, states in transitions.get(current, {}).items():
            for state in states:
                if state not in reachable:
                    reachable.add(state)
                    stack.append(state)

    # remove unreachable states
    new_transitions = deepcopy(transitions)
    for state in transitions:
        if state not in reachable:
            new_transitions.pop(state, None)
        else:
            for symbol, states in transitions[state].items():
                new_transitions[state][symbol] = {s for s in states if s in reachable}

    return new_transitions
