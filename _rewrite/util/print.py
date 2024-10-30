from typing import Any, Callable


def stringify(_obj: Any, *, indent: int = 4, depth: int = 0, cls: Callable[..., Any] = None) -> str:
    """
    Convert an object to a string representation, with customizable indentation and depth.

    Parameters:
        _obj: The object to convert to a string.
        indent: Number of spaces for indentation (default is 4).
        depth: Current depth level for nested structures (default is 0).
        cls: Optional callable for custom serialization of objects (default is None).

    Returns:
        str: A string representation of the object.
    """

    # If the object is a string, return it wrapped in quotes
    if isinstance(_obj, str):
        return f'"{_obj}"'

    # Handle complex numbers by converting to string format
    elif isinstance(_obj, complex):
        _obj: str = str(_obj)

        # Format complex number appropriately
        if _obj.find("(") != -1:
            return f'"complex{_obj.replace("+", " + ").replace("-", " - ")}"'
        else:
            return f'"complex({_obj})"'

    # Convert basic data types to string
    elif isinstance(_obj, (int, float, bool, bytes, bytearray, type(None))):
        return str(_obj)

    # If the object is a class, return its name
    elif isinstance(_obj, type):
        return _obj.__name__

    ret = ""

    # Handle collections (list, set, frozenset, tuple)
    if isinstance(_obj, (list, set, frozenset, tuple)):
        symbols = {
            list: ("[", "]"),
            set: ("{", "}"),
            frozenset: ("frozenset({", "})"),
            tuple: ("(", ")"),
        }

        # If the collection is empty, return appropriate symbols
        if len(_obj) == 0:
            return "".join(symbols[type(_obj)])

        ret += symbols[type(_obj)][0]  # Opening symbol
        ret += "\n"

        # Recursively stringify each item in the collection
        for value in _obj:
            ret += " " * indent * (depth + 1)  # Indentation for nested levels
            ret += stringify(value, indent=indent, depth=depth + 1)  # Recursive call
            ret += ",\n"  # Separator for items

        ret += " " * indent * depth  # Indentation for closing symbol
        ret += symbols[type(_obj)][1]  # Closing symbol

    # Handle dictionaries
    elif isinstance(_obj, dict):
        # If the dictionary is empty, return '{}'
        if len(_obj) == 0:
            return "{}"

        ret += "{\n"  # Opening brace for dict

        # Recursively stringify each key-value pair
        for key, value in _obj.items():
            ret += " " * indent * (depth + 1)
            ret += f'"{key}": {stringify(value, indent=indent, depth=depth + 1)}'  # Key-value pair
            ret += ",\n"  # Separator for items

        ret += " " * indent * depth  # Indentation for closing brace
        ret += "}"  # Closing brace

    # Handle class objects
    else:
        # If the object is not a recognized type, represent it by its class name
        ret += f"{_obj.__class__.__name__}("

        if hasattr(_obj, "__dict__"):  # Check if it has a __dict__ attribute
            ret += stringify(_obj.__dict__, indent=indent, depth=depth)
        elif cls is not None:
            ret += cls(_obj, indent=indent, depth=depth)  # Use custom serialization if provided
        else:
            ret += str(_obj)  # Fallback to str() for unknown types
        ret += ")"
    # Return the constructed string representation
    return ret


def pprint(_obj: Any, **kwargs):
    """
    Print the string representation of an object using the stringify function.

    Parameters:
        _obj: The object to convert to a string.
        indent: Number of spaces for indentation (default is 4).
        depth: Current depth level for nested structures (default is 0).
        cls: Optional callable for custom serialization of objects (default is None).
    """
    print(stringify(_obj, **kwargs))
