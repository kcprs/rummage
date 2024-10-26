from __future__ import annotations

import inspect
import os
import sys

import __main__ as this_module

import loupe_hooks
from loupe import Breakpoint, Frame, GlobalFileWriter, Target

####################################################################################################
# Create wrapper functions for hook functions. We do this to have full control of hook function's
# signatures. Wrappers conform to the signature required by lldb.
#
# This must be done in outer scope (at module import time) so that the wrappers are visible to lldb
# when the module is imported.
#
# Also, note that names of newly created wrapper functions may conceivably clash with functions
# defined directly in this module. For that reason:
#
#   1. We only wrap functions with names that DON'T start with an underscore. This also has the
#      benefit of allowing the user to write helper functions that will not be treated as hooks.
#
#   2. ALL functions defined in this module should have names with a leading underscore.

_hook_funcs = [
    obj
    for (name, obj) in inspect.getmembers(loupe_hooks, inspect.isfunction)
    if not name.startswith("_")
]

for hook_func in _hook_funcs:
    # We ignore args other than `frame`
    def wrapper(frame, *_):
        hook_func(Frame(frame))
        # Returning False tells lldb not to stop at the breakpoint
        return False

    setattr(this_module, hook_func.__name__, wrapper)
####################################################################################################


def _set_breakpoints(target: Target):
    for hook_func in _hook_funcs:
        b = Breakpoint.from_regex(target, r"@loupe\s*:\s*" + hook_func.__name__)
        b.set_callback(getattr(this_module, hook_func.__name__))


def _main(debugger):
    debugger.SetAsync(False)

    target = debugger.CreateTarget(loupe_hooks.EXE)

    _set_breakpoints(Target(target))

    # Launch
    with GlobalFileWriter():
        # TODO: This blocks only until the debugger stops at a breakpoint.
        # This is not a problem if we set ALL breakpoints to auto-continue.
        # Otherwise, we have to switch to async mode and periodically check process status.
        target.LaunchSimple(loupe_hooks.ARGS, None, ".")


def __lldb_init_module(debugger, *_):
    _main(debugger)


# Just to suppress "unused private function" lints
__lldb_init_module = __lldb_init_module


if __name__ == "__main__":
    rel_path = os.path.relpath(os.path.abspath(__file__), os.getcwd())
    print("This script can only be used within an interactive lldb session.")
    print("You can run it with this one-liner:\n")
    # TODO: outdated help
    print(f"    lldb --one-line-before-file 'command script import {rel_path}'")
    sys.exit()
