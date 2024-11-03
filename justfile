default: format check

alias f := format
format:
    isort .
    black .
    fd -e '.c' -x clang-format -i

alias c := check
check:
    pyright --warnings .

update_dev_deps:
    pip freeze > pip-requirements-dev.txt

alias b := build
build:
    -mkdir _build
    clang -g -o _build/test_exe main.c

lldb: build check
    lldb \
    -O 'command script import rummage.py' \
    -O 'command script import run_lldb.py' \
    -b \
