import logging

from rummage import StackFrame, VarInfo, BreakpointLocation
import rummage


def _on_hook_enter(bp_loc: BreakpointLocation, **_):
    logging.debug(f"_on_hook_enter called at {bp_loc}")


rummage.callbacks.on_hook_enter = _on_hook_enter


def test_int(frame: StackFrame, **_):
    logging.debug("testing int")
    one = frame.var("one")
    assert one > 0
    assert one == 1
    assert one + 2 == 3
    assert str(VarInfo(one)) == "<(int) one = 1>"


def test_float(frame: StackFrame, **_):
    logging.debug("testing float")
    half = frame.var("half")
    assert half == 0.5
    assert half + half == 1
    assert half > 0
    assert str(half) == str(0.5)


def test_bool(frame: StackFrame, **_):
    logging.debug("testing bool")
    truth = frame.var("truth")
    lie = frame.var("lie")
    assert truth == 1
    assert not lie == 1
    assert str(truth) == str(True)
    assert str(lie) == str(False)


def test_struct(frame: StackFrame, **_):
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


def test_array(frame: StackFrame, **_):
    logging.debug("testing array")
    array = frame.var("multiplicity")
    assert array[0] == 1
    assert array[8] == 9
    assert len(array) == 9
    for i, num in enumerate(array):
        assert num == array[i]


def test_pointer(frame: StackFrame, **_):
    logging.debug("testing pointer")
    there = frame.var("there")
    pointee = there.deref()
    assert pointee == 5
    not_a_pointer = frame.var("not_a_pointer")
    member_not_pointee = not_a_pointer.deref
    assert member_not_pointee == 15

    ptr_array = frame.var("array")
    num_checked = 0
    for i, num in enumerate(ptr_array):
        assert num == ptr_array[i]
        assert num == i + 1
        num_checked += 1
    assert len(ptr_array) == 1
    assert num_checked == 1

    as_array = ptr_array.as_array(10)
    num_checked = 0
    for i, num in enumerate(as_array):
        assert num == as_array[i]
        assert num == i + 1
        num_checked += 1
    assert len(as_array) == 10
    assert num_checked == 10

    string = frame.var("text")
    assert str(string) == "Lorem Ipsum"
    assert str(frame.var("c")) == "c"
    assert str(frame.var("long_text")) == "Lorem ipsum dolor si..."
    billion_dollar_mistake = frame.var("billion_dollar_mistake")
    assert billion_dollar_mistake.is_null()


def tests_done(**_):
    logging.debug("Tests passed")
