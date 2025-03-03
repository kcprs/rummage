import argparse
import logging
import subprocess as sp
from pathlib import Path

import rummage

logging.basicConfig(level=logging.DEBUG)


def run(hook_file, exe, args):
    rummage_dir = Path(rummage.__file__).parent

    core_file = rummage_dir / "core.py"
    run_file = rummage_dir / "run.py"

    hook_file_name = Path(hook_file).name
    # TODO: Figure out customizable names
    assert hook_file_name == "rummage_hooks.py"

    cmd = [
        "lldb",
        "--batch",
        # "--source-quietly",
        "--one-line-before-file",
        f"command script import {core_file}",
        "--one-line-before-file",
        f"command script import {hook_file}",
        "--one-line-before-file",
        f"command script import {run_file}",
        "--one-line-before-file",
        f"rummage_set_launch_exe {exe}",
        "--one-line-before-file",
        f"rummage_set_launch_args {' '.join(args)}",
        "--one-line-before-file",
        "rummage_launch",
    ]
    logging.debug(f"Running cmd {cmd}")
    sp.run(cmd)


def main():
    parser = argparse.ArgumentParser(prog="rummage")
    parser.add_argument(
        "hook_file", help="Path to file containing rummage hook functions"
    )
    parser.add_argument("exe", help="Path to the executable to be debugged")
    parser.add_argument("arg", nargs="*", help="Arguments to the debugged executable")

    args = parser.parse_args()
    run(args.hook_file, args.exe, args.arg)


if __name__ == "__main__":
    main()
