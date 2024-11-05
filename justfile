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
    rummage tests/rummage_hooks.py
