"""Streamline your code with functional syntactic sugar and types with Pythonix.

Pythonix aims to be one of the most straight-forward and clean functional libs
for Python3. It brings some of the syntactic sugar, error handling, and patterns
of Rust, Go, and Gleam to make writing clean, declarative code a breeze.

Examples:

    Take code like this ::

        >>> def add(x, y):
        ...     return x + y
        ...
        >>> total = add(10, 10)
        >>> total = add(total, 30)
        >>> final = add(total, 50)
        >>> final
        100
    
    The func above works, but it could kill the program unexpectedly if bad types
    are put in. You as the developer, don't have an easy way of knowing or handling
    that eror cleanly.

    With Pythonix, you can make it obvious if something can fail, be None, and
    do sequential operations cleanly. ::

        >>> from pythonix.prelude import *  # Easy imports of essentials
        >>> @curry.two                      # Automatic currying
        ... @res.safe(TypeError)            # Automatic type safety
        ... def add(x: int, y: int) -> int:
        ...     return x + y
        ...
        >>> (
        ...     Piper(10)                   # Enter pipeable context
        ...     >> add(10)                  # Use curried functions
        ...     >> res.map(add(30))         # Perform sequential operations
        ...     >> res.map(add(50))
        ...     >  res.unwrap               # Intentionally panic if desired
        >>> )
        100


"""
