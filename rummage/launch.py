import logging
import shlex

import hook_wrappers  # type: ignore

import rummage

LAUNCH_CONFIG = rummage.LaunchConfig()


def set_breakpoints(target: rummage.Target):
    logging.info("Setting breakpoints")

    hook_fn_names = [name for (name, _) in rummage.get_hook_fns(hook_wrappers)]

    for cb_name in hook_fn_names:
        b = rummage.Breakpoint.from_regex(target, r"@rummage\s*:\s*" + cb_name + "$")
        b.set_callback_via_path(f"{hook_wrappers.__name__}.{cb_name}")


def _cmd_set_launch_exe(debugger, exe, *_):
    _ = debugger
    logging.info(f"Setting launch exe to: {exe}")
    LAUNCH_CONFIG.exe = exe


def _cmd_set_launch_args(debugger, args, *_):
    _ = debugger
    logging.info(f"Setting launch args to: {args}")
    LAUNCH_CONFIG.args = shlex.split(args)


def _cmd_launch(debugger, *_):
    debugger.SetAsync(False)
    target = debugger.CreateTarget(LAUNCH_CONFIG.exe)
    set_breakpoints(rummage.Target(target))

    # Launch
    with rummage.GlobalFileWriter():
        # TODO: This blocks only until the debugger stops at a breakpoint.
        # This is not a problem if we set ALL breakpoints to auto-continue.
        # Otherwise, we have to switch to async mode and periodically check process status.
        logging.info("Launching debug target")
        target.LaunchSimple(LAUNCH_CONFIG.args, None, ".")


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
