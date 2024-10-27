import lldb

from loupe import Frame, GlobalFileWriter, VarInfo

EXE = "_build/test_exe"
ARGS = "arg1 arg2".split(" ")


def test_int(_frame: lldb.SBFrame, *_):
    print("testing int")
    frame = Frame(_frame)
    one = frame.var("one")
    assert one > 0
    assert one == 1
    assert one + 2 == 3

    return False


def test_float(_frame: lldb.SBFrame, *_):
    print("testing float")
    frame = Frame(_frame)
    half = frame.var("half")
    print(f"Type of half is {type(half)}")
    print(f"Half is {half}")
    assert half == 0.5
    assert half + half == 1
    assert half > 0
    return False


def test_bool(_frame: lldb.SBFrame, *_):
    print("testing bool")
    frame = Frame(_frame)
    truth = frame.var("truth")
    lie = frame.var("lie")
    assert truth == 1
    assert not lie == 1
    return False


def test_struct(_frame: lldb.SBFrame, *_):
    print("testing struct")
    frame = Frame(_frame)
    a_struct = frame.var("a_struct")
    assert hasattr(a_struct, "a")
    assert hasattr(a_struct, "b")
    assert len(a_struct) == 2
    field_names = ["a", "b"]
    for field, name in zip(a_struct, field_names):
        assert field == a_struct.__getattr__(name)
    print(f"Printing struct as Var: {a_struct}")
    print(f"Printing struct as VarInfo: {VarInfo(a_struct)}")
    return False


def test_array(_frame: lldb.SBFrame, *_):
    print("testing array")
    frame = Frame(_frame)
    array = frame.var("multiplicity")
    assert array[0] == 1
    assert array[8] == 9
    assert len(array) == 9
    for i, num in enumerate(array):
        assert num == array[i]
    return False


def test_pointer(_frame: lldb.SBFrame, *_):
    print("testing pointer")
    frame = Frame(_frame)
    there = frame.var("there")
    print(f"Pointer is {there}")
    pointee = there.deref()
    assert pointee == 5
    not_a_pointer = frame.var("not_a_pointer")
    member_or_pointee = not_a_pointer.deref
    print(VarInfo(member_or_pointee))
    ptr_array = frame.var("array")
    for i, num in enumerate(ptr_array):
        assert num == ptr_array[i]
    return False


def tests_done(*_):
    print("Tests passed")
    return False
