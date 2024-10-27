import lldb

from loupe import Frame, GlobalFileWriter, create_struct_class_from_sbvalue

EXE = "_build/test_exe"
ARGS = "arg1 arg2".split(" ")


# def break_main(frame: Frame):
#     name = "im_a_float"
#     var = frame.var(name)
#     value = var.GetValue()
#     print(f"Value of {name} is {value}")
#     var_type = var.GetType()
#     typeclass = var_type.GetTypeClass()
#     print(f"Var {name} has type {var_type} and type class {typeclass}")
#     print(f"For reference lldb.eTypeClassBuiltin has number {lldb.eTypeClassBuiltin}")
#     print(f"For reference lldb.eTypeClassTypedef has number {lldb.eTypeClassTypedef}")
#     GlobalFileWriter.instance().write("output.log", var, loc=frame.location)


# def index_int_array(frame: Frame):
#     array = frame.var("array")
#     el_3 = array.GetChildAtIndex(3)
#     assert el_3.IsValid()
#
#     GlobalFileWriter.instance().write("output.log", el_3, loc=frame.location)


# def struct_children(frame: Frame):
#     name = "some_struct"
#     var = frame.var(name)
#     var_type = var.GetType()
#     typeclass = var_type.GetTypeClass()
#     print(f"Var {name} has type {var_type} and type class {typeclass}")
#     print(f"For reference lldb.eTypeClassBuiltin has number {lldb.eTypeClassBuiltin}")
#     print(f"For reference lldb.eTypeClassTypedef has number {lldb.eTypeClassTypedef}")
#     print(f"For reference ldb.eTypeClassStruct has number {lldb.eTypeClassStruct}")
#
#     child = var.GetChildMemberWithName("avg_blorp")
#     assert child.IsValid()
#
#     GlobalFileWriter.instance().write("output.log", var, loc=frame.location)
#     GlobalFileWriter.instance().write("output.log", child, loc=frame.location)


# def deref_pointer(frame: Frame):
#     pointer = frame.var("point")
#     value = pointer.Dereference()
#
#     GlobalFileWriter.instance().write("output.log", pointer, loc=frame.location)
#     GlobalFileWriter.instance().write("output.log", value, loc=frame.location)


def test_int(_frame: lldb.SBFrame, *_):
    print("testing int")
    frame = Frame(_frame)
    one = frame.var("one")
    assert one == 1
    return False


def test_float(_frame: lldb.SBFrame, *_):
    print("testing float")
    frame = Frame(_frame)
    half = frame.var("half")
    assert half == 0.5
    return False


def test_struct(_frame: lldb.SBFrame, *_):
    print("testing struct")
    frame = Frame(_frame)
    _a_struct = frame.var("a_struct")
    a_struct = create_struct_class_from_sbvalue(_a_struct)  # type: ignore
    assert hasattr(a_struct, "a")
    assert hasattr(a_struct, "b")
    print("Successully tested struct")
