# find_package(LLVM REQUIRED CONFIG)

# list(APPEND CMAKE_MODULE_PATH "${LLVM_CMAKE_DIR}")
# include(LLVMConfig)

# set(LLVM_LINK_COMPONENTS
#   Core
#   Support
# )

add_llvm_pass_plugin(LibraryCallPass
  LibraryCallPass.cpp
)

# option(ENABLE_LLVM_SHARED "Enable building against LLVM shared libraries" ON)
