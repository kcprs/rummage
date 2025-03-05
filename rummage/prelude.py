import logging
import subprocess as sp
import sys


def _cmd_load_venv(debugger, *_):
    _ = debugger
    result = sp.run(
        ["python3", "-c", "import sys;print('\\n'.join(sys.path).strip())"],
        capture_output=True,
    )

    if result.returncode != 0:
        print(result.stderr.decode("utf-8"))
        result.check_returncode()

    paths = result.stdout.decode("utf-8").split()
    logging.info(f"Extending sys.path with paths: {paths}")
    sys.path.extend(paths)


def _cmd_set_log_level(debugger, level: str, *_):
    _ = debugger
    # Note that `level` is passed from a lldb command, so it's always a str, even when value is None.
    if level != "None":
        logging.basicConfig(level=level.upper())


def __lldb_init_module(debugger, *_):
    debugger.HandleCommand(
        "command script add -f prelude._cmd_set_log_level rummage_set_log_level "
    )
    debugger.HandleCommand(
        "command script add -f prelude._cmd_load_venv rummage_load_venv "
    )


# Just to suppress "unused private function" lints
__lldb_init_module = __lldb_init_module
_cmd_load_venv = _cmd_load_venv
_cmd_set_log_level = _cmd_set_log_level
