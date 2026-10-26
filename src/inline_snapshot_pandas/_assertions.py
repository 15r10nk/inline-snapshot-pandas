from functools import wraps
from typing import Optional

import pandas
import pandas.testing
from inline_snapshot import snapshot_arg
from inline_snapshot._snapshot.generic_value import GenericValue
from inline_snapshot._types import SnapshotRefBase

from ._pandas import PandasValue


def _make_assert_equal(assert_equal, expected_type, repr_function):
    @wraps(assert_equal)
    def result(actual, desired=..., *args, **kwargs):
        error: Optional[Exception] = None

        def compare(left, right):
            nonlocal error
            try:
                assert_equal(left, right, *args, **kwargs)
            except Exception as exception:
                error = exception
                return False
            return True

        if not isinstance(desired, (GenericValue, SnapshotRefBase)):
            if desired is not ... and not isinstance(desired, expected_type):
                assert_equal(actual, desired, *args, **kwargs)
            desired = PandasValue(desired, compare, repr_function)
            desired = snapshot_arg(desired)

        if not (PandasValue(actual, compare, repr_function) == desired):
            if error is not None:
                raise error
            raise AssertionError("Pandas comparison failed")

    return result


assert_frame_equal = _make_assert_equal(
    pandas.testing.assert_frame_equal,
    pandas.DataFrame,
    lambda frame: frame.to_dict("records"),
)
assert_series_equal = _make_assert_equal(
    pandas.testing.assert_series_equal,
    pandas.Series,
    lambda series: series.to_dict(),
)
assert_index_equal = _make_assert_equal(
    pandas.testing.assert_index_equal,
    pandas.Index,
    lambda index: index.to_list(),
)


def setup():
    """Make Pandas' testing helpers accept inline snapshots."""

    pandas.testing.assert_frame_equal = assert_frame_equal
    pandas.testing.assert_series_equal = assert_series_equal
    pandas.testing.assert_index_equal = assert_index_equal
