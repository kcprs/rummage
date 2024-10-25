from loupe import GlobalFileWriter, Location


def break_main(frame, bp_loc, extra_args, internal_dict):
    var = frame.FindVariable("some_value")
    assert var.IsValid()

    GlobalFileWriter.instance().write("output.log", var, loc=Location(frame))

    return False # Returning False tells lldb not to stop at the breakpoint


def index_int_array(frame, bp_loc, extra_args, internal_dict):
    array = frame.FindVariable("array")
    el_3 = array.GetChildAtIndex(3)
    assert el_3.IsValid()

    GlobalFileWriter.instance().write("output.log", el_3, loc=Location(frame))

    return False


def struct_children(frame, bp_loc, extra_args, internal_dict):
    struct = frame.FindVariable("some_struct")
    child = struct.GetChildMemberWithName("avg_blorp")
    assert child.IsValid()

    GlobalFileWriter.instance().write("output.log", struct, loc=Location(frame))
    GlobalFileWriter.instance().write("output.log", child, loc=Location(frame))

    return False
