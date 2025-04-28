from rummage.core import BreakpointLocation, StackFrame


def on_hook_enter(frame: StackFrame, bp_loc: BreakpointLocation, extra):
    _ = frame, bp_loc, extra


# TODO: type hints
def on_target_launch(debugger):
    _ = debugger
