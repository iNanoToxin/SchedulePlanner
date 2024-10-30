from typing import get_origin, get_args, Union, List, Dict, Any, Literal

Json = Union[Dict[str, "Json"], List["Json"], str, int, float, bool, None]


def instantiate_type(_value: Any, _type: Any):
    """
    Instantiate or cast a value to the provided type.

    If the value is None:
      - For lists or dictionaries, it returns empty instances of these types.
      - For other types, it attempts to create a new instance of the given type.

    If the value is not None:
      - Ensures the value matches the expected type or attempts to cast it.
      - Recursively processes nested types (e.g., lists, dicts, unions).

    Supports:
      - Lists: Recursively casts elements to the list's specified type.
      - Dictionaries: Recursively casts keys and values to their respective types.
      - Unions: Tries multiple types until one matches.
      - Literals: Ensures the value is among accepted literal values.
      - Typed classes: Returns the value if it matches the target class.

    Raises:
      - AssertionError if the value cannot be cast to the expected type or is invalid.
    """

    # Return value if type is any
    if _type is Any:
        return _value

    # Handle list types (e.g., List[int])
    if get_origin(_type) is list:
        # Default to an empty list
        if _value is None:
            return []

        assert isinstance(_value, list), f"Expected list, got {type(_value).__name__}"

        types = get_args(_type)
        if len(types) == 0:
            return _value  # List is of type any, return the list

        # Recursively apply instantiation logic to each element in the list
        return [instantiate_type(item, types[0]) for item in _value]

    # Handle dictionary types (e.g., Dict[str, int])
    if get_origin(_type) is dict:
        # Default to an empty dictionary
        if _value is None:
            return {}

        assert isinstance(_value, dict), f"Expected dict, got {type(_value).__name__}"

        types = get_args(_type)
        if len(types) == 0:
            return _value  # Dict is of type any, return the dictionary

        # Recursively apply instantiation logic to keys and values
        return {instantiate_type(k, types[0]): instantiate_type(v, types[1]) for k, v in _value.items()}

    # Handle union types (e.g., Union[str, int, dict, list])
    if get_origin(_type) is Union or isinstance(_type, type(int | str)):  # type(int | str) returns the UnionType
        types = get_args(_type)

        for obj_type in types:
            if obj_type is Any or isinstance(_value, obj_type):
                return instantiate_type(_value, obj_type)
        raise AssertionError(f"Expected {Union[_type]}, got {type(_value).__name__}")

    # Handle literal objects
    if get_origin(_type) is Literal:
        if _value in get_args(_type):
            return _value
        raise AssertionError(f"Expected one of {get_args(_type)}, got {_value}")

    try:
        if issubclass(_type, TypedClass):
            # If the class is a TypedClass, it does not need to be checked
            if type(_value) is _type:
                return _value
            # Raise error if value is not a dict (required for TypedClass)
            assert type(_value) is dict, f"Expected dict, got {type(_value).__name__}"
            # Create new TypedClass instance
            return _type(_value)
        else:
            if (_type is float or _type is int) and (type(_value) is float or type(_value) is int):
                _value = _type(_value)
            assert type(_value) is _type, f"Expected {_type.__name__}, got {type(_value).__name__}"
        # Return value if it is correct type
        return _value
    except AssertionError:
        raise
    except Exception:
        raise AssertionError(f"Type {_type.__name__} cannot be instantiated with {type(_value).__name__}")


class TypedClass:
    """
    A base class for models with type-annotated attributes that automatically initializes
    attributes from a given dictionary. It ensures that each attribute is assigned a value
    based on its type annotation, applying default values where necessary.

    Attributes are expected to be defined via type annotations in subclasses.
    If the value is not provided in the input dictionary, a default value will be generated
    according to the type (e.g., empty lists for `List`, empty dictionaries for `Dict`).

    Example:
        ```
        class Bookstore(TypedClass):
            url: str
            label: str

        data = {"url": "https://example.com", "label": "Example Store"}
        bookstore = Bookstore(data)
        print(bookstore.url)  # Output: https://example.com
        ```

    Args:
        _data (Json): A dictionary containing values to initialize the model's attributes.
    """

    def __init__(self, _data: Json):
        # Iterate over all annotated attributes in the class
        for attribute, annotated_type in self.__annotations__.items():
            # Use `instantiate_type` to handle nested or complex types and set attribute value
            try:
                setattr(self, attribute, instantiate_type(_data.get(attribute), annotated_type))
            except AssertionError as e:
                raise TypeError(f"{self.__class__.__name__} attribute {attribute}: {str(e)}")
            except Exception:
                raise
