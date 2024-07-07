from functools import wraps
from typing import Optional

import pandas.testing
from inline_snapshot import customize_repr
from inline_snapshot import snapshot
from inline_snapshot._inline_snapshot import GenericValue

__all__ = (
    "setup",
    "assert_frame_equal",
    "assert_series_equal",
    "assert_index_equal",
    "snapshot",
)


def make_assert_equal(data_type, assert_equal, repr_function):

    class Wrapper:
        def __init__(self, df, cmp):
            self.df = df
            self.cmp = cmp

        def __repr__(self):
            return f"{data_type.__name__}({repr_function(self.df)!r})"

        def __eq__(self, other):
            if isinstance(other, data_type):
                return self.cmp(self.df, other)
            if isinstance(other, Wrapper) and isinstance(other.df, data_type):
                return self.cmp(self.df, other.df)
            return NotImplemented

    original = data_type.__eq__

    def new_eq(a, b):
        if isinstance(b, (GenericValue, Wrapper)):
            return NotImplemented
        return original(a, b)

    data_type.__eq__ = new_eq

    @wraps(assert_equal)
    def result(df, df_snapshot, *args, **kargs):
        error: Optional[AssertionError] = None

        def cmp(a, b):
            nonlocal error
            try:
                assert_equal(a, b, *args, **kargs)
            except AssertionError as e:
                error = e
                return False
            return True

        if not Wrapper(df, cmp) == df_snapshot:
            assert error is not None
            raise error

    return result


assert_frame_equal = make_assert_equal(
    pandas.DataFrame,
    pandas.testing.assert_frame_equal,
    lambda df: df.to_dict("records"),
)
assert_series_equal = make_assert_equal(
    pandas.Series, pandas.testing.assert_series_equal, lambda df: df.to_dict()
)
assert_index_equal = make_assert_equal(
    pandas.Index, pandas.testing.assert_index_equal, lambda df: df.to_list()
)


def setup():
    pandas.testing.assert_frame_equal = assert_frame_equal
    pandas.testing.assert_series_equal = assert_series_equal
    pandas.testing.assert_index_equal = assert_index_equal
