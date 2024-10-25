default: format check

alias f := format
format:
	isort .
	black .

alias c := check
check:
	pyright --warnings .

update_dev_deps:
	pip freeze > pip-requirements-dev.txt

alias b := build
build:
    -mkdir _build
    clang -g -o _build/test_exe main.c

lldb:
    lldb -b \
    -O 'command script import loupe.py' \
    -O 'command script import breaks.py' \
    -O 'command script import run_lldb.py'
