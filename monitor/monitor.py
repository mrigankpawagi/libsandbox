from bcc import BPF
import argparse
import os
import subprocess
import warnings

warnings.filterwarnings("ignore", message=".*Possibly lost.*")

# get the script path
script_path = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":
    # accept 3 arguments: path to functions.txt, path to executable (to monitor), and path to config file
    # functions.txt is optional and defaults to ~/.libsandbox/functions.txt
    # config file is also optional and defaults to {executable}.config
    parser = argparse.ArgumentParser(description="Run executable in the Library Call Sandbox")
    parser.add_argument("--functions", default="~/.libsandbox/functions.txt", help="Path to functions.txt")
    parser.add_argument("--config", help="Path to config file")
    
    parser.add_argument("executable", help="Path to executable to monitor")

    # the executable may have arguments, so we need to accept them as well
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments to pass to the executable")    
    
    args = parser.parse_args()
    
    # check if functions.txt exists and if yes, read it into a dictionary 
    functions = {}
    functions_path = os.path.expanduser(args.functions)
    if not os.path.exists(functions_path):
        print(f"Error: functions.txt not found at {functions_path}")
        exit(1)
    with open(functions_path, "r") as f:
        for line in f:
            function_name, libcallno = line.strip().split()
            functions[int(libcallno)] = function_name
    
    # check if executable exists
    executable_path = args.executable
    if not os.path.exists(executable_path):
        print(f"Error: executable not found at {executable_path}")
        exit(1)
        
    # check if config file exists and if yes, read it into a dictionary
    if args.config:
        config_path = args.config
    else:
        config_path = f"{executable_path}.config"
    config = {}
    if not os.path.exists(config_path):
        print(f"Error: config file not found at {config_path}")
        exit(1)
    with open(config_path, "r") as f:
        # the first line is the path to policy
        # if the second line exists, it is the path to the ignores file
        policy_path = f.readline().strip()
        config["policy"] = policy_path
        ignores_path = f.readline().strip()
        if ignores_path:
            config["ignores"] = ignores_path
        else:
            config["ignores"] = None

    # check that the policy file exists. if yes, read it into a dictionary (to store an NFA)
    if not os.path.exists(policy_path):
        print(f"Error: policy file not found at {policy_path}")
        exit(1)
    with open(policy_path, 'r') as f:
        policy = f.readlines()

    startState = policy[0].strip()
    transitions = {}
    states = {startState}

    for i in range(1, len(policy)):
        state, symbol, nextState = policy[i].split()
        if state not in transitions:
            transitions[state] = {}
        if symbol not in transitions[state]:
            transitions[state][symbol] = set()
        transitions[state][symbol].add(nextState)
        states.add(state)
        states.add(nextState)

    # if the ignores_path is not None, check it exists and read it into a set
    ignores = set()
    if config["ignores"]:
        if not os.path.exists(config["ignores"]):
            print(f"Error: ignores file not found at {config['ignores']}")
            exit(1)
        with open(config["ignores"], "r") as f:
            for line in f:
                ignores.add(line.strip())
    
    # Load the BPF program
    b = BPF(src_file=f"{script_path}/monitor.c")
    b.attach_kprobe(event="__x64_sys_dummy", fn_name="syscall__dummy")
    
    pid = None # will be set to the pid of the process being monitored
    nfa_frontier = {startState} # the frontier of the NFA

    # Define the callback function to get pid and libcallno from events
    def get_event(cpu, data, size):
        global pid, nfa_frontier, ignores, functions, transitions
        event = b["events"].event(data)
        event_pid = event.pid
        event_libcallno = event.libcallno
        
        # if the pid is set, check if the event is from the process being monitored
        if pid and event_pid == pid:
            function_name = functions[event_libcallno]
            
            # ignore if the libcallno corresponds to a function in the ignores set
            if function_name in ignores:
                return
            
            # advance the frontier of the NFA
            # go to all the frontier states and see if there is a transition on the current symbol
            new_frontier = set()
            for state in nfa_frontier:
                if function_name in transitions[state]:
                    new_frontier.update(transitions[state][function_name])
            
            # if the new frontier is empty, the NFA is stuck 
            # and we should kill the process being monitored
            if not new_frontier:
                os.kill(pid, 9)
            else:
                nfa_frontier = new_frontier            

    # Set up the callback
    b["events"].open_perf_buffer(get_event, page_cnt=128)

    # Launch the executable and get its pid
    proc = subprocess.Popen([executable_path] + args.args, shell=False)
    pid = proc.pid

    while True:
        # Check if the process is still running
        retcode = proc.poll() # exit code
        if retcode is not None:
            break
        try:
            # b.perf_buffer_poll should not block the loop (as it inteferes with the retcode check)
            # so we need to use a timeout
            b.perf_buffer_poll(timeout=10)
            
        except KeyboardInterrupt:
            break
