import logging
import subprocess as sp
import sys


def _cmd_load_venv(*_):
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


def __lldb_init_module(debugger, *_):
    debugger.HandleCommand(
        "command script add -f venv._cmd_load_venv rummage_load_venv"
    )


# Just to suppress "unused private function" lints
__lldb_init_module = __lldb_init_module
_cmd_load_venv = _cmd_load_venv
