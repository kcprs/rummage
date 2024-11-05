import inspect as _inspect
import logging as _logging
import os as _os
import sys as _sys

import rummage_hooks as _rummage_hooks # type: ignore

import rummage as _rummage

# _logging.basicConfig(level=_logging.DEBUG)

_this_module = _sys.modules[__name__]
_hook_funcs = [
    obj
    for (name, obj) in _inspect.getmembers(_rummage_hooks, _inspect.isfunction)
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

      2. ALL OBJECTS defined in this module should have names with a leading underscore.
    """

    for hook_func in _hook_funcs:
        _logging.debug(f"Creating wrapper for hook {hook_func.__name__}")

        # Must wrap wrapper creation in a function with default arg value, so that the wrapper refers
        # to the current `hook_func`. Otherwise all wrappers would refer to the last `hook_func` in
        # `_hook_funcs` due to late binding in Python closures.
        def make_hook_wrapper(func=hook_func):
            # We ignore args other than `frame`
            def hook_wrapper(frame, *_):
                _logging.debug(f"Executing hook wrapper for hook {func.__name__}")
                # Returning False tells lldb not to stop at the breakpoint.
                # Hook functions may return a truthy value to request stopping at the breakpoint.
                return bool(func(_rummage.StackFrame(frame)))

            return hook_wrapper

        setattr(_this_module, hook_func.__name__, make_hook_wrapper())

    _logging.debug(f"Module {__name__} has attrs: {dir(_this_module)}")


# This must be done at module import time so that the wrappers are visible to lldb when the
# module is imported.
_create_hook_wrappers()


def _set_breakpoints(target: _rummage.Target):
    for hook_func in _hook_funcs:
        b = _rummage.Breakpoint.from_regex(
            target, r"@rummage\s*:\s*" + hook_func.__name__
        )
        b.set_callback_via_path(f"{__name__}.{hook_func.__name__}")


def _main(debugger):
    debugger.SetAsync(False)

    target = debugger.CreateTarget(_rummage_hooks.EXE)

    _set_breakpoints(_rummage.Target(target))

    # Launch
    with _rummage.GlobalFileWriter():
        # TODO: This blocks only until the debugger stops at a breakpoint.
        # This is not a problem if we set ALL breakpoints to auto-continue.
        # Otherwise, we have to switch to async mode and periodically check process status.
        target.LaunchSimple(_rummage_hooks.ARGS, None, ".")


def __lldb_init_module(debugger, *_):
    _main(debugger)


# Just to suppress "unused private function" lints
__lldb_init_module = __lldb_init_module


if __name__ == "__main__":
    rel_path = _os.path.relpath(_os.path.abspath(__file__), _os.getcwd())
    print("This script can only be used within an interactive lldb session.")
    print("You can run it with this one-liner:\n")
    # TODO: outdated help
    print(f"    lldb --one-line-before-file 'command script import {rel_path}'")
    _sys.exit()
