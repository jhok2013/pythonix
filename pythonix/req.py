"""
Module used to send HTTP requests and parse its results.
Here are some basic examples:

First, make a request of a typical method type and send it
```python
request = (
    req.get('https://www.hello.com')
    () # Add header pairs here
    () # Add param pairs here
)
response = request.send(request)
```

Or, make it with the Bind operator
```python
from pythonix.pipe import Bind
response = (
    Bind(req.get('https://www.hello.com')()())
    (req.send)
)
```
"""
from pythonix.internals.req import (
    body,
    get,
    delete,
    post,
    put,
    set_data,
    set_headers,
    set_params,
    set_url,
    send,
    Response
)
