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
    rummage tests/rummage_hooks.py _build/test_exe arg1 arg2

raw: build check
    lldb --batch \
    --one-line-before-file \
    'command script import ./rummage/core.py' \
    --one-line-before-file \
    'command script import ./tests/rummage_hooks.py' \
    --one-line-before-file \
    'command script import ./rummage/run.py' \
    --one-line-before-file \
    'rummage_set_launch_exe ./_build/test_exe' \
    --one-line-before-file \
    'rummage_set_launch_args arg1 arg2' \
    --one-line-before-file \
    rummage_launch
