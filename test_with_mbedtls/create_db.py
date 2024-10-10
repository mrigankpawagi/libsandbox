import os
import pickle

# get the absolute path of the script
script_dir = os.path.dirname(os.path.realpath(__file__))

policy_files = []
function_policy_files = []
function_policies = {}

# walk over the mbedtls directory and find all ".policy" files and ".fpolicy" files
for root, dirs, files in os.walk(script_dir + "/../mbedtls"):
    for file in files:
        if file.endswith(".policy"):
            policy_files.append(os.path.join(root, file))
        if file.endswith(".fpolicy"):
            function_policy_files.append(os.path.join(root, file))

for policy_file in policy_files:
    file_name = os.path.basename(policy_file)
    file_name = file_name[:file_name.rfind(".")]
    
    # skip files in the 'mbedtls/programs' directory
    if policy_file.startswith(script_dir + "/../mbedtls/programs"):
        continue
    
    # find all function_policy_files that have the same prefix as the policy_file
    for function_policy_file in function_policy_files:
        function_file_name = os.path.basename(function_policy_file)
        function_file_name = function_file_name[:function_file_name.rfind(".")]
        
        if function_file_name.startswith(file_name):
            function_name = function_file_name[len(file_name)+1:]
            
            # skip if the function is "main"
            if function_name == "main":
                continue

            with open(function_policy_file, 'r') as f:
                policy = f.readlines()
            
            # note that we relabel the states by subtracting the value of start_state (which is always 0)
            original_start_state = int(policy[0].strip())
            start_state = "0"
            final_state = str(int(policy[1].strip()) - original_start_state)
            
            transitions = {}
            states = {start_state, final_state}
            for i in range(2, len(policy)):
                # skip empty lines
                if policy[i].strip() == "":
                    continue
                state, symbol, next_state = policy[i].split()
                state = str(int(state) - original_start_state)
                next_state = str(int(next_state) - original_start_state)
                if symbol == "0": symbol = ""
                if state not in transitions: transitions[state] = {}
                if symbol not in transitions[state]: transitions[state][symbol] = set()
                transitions[state][symbol].add(next_state)
                states.add(state)
                states.add(next_state)
            
            # if a state is missing, add it with no transitions
            for state in states:
                if state not in transitions:
                    transitions[state] = {}
                
            value = {
                "start_state": start_state,
                "final_state": final_state,
                "transitions": transitions
            }

            if function_name in function_policies and value in function_policies[function_name]:
                continue
                
            # we will store all "possible" policies for a function and then allow all of them!
            if function_name not in function_policies:
                function_policies[function_name] = []
            function_policies[function_name].append(value)

# dump the data to a file
with open(script_dir + "/db.pkl", 'wb') as f:
    pickle.dump(function_policies, f)
