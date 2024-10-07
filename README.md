# In-kernel Per-process Library Call Sandbox

## Requirements

1. [LLVM Clang](https://clang.llvm.org)
2. [Python 3](https://www.python.org)
3. [GraphViz](https://graphviz.org)

## Generating a library call policy
From the root of the repository, run the following command.

```bash
python policygen.py <path-to-C-source-file>
```

This generates a `.dot` representation of the library call policy and a `.png` file to visualize it. It also generates a `.policy` file with the policy that can be used by the kernel module. These files are generated in the same directory as the input C source file.

## Testing with Mbed TLS

### Building Mbed TLS

1. From the root of this repository, clone the `mbedtls` [repository](https://github.com/Mbed-TLS/mbedtls) and pull all the submodules.

```bash
git clone https://github.com/Mbed-TLS/mbedtls
git submodule update --init
git checkout 46771295f2f49d8f9b91532c84d45fde4e35a5b9 # This is the commit used for testing
```

2. Build the library using the following commands.

```bash
python -m venv env
source env/bin/activate
pip install -r scripts/basic.requirements.txt
make
```

You can run `make test` to check if the library is built correctly.

### Generating Policies
We will generate policies for the example programs in the `programs` directory of the `mbedtls` repository. The outputs will be generated in the same directory as the input C source file.

```bash
python test_with_mbedtls.py
```
