'''
Log module that allows the user to wrap objects with a trail of log objects
and run functions that automatically accumulate logs.
'''
from pythonix.internals.trail import (
    new,
    logs,
    info,
    debug,
    warning,
    error,
    critical,
    Trail,
    trail,
)
from pythonix.internals.pipe import Blaze
