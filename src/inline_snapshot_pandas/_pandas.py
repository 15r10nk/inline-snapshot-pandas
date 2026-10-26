from typing import Callable

import pandas
from inline_snapshot._snapshot.generic_value import GenericValue
from inline_snapshot._types import SnapshotRefBase
from inline_snapshot.plugin import ImportFrom, customize


class PandasValue:
    def __init__(
        self,
        value,
        compare: Callable[[object, object], bool],
    ):
        self.value = value
        self.compare = compare

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

    if isinstance(value.value, pandas.DataFrame):
        representation = value.value.to_dict("records")
    elif isinstance(value.value, pandas.Series):
        representation = value.value.to_dict()
    elif isinstance(value.value, pandas.Index):
        representation = value.value.to_list()
    else:
        return None

    constructor_name = type(value.value).__name__
    constructor = builder.create_code(
        constructor_name, imports=[ImportFrom("pandas", constructor_name)]
    )
    kwargs = {}
    if isinstance(value.value, pandas.DataFrame):
        index = value.value.index
        is_default_index = (
            isinstance(index, pandas.RangeIndex)
            and index.start == 0
            and index.stop == len(value.value)
            and index.step == 1
            and index.name is None
        )
        if not is_default_index:
            if isinstance(index, pandas.MultiIndex):
                index_constructor = builder.create_code(
                    "MultiIndex.from_tuples",
                    imports=[ImportFrom("pandas", "MultiIndex")],
                )
                index_args = [index.to_list()]
                index_kwargs = {"names": index.names}
            elif isinstance(index, pandas.RangeIndex):
                index_constructor = builder.create_code(
                    "RangeIndex", imports=[ImportFrom("pandas", "RangeIndex")]
                )
                index_args = [index.start, index.stop, index.step]
                index_kwargs = {"name": index.name}
            else:
                index_constructor = builder.create_code(
                    "Index", imports=[ImportFrom("pandas", "Index")]
                )
                index_args = [index.to_list()]
                index_kwargs = {"name": index.name}
            kwargs["index"] = builder.create_call(
                index_constructor, index_args, index_kwargs
            )
    return builder.create_call(
        constructor,
        [representation],
        kwargs,
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
