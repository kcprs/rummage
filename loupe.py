from __future__ import annotations

import os
import re
from typing import Iterable, Optional

import lldb

"""
NOTES

Good references:

https://lldb.llvm.org/use/python-reference.html
https://github.com/llvm/llvm-project/tree/main/lldb/examples/python
https://gist.github.com/nkaretnikov/6ee00afabf73332c5a89eacb610369c2
"""


class Frame:
    def __init__(self, frame: lldb.SBFrame) -> None:
        self._inner = frame

    def var(self, name) -> lldb.SBValue:
        return self._inner.FindVariable(name)


class Location:
    def __init__(self, frame: lldb.SBFrame) -> None:
        line_entry = frame.GetLineEntry()
        self._file_path = line_entry.GetFileSpec().GetFilename()
        self._line_number = line_entry.GetLine()

    @property
    def file_path(self):
        return self._file_path

    @property
    def line_number(self):
        return self._line_number

    def __str__(self):
        return f"{self.file_path}:{self.line_number}"


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

    def write(self, path: str, text: str, loc: Optional[Location] = None):
        file = self._files.get(path)
        if file is None:
            file = open(path, "w")
            self._files[path] = file

        assert not file.closed

        if loc:
            text = f"{loc} {text}"

        file.write(f"{text}\n")

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
