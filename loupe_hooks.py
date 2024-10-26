from loupe import Frame, GlobalFileWriter, Location

EXE = "_build/test_exe"
ARGS = "arg1 arg2".split(" ")


def break_main(frame: Frame):
    frame_ = frame._inner
    var = frame_.FindVariable("some_value")
    assert var.IsValid()

    GlobalFileWriter.instance().write("output.log", var, loc=Location(frame_))


def index_int_array(frame: Frame):
    frame_ = frame._inner
    array = frame_.FindVariable("array")
    el_3 = array.GetChildAtIndex(3)
    assert el_3.IsValid()

    GlobalFileWriter.instance().write("output.log", el_3, loc=Location(frame_))


def struct_children(frame: Frame):
    frame_ = frame._inner
    struct = frame_.FindVariable("some_struct")
    child = struct.GetChildMemberWithName("avg_blorp")
    assert child.IsValid()

    GlobalFileWriter.instance().write("output.log", struct, loc=Location(frame_))
    GlobalFileWriter.instance().write("output.log", child, loc=Location(frame_))


def deref_pointer(frame: Frame):
    frame_ = frame._inner
    pointer = frame_.FindVariable("point")
    value = pointer.Dereference()

    GlobalFileWriter.instance().write("output.log", pointer, loc=Location(frame_))
    GlobalFileWriter.instance().write("output.log", value, loc=Location(frame_))
