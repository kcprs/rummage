try:
    from .core import *
    from . import callbacks
except ImportError:
    # .core internally imports the lldb module, which is only defined when running within lldb.
    # We still need rummmage to be "importable" outside of lldb so that the main function can be
    # run.
    pass

