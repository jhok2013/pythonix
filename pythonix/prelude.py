'''
## Submodules
A mass import of all the pythonix submodules including
- `pipe`: Wrapper types for piping and transforming sequentially
- `res`: Wrapper types and functions for handling errors
- `trail`: Wrapper types for managing and concatenating logs to objects
- `op`: Functions for mapping over and transforming data structures and objects safely
- `req`: Functions and wrapper types for creating, sending, and handling HTTP requests
- `curry`: Decorator functions for automatic currying of function definitions
- `tup`: Utility functions for operating over homogenous sequences
- `dict_utils`: Utility functions that shore up the default `dict` object
- `grammar`: Decorator functions for turning functions into pipeable wrapper types
- `prove`: Basic assertion functions that are easily used in `Do`

## Included Types
Includes the following result types by default
- `Ok`: Represents an expected outcome. Use this for pattern matching, otherwise use the `res.ok`
- `Err`: Represents an unexpected outcome. Use this for pattern matching, otherwise use the `res.err`
- `Nil`: Error type for unexpectedly `None` values.
- `Res`: Type alias for `Ok[T]` or `Err[E]`

And the following Pipe types
- `Bind` or `B`: Pipeable wrapper type for applying a series of functions on a value sequentially, changing its value.
- `Do` or `D`: Pipeable wrapper type for applying a series of functions on a value WITHOUT changing its value
- `Pipe` or `P`: Infix wrapper for applying values on its right to the value on its right. Simulates a proper pipe operator

## Included Functions
And the following utility functions
- `q`: Unwraps the value of an `Ok` or panics if `Err`. Shorthand for `res.unwrap`
- `qe`: Unwraps the err value of an `Err` or panics if `Ok`. Shorthand for `res.unwrap_err`
'''
import pythonix.pipe as pipe
import pythonix.res as res
import pythonix.trail as trail
import pythonix.op as op
from pythonix.internals.types import Fn, FnOnce
import pythonix.req as req
import pythonix.curry as curry
import pythonix.tup as tup
import pythonix.dict_utils as dict_utils
import pythonix.grammar as grammar
import pythonix.prove as prove
from pythonix.grammar import Pipe
from pythonix.grammar import Pipe as P

from pythonix.res import Ok, Err, Nil, q, Res, qe
from pythonix.pipe import Bind, Do
from pythonix.pipe import Bind as B, Do as D
