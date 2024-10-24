from __future__ import annotations

import os
import re
import sys
from typing import Iterable, Optional

if __name__ == "__main__":
    rel_path = os.path.relpath(os.path.abspath(__file__), os.getcwd())
    print("This script can only be used within an interactive lldb session.")
    print("You can run it with this one-liner:\n")
    print(f"    lldb --one-line-before-file 'command script import {rel_path}'")
    sys.exit()

# Import lldb only if not in __main__ - the import will most likely fail otherwise
import lldb

"""
NOTES

Good references:

https://lldb.llvm.org/use/python-reference.html
https://github.com/llvm/llvm-project/tree/main/lldb/examples/python
https://gist.github.com/nkaretnikov/6ee00afabf73332c5a89eacb610369c2
"""

EXE = "_build/test_exe"
ARGS = "arg1 arg2".split(" ")


class GlobalFileWriter:
    _instance: Optional[GlobalFileWriter] = None

    def __init__(self) -> None:
        self._files = dict()

    @staticmethod
    def instance():
        assert (
            GlobalFileWriter._instance is not None
        ), "Initialise using context manager: `with FileOutput():"
        return GlobalFileWriter._instance

    def write(self, path: str, text: str):
        if path not in self._files.keys():
            self._files[path] = open(path, "w")
        self._files[path].write(text)

    def __enter__(self):
        if GlobalFileWriter._instance is None:
            GlobalFileWriter._instance = GlobalFileWriter()

    def __exit__(self, exc_type, exc_value, traceback):
        for file in GlobalFileWriter.instance()._files.values():
            file.close()


class Debugger:
    def __init__(self, debugger: lldb.SBDebugger):
        self._inner = debugger

    def create_target(self, exe) -> Target:
        return Target(self._inner.CreateTarget(exe))


class Target:
    def __init__(self, target: lldb.SBTarget):
        self._inner = target

    @property
    def modules(self) -> Iterable[lldb.SBModule]:
        return self._inner.module_iter()

    @property
    def compile_units(self) -> Iterable[lldb.SBCompileUnit]:
        x = []
        for module in self.modules:
            x.extend(module.compile_unit_iter())
        return x


class Breakpoint:
    def __init__(self, target: Target):
        self._target = target

        # Ideally should be one lldb breakpoint with a custom resolver:
        # https://lldb.llvm.org/use/python-reference.html#using-the-python-api-s-to-create-custom-breakpoints
        self._breakpoints = []

    @staticmethod
    def from_regex(target, regex_str) -> Breakpoint:
        print(f"Setting breakpoints at locations that match '{regex_str}'...")

        this = Breakpoint(target)
        regex_str = re.compile(regex_str)

        def set_in_file(path):
            with open(path, "r") as file:
                for line_number, line in enumerate(file, start=1):
                    if not regex_str.search(line):
                        continue

                    breakpoint = target._inner.BreakpointCreateByLocation(
                        path, line_number
                    )

                    if breakpoint.IsValid():
                        print(f"Breakpoint set at {path}:{line_number}")
                        this._breakpoints.append(breakpoint)
                    else:
                        print(f"Failed to set breakpoint at {path}:{line_number}")

        for comp_unit in target.compile_units:
            file_spec = comp_unit.GetFileSpec()
            source_file_path = file_spec.GetDirectory() + "/" + file_spec.GetFilename()

            if os.path.isfile(source_file_path):
                set_in_file(source_file_path)

        if len(this._breakpoints) == 0:
            print("No matches found.")

        return this

    def set_callback(self, cb):
        cb_str = f"{cb.__module__}.{cb.__name__}"
        for b in self._breakpoints:
            b.SetScriptCallbackFunction(cb_str)


def break_main(frame, bp_loc, extra_args, internal_dict):
    var = frame.FindVariable("its_an_arg")
    print(var)
    GlobalFileWriter.instance().write("output.log", "hello from lldb")

    # Returning False tells lldb not to stop at the breakpoint
    return False


def main(debugger):
    debugger.SetAsync(False)

    target = debugger.CreateTarget(EXE)

    # Set breakpoints
    target = Target(target)
    b = Breakpoint.from_regex(target, "@break-main")
    b.set_callback(break_main)

    # Launch
    with GlobalFileWriter():
        target.LaunchSimple(ARGS, None, ".")


def __lldb_init_module(debugger, _dict):
    main(debugger)
