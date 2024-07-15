from sqlalchemy.sql.elements import ColumnElement
from typing import Type, cast, Any


def sql_typecast[T](value: Any, target_type: Type[T]) -> T:
    if not isinstance(value, target_type):
        raise TypeError(f"Cannot cast {type(value)} to {target_type}")
    return cast(T, value)
