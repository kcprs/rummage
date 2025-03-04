import importlib.util as _import_util
import inspect as _inspect
import logging as _logging
import sys as _sys
from functools import wraps as _wraps

import rummage as _rummage

_logging.basicConfig(level=_logging.DEBUG)

_this_module = _sys.modules[__name__]


def _import_module_from_file(file_path):
    _logging.debug(f"Dynamically importing module from {file_path}")

    # Derive a module name from the file path
    module_name = file_path.replace("/", ".").replace("\\", ".").rstrip(".py")

    # Create a module spec from the file location
    spec = _import_util.spec_from_file_location(module_name, file_path)

    if spec is None:
        raise ImportError(f"Cannot find module at {file_path}")

    # Create a new module based on the spec
    module = _import_util.module_from_spec(spec)

    # Execute the module in its own namespace
    assert spec.loader
    spec.loader.exec_module(module)

    # Add the module to sys.modules
    _sys.modules[module_name] = module

    return module


def _create_hook_wrappers(hook_module):
    """
    Create wrapper functions for hook functions. We do this to have full control of hook function's
    signatures. Wrappers conform to the signature required by lldb.

    Also, note that names of newly created wrapper functions may conceivably clash with functions
    defined directly in this module. For that reason:

      1. We only wrap functions with names that DON'T start with an underscore. This also has the
         benefit of allowing the user to write helper functions that will not be treated as hooks.

      2. ALL OBJECTS defined in this module should have names with a leading underscore.
    """

    hook_funcs = [
        obj
        for (name, obj) in _inspect.getmembers(hook_module, _inspect.isfunction)
        if not name.startswith("_")
    ]

    for hook_func in hook_funcs:
        _logging.debug(f"Creating wrapper for hook {hook_func.__name__}")

        # Must wrap wrapper creation in a function with default arg value, so that the wrapper refers
        # to the current `hook_func`. Otherwise all wrappers would refer to the last `hook_func` in
        # `_hook_funcs` due to late binding in Python closures.
        def add_hook_wrapper(func=hook_func):
            # We ignore args other than `frame`
            def hook_wrapper(frame, *_):
                _logging.debug(f"Executing hook wrapper for hook {func.__name__}")
                # Returning False tells lldb not to stop at the breakpoint.
                # Hook functions may return a truthy value to request stopping at the breakpoint.
                func(_rummage.StackFrame(frame))
                return False

            hook_wrapper.__name__ = func.__name__
            _logging.debug(f"Adding hook wrapper to {_this_module}. name: {func.__name__}, wrapper: {hook_wrapper}")
            setattr(_this_module, func.__name__, hook_wrapper)

        add_hook_wrapper()

def _cmd_load_wrapper_hooks(debugger, hook_file, *_):
    _ = debugger
    hook_module = _import_module_from_file(hook_file)
    _create_hook_wrappers(hook_module)


def __lldb_init_module(debugger, *_):
    debugger.HandleCommand(
        "command script add -f hook_wrappers._cmd_load_wrapper_hooks rummage_load_hooks"
    )


# Just to suppress "unused private function" lints
__lldb_init_module = __lldb_init_module
_cmd_load_wrapper_hooks = _cmd_load_wrapper_hooks
