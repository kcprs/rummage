import importlib.util as _import_util
import json as _json
import logging as _logging
import sys as _sys

import lldb as _lldb

import rummage as _rummage

_this_module = _sys.modules[__name__]


def _import_module_from_file(file_path):
    _logging.info(f"Dynamically importing module from {file_path}")

    module_name = file_path.replace("/", ".").replace("\\", ".").rstrip(".py")

    spec = _import_util.spec_from_file_location(module_name, file_path)
    assert spec

    module = _import_util.module_from_spec(spec)

    assert spec.loader
    spec.loader.exec_module(module)

    _sys.modules[module_name] = module

    return module


def _create_hook_wrappers(hook_module):
    """
    Create wrappers for hook functions. We do this to have full control of hook function's
    signatures. Wrappers conform to the signature required by lldb.

    Also, note that names of newly created wrapper functions added to this module may conceivably
    clash with functions defined directly in this module. For that reason:

      1. We only wrap functions with names that DON'T start with an underscore. This also has the
         benefit of allowing the user to write provate helper functions that will not be treated
         as hooks.

      2. ALL OBJECTS defined in this module should have names with a leading underscore.
    """

    for name, fn in _rummage.get_hook_fns(hook_module):
        _logging.info(f"Creating wrapper for hook {name}")

        # Must wrap wrapper creation in a function with default arg values, so that the wrapper refers
        # to the current `fn`. Otherwise all wrappers would refer to the last `name` and `fn` in
        # `hook_fns` due to late binding in Python closures.
        def add_hook_wrapper(name=name, fn=fn):
            # We ignore args other than `frame`
            def hook_wrapper(
                frame: _lldb.SBFrame,
                bp_loc: _lldb.SBBreakpointLocation,
                extra_args: _lldb.SBStructuredData,
                *_,
            ):
                _logging.info(f"Executing hook wrapper for hook {name}")

                # TODO: pass Python objects into hooks, e.g. a Target instance
                stream = _lldb.SBStream()
                extra_args.GetAsJSON(stream)
                extra_dict = _json.loads(stream.GetData())

                # Returning False tells lldb not to stop at the breakpoint.
                # Hook functions may return a truthy value to request stopping at the breakpoint.
                return bool(fn(_rummage.StackFrame(frame), extra_dict))

            _logging.debug(
                f"Adding hook wrapper to {_this_module}; "
                f"name: {name}, wrapper: {hook_wrapper}"
            )
            setattr(_this_module, name, hook_wrapper)

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
