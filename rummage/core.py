from __future__ import annotations

import inspect
import json
import logging
import os
import re
import types
from typing import Any, Iterable, List, Optional

import lldb

__all__ = [
    "BreakpointLocation",
    "LineLocation",
    "StackFrame",
    "Var",
    "VarInfo",
    "GlobalFileWriter",
    # TODO: Below are actually lib internals, could be moved somewhere else
    "Breakpoint",
    "Debugger",
    "Target",
    "LaunchConfig",
    "get_hook_fns",
]


class Type:
    class BasicType:
        def __init__(self, basic_type_enum: int) -> None:
            self._basic_type_enum = basic_type_enum

        def __str__(self) -> str:
            basic_type_enum = self._basic_type_enum
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
                return self._basic_type_enum == self._basic_type_enum
            if isinstance(value, int):
                return self._basic_type_enum == value
            return False

    class TypeClass:
        def __init__(self, type_class_enum: int) -> None:
            self._type_class_enum = type_class_enum

        def __str__(self) -> str:
            type_class_enum = self._type_class_enum
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
                return self._type_class_enum == self._type_class_enum
            if isinstance(value, int):
                return self._type_class_enum == value
            return False

    def __init__(self, sb_type: lldb.SBType) -> None:
        self._sb_type = sb_type

    @property
    def basic_type(self) -> Type.BasicType:
        return Type.BasicType(self._sb_type.GetBasicType())

    @property
    def type_class(self) -> Type.TypeClass:
        return Type.TypeClass(self._sb_type.GetTypeClass())

    @property
    def name(self) -> str:
        return self._sb_type.GetName()

    @property
    def is_pointer(self) -> bool:
        return self._sb_type.IsPointerType()

    @property
    def pointee_type(self) -> Optional[Type]:
        if not self.is_pointer:
            return None
        return Type(self._sb_type.GetPointeeType())

    @property
    def is_array(self) -> bool:
        return self._sb_type.IsArrayType()

    @property
    def is_integral_signed(self) -> bool:
        is_numeric, is_signed = lldb.is_numeric_type(self.basic_type._basic_type_enum)
        return is_numeric and is_signed and not self.is_floating_point

    @property
    def is_integral_unsigned(self) -> bool:
        is_numeric, is_signed = lldb.is_numeric_type(self.basic_type._basic_type_enum)
        return is_numeric and not is_signed and not self.is_floating_point

    @property
    def is_integral(self) -> bool:
        return self.is_integral_signed or self.is_integral_unsigned

    @property
    def is_floating_point(self) -> bool:
        return self.basic_type in [
            lldb.eBasicTypeHalf,
            lldb.eBasicTypeFloat,
            lldb.eBasicTypeDouble,
            lldb.eBasicTypeLongDouble,
        ]

    @property
    def is_boolean(self) -> bool:
        return self.basic_type == lldb.eBasicTypeBool

    @property
    def is_character(self) -> bool:
        # Not sure about the weird ones, but they DO have 'char' in their names
        return self.basic_type in [
            lldb.eBasicTypeChar,
            lldb.eBasicTypeSignedChar,
            lldb.eBasicTypeUnsignedChar,
            lldb.eBasicTypeWChar,
            lldb.eBasicTypeSignedWChar,
            lldb.eBasicTypeUnsignedWChar,
            lldb.eBasicTypeChar16,
            lldb.eBasicTypeChar32,
            lldb.eBasicTypeChar8,
        ]

    @property
    def is_numeric(self) -> bool:
        # Come on, bools in Python are quite numeric!
        return (
            lldb.is_numeric_type(self.basic_type._basic_type_enum)[0] or self.is_boolean
        )

    @property
    def info_str(self) -> str:
        return (
            f"Type {self.name}\n"
            f"  BasicType: {self.basic_type}\n"
            f"  TypeClass: {self.type_class}\n"
        )

    def __str__(self) -> str:
        return self.name


class Var:
    def __init__(self, sb_value: lldb.SBValue):
        # TODO: Careful, any member here might clash with underlying struct's members.
        self._sb_value = sb_value

        var_type = VarInfo(self).canonical_type
        if var_type.is_integral_signed:
            self._value = int(sb_value.GetValueAsSigned())
        elif var_type.is_integral_unsigned:
            self._value = int(sb_value.GetValueAsUnsigned())
        elif var_type.is_floating_point:
            self._value = float(sb_value.GetValue())
        elif var_type.is_boolean:
            self._value = bool(sb_value.GetValueAsUnsigned())
        elif var_type.is_pointer:
            self._value = int(sb_value.GetValueAsUnsigned())
        else:
            self._value = None

    def __getattr__(self, name) -> Any:
        # Search underlying variable for members with the given name
        child_sbvalue = self._sb_value.GetChildMemberWithName(name)
        if child_sbvalue and child_sbvalue.IsValid():
            return Var(child_sbvalue)

        # If member of underlying variable don't clash, emulate methods on the Var object
        if name == "deref":
            return types.MethodType(deref, self)
        if name == "is_null":
            return types.MethodType(is_null, self)
        if name == "as_array":
            return types.MethodType(as_array, self)

        raise AttributeError(f"Attribute '{name}' is not defined")

    def __getitem__(self, key):
        if type(key) not in [int, Var]:
            raise TypeError(
                f"Cannot index into an instance of {type(self)}"
                f"with an instance of {type(key)}"
            )

        if type(key) == Var and not VarInfo(key).canonical_type.is_integral:
            raise TypeError(
                f"Cannot index into an instance of {type(self)}"
                f"with a variable of type {VarInfo(key).canonical_type.name}"
            )

        child_sb_value = self._sb_value.GetValueForExpressionPath(f"[{key}]")
        if child_sb_value and child_sb_value.IsValid():
            return Var(child_sb_value)

        raise IndexError(f"Index {key} is out of range")

    def __iter__(self):
        for i in range(len(self)):
            yield Var(self._sb_value.GetChildAtIndex(i))

    def __len__(self):
        return self._sb_value.GetNumChildren()

    def __int__(self):
        return int(self._value)  # type: ignore - we should get a runtime error if this is not valid

    def __index__(self):
        return int(self._value)  # type: ignore - we should get a runtime error if this is not valid

    def __float__(self):
        return float(self._value)  # type: ignore - we should get a runtime error if this is not valid

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
        return -self._value  # type: ignore - we should get a runtime error if this is not valid

    def __abs__(self):
        return abs(self._value)  # type: ignore - we should get a runtime error if this is not valid

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
        var_info = VarInfo(self)
        if self._value is not None:
            type_ = var_info.canonical_type

            # Special char handling
            if type_.is_character:
                assert type(self._value) == int
                return chr(self._value)

            if type_.is_pointer:
                assert type_.pointee_type is not None

                # Special C string handling
                if type_.pointee_type.is_character:
                    max_chars = 20
                    string, i, c = "", 0, "\0"

                    for i in range(max_chars):
                        c = str(self[i])
                        if c == "\0":
                            break
                        string += c

                    # Print ellipsis if reached max_chars and still not at end of string
                    if i == max_chars - 1 and str(self[i + 1]) != "\0":
                        string += "..."
                    return string

                # Special pointer handling
                assert type(self._value) == int
                return hex(self._value)

            return str(self._value)

        return f"<({var_info.canonical_type}) {var_info.name}>"

    def __repr__(self):
        var_info = VarInfo(self)
        return (
            f'({var_info.canonical_type}) {var_info.name} {{ {self._value or "..."} }}'
        )


def deref(var: Var) -> Var:
    type_ = VarInfo(var).canonical_type
    if not type_.is_pointer:
        raise ValueError(f"Can't dereference a variable of type {type_.name}")

    return Var(var._sb_value.Dereference())


def is_null(var: Var) -> bool:
    type_ = VarInfo(var).canonical_type
    if not type_.is_pointer:
        raise ValueError(f"Variable of type {type_.name} can't be NULL")

    return var == 0


def as_array(var: Var, len: int) -> Var:
    type_ = var._sb_value.GetType()
    if not type_.IsPointerType():
        raise ValueError(
            f"Can't cast a variable of type {type_.GetName()} to an array."
        )

    return Var(
        # Not sure why the deref, but it fixes tests...
        var._sb_value.Dereference().Cast(type_.GetPointeeType().GetArrayType(len))
    )


class VarInfo:
    """
    Class for accessing info about a variable.

    Avoids adding attributes to the Var class which may clash with the members of the underlying
    variable.
    """

    def __init__(self, var: Var) -> None:
        self._sb_value = var._sb_value

    @property
    def canonical_type(self) -> Type:
        return Type(self._sb_value.GetType().GetCanonicalType())

    @property
    def name(self) -> str:
        return self._sb_value.GetName()

    def __str__(self) -> str:
        return f"<{self._sb_value}>"


class StackFrame:
    def __init__(self, frame: lldb.SBFrame) -> None:
        self._inner = frame

    def var(self, name) -> Var:
        var = self._inner.FindVariable(name)
        if not var.IsValid():
            raise KeyError(f"Variable '{name}' not found")
        return Var(var)

    @property
    def location(self):
        line_entry = self._inner.GetLineEntry()
        file_path = line_entry.GetFileSpec().GetFilename()
        line_number = line_entry.GetLine()
        return LineLocation(file_path, line_number)

    def eval(self, expr: str) -> lldb.SBValue:
        # TODO: if value.IsValid() and value.GetError().Success():
        return self._inner.EvaluateExpression(expr)


class BreakpointLocation:
    def __init__(self, bp_loc: lldb.SBBreakpointLocation) -> None:
        self._inner = bp_loc

    @property
    def line_location(self) -> LineLocation:
        address = self._inner.GetAddress()
        line_entry = address.GetLineEntry()
        file_spec = line_entry.GetFileSpec()

        file_path = file_spec.GetDirectory() + "/" + file_spec.GetFilename()
        line_number = line_entry.GetLine()
        return LineLocation(file_path, line_number)

    @property
    def hit_count(self) -> int:
        return self._inner.GetHitCount()

    def __str__(self) -> str:
        attrs = ["line_location", "hit_count"]
        return f"<BreakpointLocation ({', '.join(f'{attr}: {getattr(self, attr)}' for attr in attrs)})>"


class LineLocation:
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

    def write(self, path: str, text):
        file = self._files.get(path)
        if file is None:
            file = open(path, "w")
            self._files[path] = file

        assert not file.closed

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

    @property
    def exe(self) -> str:
        return self._inner.GetExecutable().fullpath

    @property
    def args(self) -> List[str]:
        launch_info = self._inner.GetLaunchInfo()
        return list(
            launch_info.GetArgumentAtIndex(i)
            for i in range(launch_info.GetNumArguments())
        )


class Breakpoint:
    def __init__(self, target: Target):
        self._target = target

        # Ideally should be one lldb breakpoint with a custom resolver:
        # https://lldb.llvm.org/use/python-reference.html#using-the-python-api-s-to-create-custom-breakpoints
        self._breakpoints = []

    @staticmethod
    def from_regex(target, regex_str) -> Breakpoint:
        logging.info(f"Setting breakpoints at locations that match '{regex_str}'...")

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
                        logging.info(f"Breakpoint set at {path}:{line_number}")
                        this._breakpoints.append(breakpoint)
                    else:
                        logging.warning(
                            f"Failed to set breakpoint at {path}:{line_number}"
                        )

        for comp_unit in target.compile_units:
            file_spec = comp_unit.GetFileSpec()
            source_file_path = file_spec.GetDirectory() + "/" + file_spec.GetFilename()

            if os.path.isfile(source_file_path):
                set_in_file(source_file_path)

        if len(this._breakpoints) == 0:
            logging.info("No matches found.")

        return this

    def set_callback_via_path(self, cb_name: str):
        logging.debug(f"Breakpoint: adding callback {cb_name}")
        for b in self._breakpoints:
            extra_args = lldb.SBStructuredData()
            extra_args.SetFromJSON(
                json.dumps(
                    {
                        "exe": self._target.exe,
                        "args": self._target.args,
                    }
                )
            )
            b.SetScriptCallbackFunction(cb_name, extra_args)


class LaunchConfig:
    def __init__(self) -> None:
        self.exe = None
        self.args = []


def get_hook_fns(module):
    """
    Retrieve all public function members and their names from a given module.

    Args:
        module: The module object from which to retrieve function members.

    Returns:
        A list of tuples, each containing the name of the function and
        the function object itself.
    """

    # Note for the future: here we collect names of all function members as they appear as keys in
    # the members dict of the module. It's important to distinguish between member names and the
    # __name__ attribute of the members. They are not necessarily equal, e.g. in the case of
    # hook wrappers that were bolted onto the module using setattr.
    return [
        (name, fn)
        for (name, fn) in inspect.getmembers(module, inspect.isfunction)
        if not name.startswith("_")
    ]
