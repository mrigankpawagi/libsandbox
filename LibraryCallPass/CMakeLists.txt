add_llvm_pass_plugin(LibraryCallPass
  LibraryCallPass.cpp
)

add_definitions(-DSOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}")
