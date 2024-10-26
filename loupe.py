from __future__ import annotations

import os
import re
from typing import Iterable, Optional, Union

import lldb

"""
NOTES

Good references:

https://lldb.llvm.org/use/python-reference.html
https://github.com/llvm/llvm-project/tree/main/lldb/examples/python
https://gist.github.com/nkaretnikov/6ee00afabf73332c5a89eacb610369c2
"""


class StructVar: ...


class NumericVar:
    def __init__(self, sb_value: lldb.SBValue):
        self._sb_value = sb_value
        self._value = self._extract_value(sb_value)

    def _extract_value(self, sb_value):
        value_type = sb_value.GetType()

        if value_type.IsPointerType() or value_type.IsArrayType():
            raise TypeError(
                "Pointer or array types are not supported in this wrapper class."
            )

        basic_type = value_type.GetBasicType()
        if (
            basic_type == lldb.eBasicTypeInt
            or basic_type == lldb.eBasicTypeLong
            or basic_type == lldb.eBasicTypeChar
            or basic_type == lldb.eBasicTypeShort
        ):
            return sb_value.GetValueAsSigned()
        elif (
            basic_type == lldb.eBasicTypeUnsignedInt
            or basic_type == lldb.eBasicTypeUnsignedLong
            or basic_type == lldb.eBasicTypeUnsignedChar
            or basic_type == lldb.eBasicTypeUnsignedShort
        ):
            return sb_value.GetValueAsUnsigned()
        elif basic_type == lldb.eBasicTypeFloat or basic_type == lldb.eBasicTypeDouble:
            return float(sb_value.GetValue())
        else:
            raise TypeError("Unsupported SBValue type for numeric operations.")

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return float(self._value)

    def __add__(self, other):
        return self._value + other

    def __radd__(self, other):
        return other + self._value

    def __sub__(self, other):
        return self._value - other

    def __rsub__(self, other):
        return other - self._value

    def __mul__(self, other):
        return self._value * other

    def __rmul__(self, other):
        return other * self._value

    def __truediv__(self, other):
        return self._value / other

    def __rtruediv__(self, other):
        return other / self._value

    def __floordiv__(self, other):
        return self._value // other

    def __rfloordiv__(self, other):
        return other // self._value

    def __mod__(self, other):
        return self._value % other

    def __rmod__(self, other):
        return other % self._value

    def __pow__(self, other):
        return self._value**other

    def __rpow__(self, other):
        return other**self._value

    def __neg__(self):
        return -self._value

    def __abs__(self):
        return abs(self._value)

    def __eq__(self, other):
        return self._value == other

    def __ne__(self, other):
        return self._value != other

    def __lt__(self, other):
        return self._value < other

    def __le__(self, other):
        return self._value <= other

    def __gt__(self, other):
        return self._value > other

    def __ge__(self, other):
        return self._value >= other

    def __str__(self) -> str:
        return str(self._sb_value)

    def __repr__(self):
        return f"NumericVar({self._value})"


class VarMetadata:
    def __init__(self, var: NumericVar) -> None:
        self._sb_value = var._sb_value
        # TODO: This should be an interface for var metadata, e.g. name etc.


class Frame:
    def __init__(self, frame: lldb.SBFrame) -> None:
        self._inner = frame

    def var(self, name) -> Union[lldb.SBValue, NumericVar]:
        var = self._inner.FindVariable(name)
        assert var.IsValid(), f"Variable '{name}' not found"

        try:
            var = NumericVar(var)
        except TypeError:
            pass

        return var

    @property
    def location(self):
        line_entry = self._inner.GetLineEntry()
        file_path = line_entry.GetFileSpec().GetFilename()
        line_number = line_entry.GetLine()
        return Location(file_path, line_number)


class Location:
    def __init__(self, file_path, line_number) -> None:
        self._file_path = file_path
        self._line_number = line_number

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

    def write(self, path: str, text, loc: Optional[Location] = None):
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

    def set_callback_via_path(self, cb_name: str):
        print(f"Breakpoint: adding callback {cb_name}")
        for b in self._breakpoints:
            b.SetScriptCallbackFunction(cb_name)
