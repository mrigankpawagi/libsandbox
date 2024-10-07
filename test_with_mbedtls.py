import os

skip_list = [
    "psa/psa_constant_names",
    "test/benchmark",
    "test/metatest",
    "test/selftest",
] # currently not supported

# get the absolute path of the script
script_dir = os.path.dirname(os.path.realpath(__file__))

# git reset the Makefile
os.system('git checkout -- ' + script_dir + '/mbedtls/programs/Makefile')

# open {script_dir}/mbedtls/programs/Makefile
with open(script_dir + '/mbedtls/programs/Makefile', 'r') as f:
    makefile = f.readlines()
    
# find all lines with "$(EXEXT):"
exext_line_numbers = [i for i, line in enumerate(makefile) if '$(EXEXT):' in line]

insertions = []

for line_number in exext_line_numbers:
    # take the prefix of the line to get the target
    target = makefile[line_number].split('$(EXEXT):')[0].strip()
    
    # skip if the target is in skip_list
    if target in skip_list:
        continue
    
    # starting from line_number, find the first line which contains $(CC)
    for i in range(line_number, len(makefile)):
        if '$(CC)' in makefile[i]:
            break

    insertions.append((i, i+1, 
                       "\t" + makefile[i].replace('$(CC)', 'clang').strip() + f" -O0 -fpass-plugin=/home/mrigankp/libsandbox/build/LibraryCallPass/LibraryCallPass.so -Wno-unused-command-line-argument\n" 
                       + f"\tpython ../../render.py {target}.dot\n"
                    ))

# insert the lines
for start, end, insertion in insertions[::-1]:
    makefile = makefile[:start] + [insertion] + makefile[end:]

# write back to the file
with open(script_dir + '/mbedtls/programs/Makefile', 'w') as f:
    f.write(''.join(makefile))
