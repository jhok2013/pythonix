"""Wrap operations and values with logs that can be used at runtime."""
from pythonix.internals.trail.trail import (
    Trail,
    Log,
    Info,
    Critical,
    Warning,
    Debug,
    Error,
)
from pythonix.internals.trail.decorators import start, then_log, then_log_top
