"""Essential functions and types for using the pythonix modules

Classes:

    * Piper: Pipe wrapper do sequential calls with >>>, |, and >
    * P: Pipe operator object like `|>` in Julia and Gleam
    * Ok: Indicates a successful response
    * Err: Indicates an unsuccessful response
    * Nil: Exception class indicating an unexpected None

Funcs:

    * fn: Util for creating typed lambda functions
    * q: Alias for res.unwrap
    * qe: Alias for res.unwrap_err
    * ok: Util for creating typed Ok | Err objects as Ok
    * err: Util for creating typed Ok | Err objets as Err
    * unpack: Converts Ok | Err to an unpackable tuple

Types:

    * Res: Alias for Ok[T] | Err[E]
    * Opt: Alias for Ok[T] | Err[Nil]

Modules:

    * res: utils for handling Ok or Err results
    * trail: Log concatenation
    * op: Partial functions for data structures
    * curry: Automatic currying decorators
    * tup: Utils for handling tuples
    * dict_utils: Fills the gaps in the dict api
    * grammar: Decorators for pipeable functions
    * prove: Simple assertions
    * fn: Module for handling lambda functions

"""
import pythonix.res as res
import pythonix.trail as trail
import pythonix.op as op
import pythonix.jsn as jsn
import pythonix.req as req
import pythonix.curry as curry
import pythonix.tup as tup
import pythonix.dict_utils as dict_utils
import pythonix.grammar as grammar
import pythonix.prove as prove
import pythonix.deq as deq
import pythonix.either as either
import pythonix.shortcuts as shortcuts
from pythonix.grammar import P, Piper
from pythonix.fn import fn
from pythonix.res import Ok, Err, Nil, Res, Opt
from pythonix.shortcuts import unwrap, unpack, q, u
