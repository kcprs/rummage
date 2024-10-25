from loupe import GlobalFileWriter, Location


def break_main(frame, bp_loc, extra_args, internal_dict):
    var = frame.FindVariable("some_value")
    GlobalFileWriter.instance().write("output.log", var, loc=Location(frame))

    # Returning False tells lldb not to stop at the breakpoint
    return False


def index_int_array(frame, bp_loc, extra_args, internal_dict):
    array = frame.FindVariable("array")
    el_3 = array.GetChildAtIndex(3)

    GlobalFileWriter.instance().write("output.log", el_3, loc=Location(frame))
