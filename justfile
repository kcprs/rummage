default: format check

alias f := format
format:
    isort .
    black .
    fd -e '.c' -x clang-format -i

alias c := check
check:
    pyright --warnings .

alias b := build
build:
    -mkdir _build
    clang -g -o _build/test_exe main.c

lldb: build check
    # TODO: This should be replaced by a main package script
    lldb -b -Q \
    -O 'command script import rummage/rummage.py' \
    -O 'command script import rummage/run_lldb.py' \
