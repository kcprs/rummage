from __future__ import annotations

import inspect
import os
import sys

import breakpoints
from loupe import Breakpoint, GlobalFileWriter, Target

EXE = "_build/test_exe"
ARGS = "arg1 arg2".split(" ")


def set_breakpoints(target: Target):
    print("Searching for break functions")
    break_funcs = [
        obj
        for (name, obj) in inspect.getmembers(breakpoints, inspect.isfunction)
        if not name.startswith("_")
    ]
    print(f"Found break functions: {breakpoints}")

    for func in break_funcs:
        b = Breakpoint.from_regex(target, r"@loupe\s*:\s*" + func.__name__)
        b.set_callback(func)


def main(debugger):
    debugger.SetAsync(False)

    target = debugger.CreateTarget(EXE)

    set_breakpoints(Target(target))

    # Launch
    with GlobalFileWriter():
        # TODO: This blocks only until the debugger stops at a breakpoint.
        # This is not a problem if we set ALL breakpoints to auto-continue.
        # Otherwise, we have to switch to async mode and periodically check process status.
        target.LaunchSimple(ARGS, None, ".")


def __lldb_init_module(debugger, _dict):
    main(debugger)


if __name__ == "__main__":
    rel_path = os.path.relpath(os.path.abspath(__file__), os.getcwd())
    print("This script can only be used within an interactive lldb session.")
    print("You can run it with this one-liner:\n")
    print(f"    lldb --one-line-before-file 'command script import {rel_path}'")
    sys.exit()
