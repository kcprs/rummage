import logging
import subprocess as sp
import sys

logging.basicConfig(level=logging.INFO)


def load_venv():
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
    _ = debugger
    load_venv()


# Just to suppress "unused private function" lints
__lldb_init_module = __lldb_init_module
