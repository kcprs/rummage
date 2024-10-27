from __future__ import annotations

import os
import re
import types
from typing import Iterable, Optional, Union

import lldb

"""
NOTES

Good references:

https://lldb.llvm.org/use/python-reference.html
https://github.com/llvm/llvm-project/tree/main/lldb/examples/python
https://gist.github.com/nkaretnikov/6ee00afabf73332c5a89eacb610369c2
"""

class Type:
    class BasicType:
        def __init__(self, basic_type_enum: int) -> None:
            self.basic_type_enum = basic_type_enum

        def __str__(self) -> str:
            basic_type_enum = self.basic_type_enum
            if basic_type_enum == lldb.eBasicTypeInvalid:
                return "lldb.eBasicTypeInvalid"
            if basic_type_enum == lldb.eBasicTypeVoid:
                return "lldb.eBasicTypeVoid"
            if basic_type_enum == lldb.eBasicTypeChar:
                return "lldb.eBasicTypeChar"
            if basic_type_enum == lldb.eBasicTypeSignedChar:
                return "lldb.eBasicTypeSignedChar"
            if basic_type_enum == lldb.eBasicTypeUnsignedChar:
                return "lldb.eBasicTypeUnsignedChar"
            if basic_type_enum == lldb.eBasicTypeWChar:
                return "lldb.eBasicTypeWChar"
            if basic_type_enum == lldb.eBasicTypeSignedWChar:
                return "lldb.eBasicTypeSignedWChar"
            if basic_type_enum == lldb.eBasicTypeUnsignedWChar:
                return "lldb.eBasicTypeUnsignedWChar"
            if basic_type_enum == lldb.eBasicTypeChar16:
                return "lldb.eBasicTypeChar16"
            if basic_type_enum == lldb.eBasicTypeChar32:
                return "lldb.eBasicTypeChar32"
            if basic_type_enum == lldb.eBasicTypeChar8:
                return "lldb.eBasicTypeChar8"
            if basic_type_enum == lldb.eBasicTypeShort:
                return "lldb.eBasicTypeShort"
            if basic_type_enum == lldb.eBasicTypeUnsignedShort:
                return "lldb.eBasicTypeUnsignedShort"
            if basic_type_enum == lldb.eBasicTypeInt:
                return "lldb.eBasicTypeInt"
            if basic_type_enum == lldb.eBasicTypeUnsignedInt:
                return "lldb.eBasicTypeUnsignedInt"
            if basic_type_enum == lldb.eBasicTypeLong:
                return "lldb.eBasicTypeLong"
            if basic_type_enum == lldb.eBasicTypeUnsignedLong:
                return "lldb.eBasicTypeUnsignedLong"
            if basic_type_enum == lldb.eBasicTypeLongLong:
                return "lldb.eBasicTypeLongLong"
            if basic_type_enum == lldb.eBasicTypeUnsignedLongLong:
                return "lldb.eBasicTypeUnsignedLongLong"
            if basic_type_enum == lldb.eBasicTypeInt128:
                return "lldb.eBasicTypeInt128"
            if basic_type_enum == lldb.eBasicTypeUnsignedInt128:
                return "lldb.eBasicTypeUnsignedInt128"
            if basic_type_enum == lldb.eBasicTypeBool:
                return "lldb.eBasicTypeBool"
            if basic_type_enum == lldb.eBasicTypeHalf:
                return "lldb.eBasicTypeHalf"
            if basic_type_enum == lldb.eBasicTypeFloat:
                return "lldb.eBasicTypeFloat"
            if basic_type_enum == lldb.eBasicTypeDouble:
                return "lldb.eBasicTypeDouble"
            if basic_type_enum == lldb.eBasicTypeLongDouble:
                return "lldb.eBasicTypeLongDouble"
            if basic_type_enum == lldb.eBasicTypeFloatComplex:
                return "lldb.eBasicTypeFloatComplex"
            if basic_type_enum == lldb.eBasicTypeDoubleComplex:
                return "lldb.eBasicTypeDoubleComplex"
            if basic_type_enum == lldb.eBasicTypeLongDoubleComplex:
                return "lldb.eBasicTypeLongDoubleComplex"
            if basic_type_enum == lldb.eBasicTypeObjCID:
                return "lldb.eBasicTypeObjCID"
            if basic_type_enum == lldb.eBasicTypeObjCClass:
                return "lldb.eBasicTypeObjCClass"
            if basic_type_enum == lldb.eBasicTypeObjCSel:
                return "lldb.eBasicTypeObjCSel"
            if basic_type_enum == lldb.eBasicTypeNullPtr:
                return "lldb.eBasicTypeNullPtr"
            if basic_type_enum == lldb.eBasicTypeOther:
                return "lldb.eBasicTypeOther"
            return "unknown"

        def __eq__(self, value: object, /) -> bool:
            if isinstance(value, Type.BasicType):
                return self.basic_type_enum == self.basic_type_enum
            if isinstance(value, int):
                return self.basic_type_enum == value
            return False
            

    class TypeClass:
        def __init__(self, type_class_enum: int) -> None:
            self.type_class_enum = type_class_enum

        def __str__(self) -> str:
            type_class_enum = self.type_class_enum
            if type_class_enum == lldb.eTypeClassInvalid:
                return "lldb.eTypeClassInvalid"
            if type_class_enum == lldb.eTypeClassArray:
                return "lldb.eTypeClassArray"
            if type_class_enum == lldb.eTypeClassBlockPointer:
                return "lldb.eTypeClassBlockPointer"
            if type_class_enum == lldb.eTypeClassBuiltin:
                return "lldb.eTypeClassBuiltin"
            if type_class_enum == lldb.eTypeClassClass:
                return "lldb.eTypeClassClass"
            # if type_class == lldb.eTypeClassFloat: # Somehow not in the lldb module
            #     return "lldb.eTypeClassFloat"
            if type_class_enum == lldb.eTypeClassComplexInteger:
                return "lldb.eTypeClassComplexInteger"
            if type_class_enum == lldb.eTypeClassComplexFloat:
                return "lldb.eTypeClassComplexFloat"
            if type_class_enum == lldb.eTypeClassFunction:
                return "lldb.eTypeClassFunction"
            if type_class_enum == lldb.eTypeClassMemberPointer:
                return "lldb.eTypeClassMemberPointer"
            if type_class_enum == lldb.eTypeClassObjCObject:
                return "lldb.eTypeClassObjCObject"
            if type_class_enum == lldb.eTypeClassObjCInterface:
                return "lldb.eTypeClassObjCInterface"
            if type_class_enum == lldb.eTypeClassObjCObjectPointer:
                return "lldb.eTypeClassObjCObjectPointer"
            if type_class_enum == lldb.eTypeClassPointer:
                return "lldb.eTypeClassPointer"
            if type_class_enum == lldb.eTypeClassReference:
                return "lldb.eTypeClassReference"
            if type_class_enum == lldb.eTypeClassStruct:
                return "lldb.eTypeClassStruct"
            if type_class_enum == lldb.eTypeClassTypedef:
                return "lldb.eTypeClassTypedef"
            if type_class_enum == lldb.eTypeClassUnion:
                return "lldb.eTypeClassUnion"
            if type_class_enum == lldb.eTypeClassVector:
                return "lldb.eTypeClassVector"
            if type_class_enum == lldb.eTypeClassOther:
                return "lldb.eTypeClassOther"
            if type_class_enum == lldb.eTypeClassAny:
                return "lldb.eTypeClassAny"
            return "unknown"

        def __eq__(self, value: object, /) -> bool:
            if isinstance(value, Type.TypeClass):
                return self.type_class_enum == self.type_class_enum
            if isinstance(value, int):
                return self.type_class_enum == value
            return False
            

    def __init__(self, sb_type: lldb.SBType) -> None:
        self.sb_type = sb_type

    @property
    def basic_type(self) -> Type.BasicType:
        return Type.BasicType(self.sb_type.GetBasicType())

    @property
    def type_class(self) -> Type.TypeClass:
        return Type.TypeClass(self.sb_type.GetTypeClass())

    @property
    def name(self) -> str:
        return self.sb_type.GetName()

    @property
    def info_str(self) -> str:
        return (
            f"Type {self.name}\n"
            f"  BasicType: {self.basic_type}\n"
            f"  TypeClass: {self.type_class}\n"
        )

    def __str__(self) -> str:
        return self.name

def create_struct_class_from_sbvalue(sb_value: lldb.SBValue):
    print(Type(sb_value.GetType()).info_str)

    # Ensure the sb_value is a struct
    if sb_value.GetType().GetTypeClass() != lldb.eTypeClassStruct:
        raise ValueError("SBValue is not a struct")

    # Initialize the dynamic class with struct fields
    def populate_attrs(class_namespace):
        for i in range(sb_value.GetNumChildren()):
            child = sb_value.GetChildAtIndex(i)
            field_name = child.GetName()
            field_value = child.GetValue()
            class_namespace[field_name] = field_value

    # Create a dynamic class
    # TODO: avoid defining a class multiple times for one struct
    class_name = sb_value.GetType().GetName()
    struct_class = types.new_class(class_name, exec_body=populate_attrs)

    # Create an instance of the dynamic class
    instance = struct_class()
    return instance


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
