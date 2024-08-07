from typing import Any, Type, cast


def sql_typecast[T](value: Any, target_type: Type[T]) -> T:
    if not isinstance(value, target_type):
        raise TypeError(f"Cannot cast {type(value)} to {target_type}")
    return cast(T, value)
