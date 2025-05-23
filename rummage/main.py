import argparse
import os
import subprocess as sp
from pathlib import Path

import rummage


def run(hook_file, exe, args, *, log_level):
    rummage_dir = Path(rummage.__file__).parent

    prelude_file = rummage_dir / "prelude.py"
    wrappers_file = rummage_dir / "hook_wrappers.py"
    launch_file = rummage_dir / "launch.py"

    hook_file = Path(hook_file)
    if not hook_file.is_absolute():
        hook_file = Path(os.getcwd()) / hook_file

    # Generate flag to interleave with lldb commands
    def flag():
        while True:
            yield "--one-line-before-file"

    lldb_cmds = [
        f"command script import {prelude_file}",
        f"rummage_set_log_level {log_level}",
        "rummage_load_venv",
        f"command script import {wrappers_file}",
        f"rummage_load_hooks {hook_file}",
        f"command script import {launch_file}",
        f"rummage_set_launch_exe {exe}",
        f"rummage_set_launch_args {' '.join(args)}",
        "rummage_launch",
    ]

    cmd = [
        "lldb",
        "--batch",
        "--source-quietly",
        *[x for pair in zip(flag(), lldb_cmds) for x in pair],
    ]

    sp.run(cmd)


def main():
    parser = argparse.ArgumentParser(prog="rummage")
    parser.add_argument(
        "hook_file", help="Path to file containing rummage hook functions"
    )
    parser.add_argument(
        "--log-level",
        help="Level of detail for logging rummage internals",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
    )
    parser.add_argument("exe", help="Path to the executable to be debugged")
    parser.add_argument("arg", nargs="*", help="Arguments to the debugged executable")

    args = parser.parse_args()
    run(args.hook_file, args.exe, args.arg, log_level=args.log_level)


if __name__ == "__main__":
    main()
