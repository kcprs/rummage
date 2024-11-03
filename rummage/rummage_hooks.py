# TODO: This should move to /tests

import logging

from rummage import GlobalFileWriter, StackFrame, VarInfo

EXE = "_build/test_exe"
ARGS = "arg1 arg2".split(" ")


def test_int(frame: StackFrame):
    logging.debug("testing int")
    one = frame.var("one")
    assert one > 0
    assert one == 1
    assert one + 2 == 3
    assert str(VarInfo(one)) == "<(int) one = 1>"


def test_float(frame: StackFrame):
    logging.debug("testing float")
    half = frame.var("half")
    assert half == 0.5
    assert half + half == 1
    assert half > 0
    assert str(half) == str(0.5)


def test_bool(frame: StackFrame):
    logging.debug("testing bool")
    truth = frame.var("truth")
    lie = frame.var("lie")
    assert truth == 1
    assert not lie == 1
    assert str(truth) == str(True)
    assert str(lie) == str(False)


def test_struct(frame: StackFrame):
    logging.debug("testing struct")
    a_struct = frame.var("a_struct")
    assert hasattr(a_struct, "a")
    assert hasattr(a_struct, "b")
    assert len(a_struct) == 2
    field_names = ["a", "b"]
    for field, name in zip(a_struct, field_names):
        assert field == a_struct.__getattr__(name)
    assert str(a_struct) == "<(TestStruct) a_struct>"
    assert str(VarInfo(a_struct)) == "<(TestStruct) a_struct = (a = 1, b = 3.5)>"


def test_array(frame: StackFrame):
    logging.debug("testing array")
    array = frame.var("multiplicity")
    assert array[0] == 1
    assert array[8] == 9
    assert len(array) == 9
    for i, num in enumerate(array):
        assert num == array[i]


def test_pointer(frame: StackFrame):
    logging.debug("testing pointer")
    there = frame.var("there")
    pointee = there.deref()
    assert pointee == 5
    not_a_pointer = frame.var("not_a_pointer")
    member_not_pointee = not_a_pointer.deref
    assert member_not_pointee == 15
    ptr_array = frame.var("array")
    for i, num in enumerate(ptr_array):
        assert num == ptr_array[i]
    assert len(ptr_array) == 1
    string = frame.var("text")
    assert str(string) == "Lorem Ipsum"
    assert str(frame.var("c")) == "c"
    assert str(frame.var("long_text")) == "Lorem ipsum dolor si..."


def tests_done(*_):
    logging.debug("Tests passed")
