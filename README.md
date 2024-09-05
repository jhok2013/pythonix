# PYTHONIX V2

Pythonix is meant to imitate some of my favorite features from Rust and Gleam like Errors as values, pipes, and immutable types.
It also features log concatentaion classes, enhanced dictionary and deque utilities and wrappers.

## Exceptions as Values

With Pythonix you can take code like this:

```python
# Make request
def get_data(url: str) -> dict:
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

try:
    url = MY_ENDPOINT
    data = get_data(url)
except (HTTPError, TimeoutError) as e:
    ... # Handle errors, log, etc
```

And capture errors instead like this

```python
@safe(HTTPError, TimeoutError)
def get_data(url: str) -> dict:
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

url = MY_ENDPOINT
data_result: Res[dict, HTTPError | TimeoutError] = get_data(url)
```

You can handle captured errors with the methods on the `Res` class, using pattern matching, unpacking, or simple if then statements.

```python
data = data_result.unwrap()
```

Unwrapping a result will cause a panic if it failed. You can use other methods to transform or handle the potential failure.

```python
data = data_result.unwrap_or('default_id') # Use a default
data = data_result.expect("Nice error message") # Use a nicer error message
```

You could also use pattern matching to get the wrapped value or Exception

```python
match data_result:
    case Res(dict(data)):
        id_value = data.get('id')
    case Res(err):
        print(err) # Handle the error case here
```

Or you could use unpacking to handle the failure like in Go

```python
data, err = data_result.unpack()
if err is not None:
    print(err) # Handle the error case here
```

Or just by using the `is_err` or `is_ok` properties to check the state of the result

```python
if data.is_err:
    err = data_result.unwrap_err()
    print(err) # Handle the error here
data = data.unwrap()
```

Finally, you can handle it by not handling it. Just use the methods on the `Res` class to transform or use your value.
The pipeline below prints the Exception, gets an element from the wrapped value, checks for if its None, sends it off using
a function that also returns a `Res`, logs those Errors if any, and then unwraps.

```python
@safe(HTTPError, TimeoutError)
def send_id(id: str) -> Response:
    response = put(ENDPOINT, data={"id": id})
    response.raise_for_status()
    return response

(
    data_result
    .do_err(log_errors)
    .map(lambda data: data.get('id'))
    .some()
    .do_err(log_errors)
    .and_then(send_id)
    .do_err(log_errors)
    .unwrap()
)
```

The code provides the better safety and is more concise than the code beneath:

```python
if data_result.is_err:
    err = data_result.unwrap_err()
    print(err)
    raise err

data: dict[str, str] = data_result.unwrap()
id_value: str | None = data.get('id')
if id_value is None:
    raise ValueError("No id found")

try:
    response = put(ENDPOINT, data={"id": id})
    response.raise_for_status()
except (HTTPError, TimeoutError) as e:
    print(e)
    raise e

```

Any of the described methods works well. But why do this in the first place?

1. Better transparency: You can easily tell what can fail and why
2. Forces you to handle errors: If your only way of handling errors is to let them crash your code then your code isn't very robust

## Pipes and Grammar

Another fun feature is being able to pass values using pipes rather than nesting functions. You can take code like this:

```python
encoded = str(dict(filter(lambda kv: kv[0] == "foo", map(lambda kv: (kv[0], kv[1] + 1), tuple(("foo", 0), ("bar", 1)))))
```

And replace it with something like this using Piper:

```python
encoded = (
    Piper(tuple(("foo", 0), ("bar", 1)))
    >> op.map_over(lambda kv: (kv[0], kv[1] + 1))
    >> op.where(lambda kv: kv[0] == "foo")
    >> dict
    > str
)
```

Or you can use the `x` or `P` operators to pipe values infix like

```python
10 <<x>> fn(int, int)(lambda x: x + 10) <<x>> float <<x>> str
```
