from rummage.core import StackFrame, BreakpointLocation


def on_hook_enter(frame: StackFrame, bp_loc: BreakpointLocation, extra):
    _ = frame, bp_loc, extra
