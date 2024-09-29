# In-kernel Per-process Library Call Sandbox

## Requirements

1. [LLVM Clang](https://clang.llvm.org)
2. [LLVM `opt`](https://llvm.org/docs/CommandGuide/opt.html)
3. [Python 3](https://www.python.org)

## Generating a library call policy
From the root of the repository, run the following command.

```bash
$ python policygen.py <path-to-C-source-file>
```

This generates a `.dot` representation of the library call policy and a `.png` file to visualize it. It also generates a `.policy` file with the policy that can be used by the kernel module. These files are generated in the same directory as the input C source file.
