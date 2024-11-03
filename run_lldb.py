from __future__ import annotations

import inspect
import os
import sys

import rummage_hooks
from rummage import Breakpoint, StackFrame, GlobalFileWriter, Target

_this_module = sys.modules[__name__]
_hook_funcs = [
    obj
    for (name, obj) in inspect.getmembers(rummage_hooks, inspect.isfunction)
    if not name.startswith("_")
]

def _create_hook_wrappers():
    """
    Create wrapper functions for hook functions. We do this to have full control of hook function's
    signatures. Wrappers conform to the signature required by lldb.

    Also, note that names of newly created wrapper functions may conceivably clash with functions
    defined directly in this module. For that reason:

      1. We only wrap functions with names that DON'T start with an underscore. This also has the
         benefit of allowing the user to write helper functions that will not be treated as hooks.

      2. ALL functions defined in this module should have names with a leading underscore.
    """

    for hook_func in _hook_funcs:
        print(f"Creating wrapper for hook {hook_func.__name__}")

        # Must wrap wrapper creation in a function with default arg value, so that the wrapper refers
        # to the current `hook_func`. Otherwise all wrappers would refer to the last `hook_func` in
        # `_hook_funcs` due to late binding in Python closures.
        def make_hook_wrapper(func=hook_func):
            # We ignore args other than `frame`
            def hook_wrapper(frame, *_):
                print(f"Executing hook wrapper for hook {func.__name__}")
                # Returning False tells lldb not to stop at the breakpoint.
                # Hook functions may return a truthy value to request stopping at the breakpoint.
                return bool(func(StackFrame(frame)))

            return hook_wrapper

        setattr(_this_module, hook_func.__name__, make_hook_wrapper())

    print("Module has:")
    print(dir(_this_module))


# This must be done at module import time so that the wrappers are visible to lldb when the
# module is imported.
_create_hook_wrappers()


def _set_breakpoints(target: Target):
    for hook_func in _hook_funcs:
        b = Breakpoint.from_regex(target, r"@rummage\s*:\s*" + hook_func.__name__)
        b.set_callback_via_path(f"{__name__}.{hook_func.__name__}")


def _main(debugger):
    debugger.SetAsync(False)

    target = debugger.CreateTarget(rummage_hooks.EXE)

    _set_breakpoints(Target(target))

    # Launch
    with GlobalFileWriter():
        # TODO: This blocks only until the debugger stops at a breakpoint.
        # This is not a problem if we set ALL breakpoints to auto-continue.
        # Otherwise, we have to switch to async mode and periodically check process status.
        target.LaunchSimple(rummage_hooks.ARGS, None, ".")


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
