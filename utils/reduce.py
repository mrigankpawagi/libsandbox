from copy import deepcopy

def removeEpsilonTransitions(transitions: dict[str, dict[str, set[str]]], startState: str) -> dict[str, dict[str, set[str]]]:
    """
    Create an equivalent NFA without epsilon transitions.
    """
    epsilon = ''  # Assuming epsilon transitions are represented by an empty string
    new_transitions = {state: {symbol: set(states) for symbol, states in trans.items()} for state, trans in transitions.items()}

    def epsilon_closure(state: str) -> set[str]:
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

    # fuse the startState with its epsilon closure
    for state in closures[startState]:
        # add transitions from the epsilon closure of the startState to the startState
        for symbol, states in new_transitions.get(state, {}).items():
            if symbol != epsilon:
                if symbol not in new_transitions[startState]:
                    new_transitions[startState][symbol] = set()
                new_transitions[startState][symbol].update(states)
        # add transitions to the epsilon closure of the startState to the startState
        for s, trans in new_transitions.items():
            for symbol, states in trans.items():
                if symbol != epsilon:
                    if states.intersection(closures[startState]):
                        new_transitions[s][symbol] = {x for x in new_transitions[s][symbol] if x not in closures[startState]}
                        new_transitions[s][symbol].add(startState)

    # remove epsilon transitions
    for state in transitions:
        new_transitions[state].pop(epsilon, None)
    
    # remove all states in the epsilon closure of the startState except the startState
    for state in closures[startState]:
        if state != startState:
            new_transitions.pop(state, None)

    return new_transitions

def removeUnreachableStates(transitions: dict[str, dict[str, set[str]]], startState: str) -> dict[str, dict[str, set[str]]]:
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
