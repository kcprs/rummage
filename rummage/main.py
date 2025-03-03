import argparse
import subprocess as sp
from pathlib import Path
import logging

import rummage

logging.basicConfig(level=logging.DEBUG)


def run(hook_file):
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
    ]
    logging.debug(f"Running cmd {cmd}")
    sp.run(cmd)


def main():
    parser = argparse.ArgumentParser(prog="rummage")
    parser.add_argument(
        "hook_file", help="Path to file containing rummage hook functions"
    )

    args = parser.parse_args()
    run(args.hook_file)


if __name__ == "__main__":
    main()
