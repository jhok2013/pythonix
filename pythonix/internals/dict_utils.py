from typing import TypeVar, Dict, Callable
import pythonix.res as res

Val = TypeVar('Val')
NewVal = TypeVar('NewVal')
Key = TypeVar('Key', str, int, float, tuple)
NewKey = TypeVar('NewKey', str, int, float, tuple)

def map_keys(using: Callable[[Key], NewKey]):
    """
    Runs the provided function over each key in a `dict`, returning a new
    `dict` with the updated `keys` and the same values
    #### Example
    ```python
    import pythonix.dict_utils as dict_utils

    data: dict[str, int] = {'First': 1, 'Second': 2}
    upper_dict: dict[str, int] = dict_utils.map_keys(str.upper)(data)
    upper_keys: tuple[str, ...] = tuple(upper_dict.keys())
    assert upper_keys == ('FIRST', 'SECOND')
    ```
    """
    def get_dict(dict_obj: Dict[Key, Val]) -> Dict[NewKey, Val]:

        return {using(k): v for k, v in dict_obj.items()}
    
    return get_dict


def map_values(using: Callable[[Val], NewVal]):
    """
    Runs the provided function over each value in a `dict`, returning a new
    `dict` with the updated values and the same keys
    #### Example
    ```python
    import pythonix.dict_utils as dict_utils

    data: dict[str, int] = {'First': 1, 'Second': 2}
    str_values_dict: dict[str, str] = dict_utils.map_values(str)
    values: tuple[str, ...] = tuple(str_values_dict.values())
    assert values == ('1', '2')
    ```
    """   
    def get_dict(dict_obj: Dict[Key, Val]) -> Dict[Key, NewVal]:

        return {k: using(v) for k, v in dict_obj.items()}
    
    return get_dict


def filter_keys(predicate: Callable[[Key], bool]):
    """
    Runs the provided filter function over the keys in a `dict`, returning a new `dict`
    with only the `keys` that evaluated to `True`
    #### Example
    ```python
    import pythonix.dict_utils as dict_utils

    data: dict[str, int] = {'First': 1, 'Second': 2}
    only_first: dict[str, int] = dict_utils.filter_keys(lambda key: key == 'First')
    assert tuple(only_first.items()) == ('First', 1)
    ```
    """
    def get_dict(dict_obj: Dict[Key, Val]) -> Dict[Key, Val]:

        return {k: v for k, v in dict_obj.items() if predicate(k)}
    
    return get_dict


def filter_values(predicate: Callable[[Val], bool]):
    """
    Runs the provided filter function over the values in a `dict`, returning a new `dict`
    with only the values that evaluated to `True`
    #### Example
    ```python
    import pythonix.dict_utils as dict_utils

    data: dict[str, int] = {'First': 1, 'Second': 2}
    evens_only: dict[str, int] = dict_utils.filter_values(lambda v: v % 2 == 0)
    assert tuple(evens_only.items()) == ('Second', 2)
    ```
    """
    def get_dict(dict_obj: Dict[Key, Val]) -> Dict[Key, Val]:

        return {k: v for k, v in dict_obj.items() if predicate(v)}
    
    return get_dict


def merge(new_dict: Dict[NewKey, NewVal]):
    """
    Merges two dictionaries together, with values in the `old_dict` overrinding the values from the `new_dict`
    #### Example
    ```python
    old: dict[str, int] = {'foo': 0}
    new: dict[int, str] = {1: 'bar'}
    merged: dict[str | int, str | int] = merge(new)(old)
    ```
    """
    def get_old(old_dict: Dict[Key, Val]) -> Dict[Key | NewKey, Val | NewVal]:

        return old_dict | new_dict

    return get_old


def put(key: NewKey):
    """
    Puts a new value into a `dict`.
    #### Example
    ```python
    data: dict[str, int] = {'hello': 0}    
    updated: dict[str, int] = put('joe')(1)(data)
    ```
    """
    def get_val(val: NewVal) -> Callable[[Dict[Key, Val]], Dict[Key | NewKey, Val | NewVal]]:

        def get_dict(dict_obj: Dict[Key, Val]) -> Dict[Key | NewKey, Val | NewVal]:

            return merge(dict_obj)({key: val})
        
        return get_dict
    
    return get_val


def get(key: Key):
    """
    Safely retrieves a value from the `dict_obj` as an `Ok[Val]` or `Err[Nil]` 
    #### Example
    ```python
    data: dict[str, int] = {'hello': 0}
    opt: Ok[int] | Err[Nil] = get('hello')(data)
    value: int = res.unwrap(opt)
    ```
    """
    def get_dict(dict_obj: Dict[Key, Val]) -> res.Ok[Val] | res.Err[res.Nil]:

        return res.some(dict_obj.get(key))
    
    return get_dict
    