# In-kernel Per-process Library Call Sandbox

## Requirements

1. [LLVM Clang](https://clang.llvm.org)
2. [Python 3](https://www.python.org)
3. [GraphViz](https://graphviz.org)
4. [Pydot](https://github.com/pydot/pydot)

## Generating a library call policy
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

Note that the generation of an intermediate `.ll` file is not done while compiling modules in the `mbedtls` repository with our compiler plugin. This will create `.policy` and `.fpolicy` files for each C source file in `mbedtls`. Note that these `.policy` files are _unflattened_ policies. For C source files in `mbedtls/programs`, `.dot` files corresponding to _flattened_ policies are also generated (`.png` files may be generated for small graphs). These files are placed in the same directory as the input C source file. The flattened `.policy` files (and their corresponding `.dot` files) are dumped into the `mbedtls_programs_policies/` directory.

Optionally, the name of the module to be processed can be passed as an argument to `generate.py`. For example, to generate policies only for the `strerror` module, run `python test_with_mbedtls/generate.py strerror`.
