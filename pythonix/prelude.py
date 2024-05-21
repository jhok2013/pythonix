"""
TODO
====

* deprecate pipe
* update trail docs
* update tup docs
* update op docs
* update prove docs
* add req as an optional feature with dependencies
* test req
* add __init__ docs
* update prelude docs
* udpate readme
* test type hints
* run integration tests
"""
import pythonix.pipe as pipe
import pythonix.res as res
import pythonix.trail as trail
import pythonix.op as op
import pythonix.req as req
import pythonix.curry as curry
import pythonix.tup as tup
import pythonix.dict_utils as dict_utils
import pythonix.grammar as grammar
import pythonix.prove as prove
import pythonix.deq as deq
from pythonix.grammar import P, Piper
from pythonix.fn import fn

from pythonix.res import Ok, Err, Nil, q, Res, qe, ok, err, Opt
from pythonix.pipe import Bind, Do
from pythonix.pipe import Bind as B, Do as D
