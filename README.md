# In-kernel Per-process Library Call Sandbox

## Generating a Library Call Policy

### Requirements

1. [LLVM Clang](https://clang.llvm.org)
2. [Python 3](https://www.python.org)
3. [GraphViz](https://graphviz.org)
4. [Pydot](https://github.com/pydot/pydot)

### Policy generation

From the root of the repository, run the following command.

```bash
python policygen.py <path-to-C-source-file>
```

This generates the following files in the same directory as the input C source file:

1. A `.dot` representation of the library call policy.
2. A `.png` file to visualize the policy.
3. A `.policy` file with the policy that can be used by the kernel module.
4. `.fpolicy` files with the function policies for each function in the input C source file.
5. An `.ll` file with the LLVM IR representation of the input C source file.
6. A compiled executable.

An example file, `example.c`, is provided at the root of the repository.

## Running Executables with the Policy

### Setting up the system
The instructions in this section are partly taken from Stephen Brennan's [tutorial on writing a system call](https://brennan.io/2016/11/14/kernel-dev-ep3/).

1. Download the Arch Linux virtual machine image from [OSBoxes](https://sourceforge.net/projects/osboxes/files/v/vb/4-Ar---c-x/20240601/CLI/64bit.7z/download). This machine has the root user `osboxes` with password `osboxes.org`. Boot the virtual machine and log in as the root user.

2. Install `bc` by running the following commands as root.

```bash
pacman -Syu
pacman -S bc
reboot
```

3. Download the Linux kernel source code and configure it.

```bash
curl -O -J https://www.kernel.org/pub/linux/kernel/v6.x/linux-6.11.5.tar.xz
tar xvf linux-6.11.5.tar.xz
cd linux-6.11.5
zcat /proc/config.gz > .config
```

You will also have to change the kernel name by setting `CONFIG_LOCALVERSION="-libsandbox"` in the `.config` file.

4. Add the dummy system call by adding the following line to `arch/x86/entry/syscalls/syscall_64.tbl`.

```tbl
999	common	dummy			sys_dummy
```

You also need to create an implementation for the system call by adding the following in `kernel/sys.c`.

```c
SYSCALL_DEFINE1(dummy, int, libcallno) {
	printk(KERN_INFO "Dummy syscall invoked with libcallno: %d\n", libcallno);
    return 0;
}
```

5. Compile the kernel and install it by running the script `monitor/deploy.sh` from the `linux-6.11.5` directory.

6. Reboot the virtual machine and log back in as the root user.

7. Install the necessary packages by running the script `monitor/setup.sh`.

### Running the executable

1. Copy the file `LibraryCallPass/functions.txt` to `/root/.libsandbox/` on the virtual machine. This file is generated automatically when policies are created and contains the mapping from function names to their integer codes.

2. Copy the generated executable along with its `.policy` file to the virtual machine. Create a configuration file for the executable in the same directory as the executable. The configuration file contains a single line with the path to the `.policy` file for the executable.

3. Copy `monitor/monitor.c` and `monitor/monitor.py` to the virtual machine. The `monitor.py` file is the entry point for the sandbox and should be run as the root user in the following manner.

```bash
python path/to/monitor.py [--functions=FUNCTIONS] [--config=CONFIG] executable ...args
```

You can use the `-h` flag on the `monitor.py` script to see the help message. 
Here `executable` is the path to the executable to be run. The optional `--functions` flag provides the path to the `functions.txt` file, and is by default set to `/root/.libsandbox/functions.txt`. The optional `--config` flag provides the path to the configuration file for the executable, and is by default set to the executable path with the `.config` extension. Any command-line arguments after the executable are passed to the executable.

The system call monitor is built using the [BCC](https://github.com/iovisor/bcc) toolkit for eBPF.

## Testing with Mbed TLS

### Building Mbed TLS

1. From the root of this repository, clone the `mbedtls` [repository](https://github.com/Mbed-TLS/mbedtls) and pull all the submodules.

```bash
git clone https://github.com/Mbed-TLS/mbedtls && cd mbedtls
git submodule update --init
git checkout 46771295f2f49d8f9b91532c84d45fde4e35a5b9 # This is the commit used for testing
```

2. Build the library with the plugin using the following commands from the `mbedtls` directory.

```bash
python -m venv env
source env/bin/activate
pip install -r scripts/basic.requirements.txt pydot
mkdir build && cd build
python ../../test_with_mbedtls/build.py
```

### Generating Policies
We will generate policies for the example programs in the `programs` directory of the `mbedtls` repository. The outputs will be generated in the same directory as the input C source file. Execute the following commands from the root of this repository.

```bash
python test_with_mbedtls/create_db.py
python test_with_mbedtls/generate.py
```

Note that the generation of an intermediate `.ll` file is not done while compiling modules in the `mbedtls` repository with our compiler plugin. This will create `.policy` and `.fpolicy` files for each C source file in `mbedtls`. Note that these `.policy` files are _unflattened_ policies. For C source files in `mbedtls/programs`, `.dot` files corresponding to _flattened_ policies are also generated (`.png` files may be generated for small graphs). These files are placed in the same directory as the input C source file. The flattened `.policy` files (and their corresponding `.dot` files) are dumped into the `mbedtls_programs_policies/` directory. An `ignore.txt` file is also generated in the `mbedtls_programs_policies/` directory, which contains the names of all the Mbed TLS functions that were resolved.

Optionally, the name of the module to be processed can be passed as an argument to `generate.py`. For example, to generate policies only for the `strerror` module, run `python test_with_mbedtls/generate.py strerror`.

### Running the programs
The executables generated by the `build.py` script should be copied to the virtual machine, along with their policies in the `mbedtls_programs_policies/` directory. The `ignore.txt` file should also be copied to the virtual machine. The configuration files for the executables should contain the path to the corresponding `.policy` file in the first line, and the path to `ignore.txt` in the second line. These can then be run using the `monitor.py` script as usual.
