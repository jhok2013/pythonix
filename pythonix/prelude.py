"""Essential functions and types for using the pythonix modules

Imported types include

    - Res: A type used for Exception handling as values
    - Nil: An Exception used to indicate an unexpected None
    - fn: A two step curried function used to add type information to lambda functions
    - Piper: Monad class used to pipe values into functions repeatedly
    - P: Special object used to pipe values into functions with `|`

"""
import pythonix.res as res
import pythonix.trail as trail
import pythonix.op as op
import pythonix.jsn as jsn
import pythonix.curry as curry
import pythonix.collections as collections
import pythonix.grammar as grammar
import pythonix.prove as prove
from pythonix.grammar import P, Piper
from pythonix.fn import fn
from pythonix.res import Res, Nil
