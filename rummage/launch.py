import inspect as _inspect
import logging as _logging
import shlex as _shlex
import sys as _sys

import hook_wrappers  # type: ignore

import rummage as _rummage

_logging.basicConfig(level=_logging.DEBUG)

_launch_config = _rummage.LaunchConfig()


def _set_breakpoints(target: _rummage.Target):
    _logging.debug("Setting breakpoints")
    hook_funcs = [
        (name, obj)
        for (name, obj) in _inspect.getmembers(hook_wrappers, _inspect.isfunction)
        if not name.startswith("_")
    ]

    for name, hook_func in hook_funcs:
        _logging.debug(
            f"Breakpoint for hook {hook_func} with name {name} and __name__ {hook_func.__name__}"
        )
        b = _rummage.Breakpoint.from_regex(
            target, r"@rummage\s*:\s*" + hook_func.__name__ + "$"
        )
        b.set_callback_via_path(f"{hook_wrappers.__name__}.{hook_func.__name__}")


def _cmd_set_launch_exe(debugger, exe, *_):
    _ = debugger
    _logging.debug(f"Setting launch exe to: {exe}")
    _launch_config.exe = exe


def _cmd_set_launch_args(debugger, args, *_):
    _ = debugger
    _logging.debug(f"Setting launch args to: {args}")
    _launch_config.args = _shlex.split(args)


def _cmd_launch(debugger, *_):
    debugger.SetAsync(False)

    target = debugger.CreateTarget(_launch_config.exe)

    _set_breakpoints(_rummage.Target(target))

    # Launch
    with _rummage.GlobalFileWriter():
        # TODO: This blocks only until the debugger stops at a breakpoint.
        # This is not a problem if we set ALL breakpoints to auto-continue.
        # Otherwise, we have to switch to async mode and periodically check process status.
        _logging.debug("Launching debug target")
        target.LaunchSimple(_launch_config.args, None, ".")


def __lldb_init_module(debugger, *_):
    debugger.HandleCommand(
        "command script add -f launch._cmd_set_launch_exe rummage_set_launch_exe"
    )
    debugger.HandleCommand(
        "command script add -f launch._cmd_set_launch_args rummage_set_launch_args"
    )
    debugger.HandleCommand("command script add -f launch._cmd_launch rummage_launch")


# Just to suppress "unused private function" lints
__lldb_init_module = __lldb_init_module
_cmd_set_launch_exe = _cmd_set_launch_exe
_cmd_set_launch_args = _cmd_set_launch_args
_cmd_launch = _cmd_launch
