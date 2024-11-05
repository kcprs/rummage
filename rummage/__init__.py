try:
    from .core import *
except ImportError:
    # .core internally imports the lldb module, which is only defined when running within lldb.
    # We still need rummmage to be "importable" without an error outside of lldb so that the main
    # function can find out where the module is installed. No actual functionality required, so
    # it's OK to return an empty module.
    pass
