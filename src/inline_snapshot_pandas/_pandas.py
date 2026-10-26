from typing import Callable, Optional

import pandas
from inline_snapshot._snapshot.generic_value import GenericValue
from inline_snapshot._types import SnapshotRefBase
from inline_snapshot.plugin import ImportFrom, customize


class PandasValue:
    def __init__(
        self,
        value,
        compare: Callable[[object, object], bool],
        repr_function: Optional[Callable[[object], object]] = None,
    ):
        self.value = value
        self.compare = compare
        self.repr_function = repr_function

    def __eq__(self, other):
        if isinstance(other, (GenericValue, SnapshotRefBase)):
            return NotImplemented
        if isinstance(other, PandasValue):
            other = other.value
        if not isinstance(other, type(self.value)):
            return NotImplemented
        return self.compare(self.value, other)


@customize
def customize_pandas(value, builder):
    if not isinstance(value, PandasValue):
        return None

    assert value.repr_function is not None
    constructor_name = type(value.value).__name__
    constructor = builder.create_code(
        constructor_name, imports=[ImportFrom("pandas", constructor_name)]
    )
    return builder.create_call(
        constructor,
        [value.repr_function(value.value)],
        {},
    )


def defer_snapshot_comparisons(data_type) -> None:
    original = data_type.__eq__

    def new_eq(left, right):
        if isinstance(right, (GenericValue, SnapshotRefBase, PandasValue)):
            return NotImplemented
        return original(left, right)

    data_type.__eq__ = new_eq


for _data_type in (pandas.DataFrame, pandas.Series, pandas.Index):
    defer_snapshot_comparisons(_data_type)
