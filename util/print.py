from functools import singledispatch
from typing import Any, Callable, Set, Union, FrozenSet, List, Tuple, Dict, Optional
from types import NoneType
from io import StringIO


dict_keys = type({}.keys())
dict_values = type({}.values())
dict_items = type({}.items())


def stringify(_obj: Any, indent: int = 4, cls: Optional[Callable[[Any, StringIO], bool]] = None) -> str:
    """
    Return the string representation of an object.

    Parameters:
        _obj: The object to convert to a string.
        indent: Number of spaces for indentation (default is 4).
        cls: Optional callable for custom serialization of objects.
    """
    with StringIO() as buffer:
        buffer_write(_obj, buffer, indent=indent, depth=0, cls=cls, visited=set())
        return buffer.getvalue()


def pprint(*_objects: Any, indent: int = 4, cls: Optional[Callable[[Any, StringIO], bool]] = None):
    """
    Print the string representation of an object using the stringify function.

    Parameters:
        _obj: The object to convert to a string.
        indent: Number of spaces for indentation (default is 4).
        cls: Optional callable for custom serialization of objects.
    """
    for obj in _objects:
        end_line = "\n" if _objects[-1] == obj else " "
        print(stringify(obj, indent=indent, cls=cls), end=end_line)


@singledispatch
def buffer_write(
    _obj: Any,
    _buffer: StringIO,
    *,
    visited: Set[int],
    cls: Optional[Callable[[Any, StringIO], bool]] = None,
    **kwargs,
):
    obj_id = id(_obj)
    if obj_id in visited:
        _buffer.write(f"<Circular reference to {type(_obj).__name__}, ID({obj_id})>")
        return

    visited.add(obj_id)

    if cls is not None and cls(_obj, _buffer, visited=visited, cls=cls, **kwargs):
        pass
    else:
        _buffer.write(f"{_obj.__class__.__name__}(")
        # Recursively stringify each key-value pair inside object
        if hasattr(_obj, "__dict__"):
            buffer_write(_obj.__dict__, _buffer, visited=visited, cls=cls, **kwargs)
        else:
            _buffer.write(str(_obj))
        _buffer.write(")")

    visited.remove(obj_id)


@buffer_write.register(str)
def _(_obj: str, _buffer: StringIO, **kwargs):
    if _obj.find("\n") == -1:
        _buffer.write(f'"{_obj}"')
    else:
        _buffer.write(f'"""{_obj}"""')


@buffer_write.register(type)
def _(_obj: type, _buffer: StringIO, **kwargs):
    _buffer.write(_obj.__name__)


@buffer_write.register(complex)
def _(_obj: complex, _buffer: StringIO, **kwargs):
    _buffer.write("complex(")

    if _obj.real != 0:
        _buffer.write(str(_obj.real))
        _buffer.write(" ")
        _buffer.write("-" if _obj.imag < 0 else "+")
        _buffer.write(" ")
    elif _obj.imag < 0:
        _buffer.write("-")

    _buffer.write(str(abs(_obj.imag)))
    _buffer.write("j")

    _buffer.write(")")


@buffer_write.register(Union[int, float, bool, bytes, bytearray, NoneType])
def _(_obj: Union[int, float, bool, bytes, bytearray, NoneType], _buffer: StringIO, **kwargs):
    _buffer.write(str(_obj))


@buffer_write.register(Union[list, set, frozenset, tuple])
def _(
    _obj: Union[List, Set, FrozenSet, Tuple],
    _buffer: StringIO,
    *,
    indent: int,
    depth: int,
    visited: Set[int],
    **kwargs,
):
    obj_id = id(_obj)
    if obj_id in visited:
        _buffer.write(f"<Circular reference to {type(_obj).__name__}, ID({obj_id})>")
        return

    symbols = {
        list: ("[", "]"),
        set: ("{", "}"),
        frozenset: ("frozenset({", "})"),
        tuple: ("(", ")"),
    }

    for key, value in symbols.items():
        if isinstance(_obj, key):
            opening, closing = value
            break

    # This means that object is inheriting from the underlying base class
    if type(_obj) not in symbols:
        _buffer.write(f"{type(_obj).__name__}(")

    # If the collection is empty, write appropriate symbols
    if len(_obj) == 0:
        _buffer.write(opening + closing)
    else:
        visited.add(obj_id)

        _buffer.write(opening)
        _buffer.write("\n")

        # Recursively stringify each item in the collection
        for value in _obj:
            _buffer.write(" " * indent * (depth + 1))
            buffer_write(value, _buffer, indent=indent, depth=depth + 1, visited=visited, **kwargs)
            _buffer.write(",\n")

        _buffer.write(" " * indent * depth)
        _buffer.write(closing)

        visited.remove(obj_id)

    if type(_obj) not in symbols:
        _buffer.write(")")


@buffer_write.register(dict)
def _(
    _obj: Dict,
    _buffer: StringIO,
    *,
    indent: int,
    depth: int,
    visited: Set[int],
    **kwargs,
):
    # If the dictionary is empty, write '{}'
    if len(_obj) == 0:
        _buffer.write("{}")
        return

    obj_id = id(_obj)
    if obj_id in visited:
        _buffer.write(f"<Circular reference to {type(_obj).__name__}, ID({obj_id})>")
        return

    visited.add(obj_id)

    _buffer.write("{\n")

    # Recursively stringify each key-value pair
    for key, value in _obj.items():
        _buffer.write(" " * indent * (depth + 1))
        buffer_write(key, _buffer, indent=indent, depth=depth + 1, visited=visited, **kwargs)
        _buffer.write(": ")
        buffer_write(value, _buffer, indent=indent, depth=depth + 1, visited=visited, **kwargs)
        _buffer.write(",\n")

    _buffer.write(" " * indent * depth)
    _buffer.write("}")

    visited.remove(obj_id)


@buffer_write.register(dict_keys)
def _(_obj: List, _buffer: StringIO, **kwargs):
    _buffer.write("dict_keys(")
    buffer_write(list(_obj), _buffer, **kwargs)
    _buffer.write(")")


@buffer_write.register(dict_values)
def _(_obj: List, _buffer: StringIO, **kwargs):
    _buffer.write("dict_values(")
    buffer_write(list(_obj), _buffer, **kwargs)
    _buffer.write(")")


@buffer_write.register(dict_items)
def _(_obj: Dict, _buffer: StringIO, **kwargs):
    _buffer.write("dict_items(")
    buffer_write(dict(_obj), _buffer, **kwargs)
    _buffer.write(")")


@buffer_write.register(range)
def _(_obj: range, _buffer: StringIO, **kwargs):
    _buffer.write("range(")

    if _obj.start != 0:
        _buffer.write(str(_obj.start))
        _buffer.write(", ")

    _buffer.write(str(_obj.stop))

    if _obj.step != 1:
        _buffer.write(", ")
        _buffer.write(str(_obj.step))

    _buffer.write(")")


try:
    import numpy as np

    @buffer_write.register(np.ndarray)
    def _(_obj: np.ndarray, _buffer: StringIO, *, indent: int, depth: int, **kwargs):
        if _obj.ndim == 0 or _obj.size == 0:
            _buffer.write("[]")
            return

        # Special formatting for 2D arrays or matrices
        if _obj.ndim == 2:
            _buffer.write("[\n")
            for row in _obj:
                _buffer.write(" " * indent * (depth + 1))
                _buffer.write("[")

                for value in row:
                    buffer_write(value, _buffer, indent=indent, depth=depth + 1, **kwargs)
                    _buffer.write(", ")

                if len(row) > 0:
                    _buffer.seek(_buffer.tell() - 2)

                _buffer.write("],\n")

            _buffer.write(" " * indent * depth)
            _buffer.write("]")
        else:
            _buffer.write("[\n")

            for value in _obj:
                _buffer.write(" " * indent * (depth + 1))
                buffer_write(value, _buffer, indent=indent, depth=depth + 1, **kwargs)
                _buffer.write(",\n")

            _buffer.write(" " * indent * depth)
            _buffer.write("]")
except ImportError:
    pass
