from rummage.core import StackFrame, BreakpointLocation


def on_hook_enter(frame: StackFrame, bp_loc: BreakpointLocation, extra_dict):
    _ = frame, bp_loc, extra_dict
