from sqlalchemy.sql.elements import ColumnElement
from typing import cast


def cast_sql(cond: bool) -> ColumnElement[bool]:
    return cast("ColumnElement[bool]", cond)
