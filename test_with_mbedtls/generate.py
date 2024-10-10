import os
import pickle
from utils.reduce import removeEpsilonTransitions, removeUnreachableStates
from utils.render import createDot, render
import argparse

def process_policy(policy_path, function_policies):
    policy_file_without_extension = '.'.join(policy_path.split('.')[:-1])
    policy_file_name_without_extension = os.path.basename(policy_file_without_extension)
    with open(policy_path, 'r') as f:
        policy = f.readlines()
    startState = policy[0].strip()
    transitions = {}
    states = {startState}

    for i in range(1, len(policy)):
        state, symbol, nextState = policy[i].split()
        if symbol == "0": symbol = ""
        if state not in transitions: transitions[state] = {}
        if symbol not in transitions[state]: transitions[state][symbol] = set()
        transitions[state][symbol].add(nextState)
        states.add(state)
        states.add(nextState)

    while any(transition in function_policies for state in transitions for transition in transitions[state]):
        # now loop over all states and see if any of their transitions is available in the function_policies database
        for state in list(transitions.keys()):
            for transition in list(transitions[state].keys()):
                if transition in function_policies:
                    for i, function_policy in enumerate(function_policies[transition]):
                        # prefix all states with "{transition}{i}_"
                        function_start_state = f"{transition}{i}_" + function_policy["start_state"]
                        function_final_state = f"{transition}{i}_" + function_policy["final_state"]
                        function_transitions = {}
                     
                        for function_state in function_policy["transitions"]:
                            function_transitions[f"{transition}{i}_" + function_state] = {}
                            for symbol in function_policy["transitions"][function_state]:
                                function_transitions[f"{transition}{i}_" + function_state][symbol] = {f"{transition}{i}_" + next_state for next_state in function_policy["transitions"][function_state][symbol]}

                        # incorporate this function policy
                        if function_start_state not in transitions:
                            transitions.update(function_transitions)

                        if "" not in transitions[state]: transitions[state][""] = set()
                        transitions[state][""].add(function_start_state)
                        
                        if function_final_state not in transitions: transitions[function_final_state] = {}
                        if "" not in transitions[function_final_state]: transitions[function_final_state][""] = set()

                        for next_state in transitions[state][transition]:
                            transitions[function_final_state][""].add(next_state)
                        
                    # remove the transition
                    transitions[state].pop(transition, None)
        
    # if a state is missing, add it with no transitions
    for state in states:
        if state not in transitions:
            transitions[state] = {}

    # remove epsilon transitions
    transitions = removeEpsilonTransitions(transitions)

    # remove unreachable states
    transitions = removeUnreachableStates(transitions, startState)

    # print the new policy file in the mbedtls/ directory 
    os.makedirs("mbedtls_programs_policies", exist_ok=True)
    with open(f"mbedtls_programs_policies/{policy_file_name_without_extension}.policy", 'w') as f:
        f.write(startState + '\n')
        for state in transitions:
            for symbol in transitions[state]:
                for next_state in transitions[state][symbol]:
                    f.write(f"{state} {symbol} {next_state}\n")

    # create a dot file from the NFA transitions and also (try to) render it
    with open(policy_file_without_extension + '.dot', 'w') as f:
        f.write(createDot(transitions, startState))
    
    # save the dot file in the mbedtls_programs_policies directory also
    with open(f"mbedtls_programs_policies/{policy_file_name_without_extension}.dot", 'w') as f:
        f.write(createDot(transitions, startState))

    render(policy_file_without_extension + '.dot', policy_file_without_extension + '.png')

if __name__ == "__main__":
    # get the absolute path of the script
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # read db.pkl
    with open(script_dir + '/db.pkl', 'rb') as f:
        function_policies = pickle.load(f)
    
    # optionally accept a single file name as an argument
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', default=None)
    args = parser.parse_args()

    # walk over the mbedtls/programs directory and find all ".policy" files
    for root, dirs, files in os.walk(script_dir + "/../mbedtls/programs"):
        for file in files:
            if file.endswith(".policy"):
                if args.file is not None and os.path.basename(file) != f"{args.file}.policy":
                    continue
                print("Processing", os.path.basename(file))
                process_policy(os.path.join(root, file), function_policies)
