from inline_snapshot import snapshot
from inline_snapshot.extra import raises
from inline_snapshot_pandas import assert_frame_equal
from inline_snapshot_pandas import assert_index_equal
from inline_snapshot_pandas import assert_series_equal
from inline_snapshot_pandas import setup
from inline_snapshot_pandas import snapshot as pandas_snapshot
from pandas import DataFrame
from pandas import Index
from pandas import Series


def test_assert_equal():
    df = DataFrame({"col0": [1, 2], "col1": [1, 5j], "col3": ["a", "b"]})

    # the second argument can be a snapshot
    # the second argument can be a snapshot
    assert_frame_equal(
        df,
        pandas_snapshot(
            DataFrame(
                [
                    {"col0": 1, "col1": (1 + 0j), "col3": "a"},
                    {"col0": 2, "col1": 5j, "col3": "b"},
                ]
            )
        ),
    )

    # and can also be used without a snapshot
    assert_frame_equal(df, df)

    # for Index
    index = Index(range(5))
    assert_index_equal(index, pandas_snapshot(Index([0, 1, 2, 3, 4])))

    # for Series
    index = Series({1: 8, 5: 4})
    assert_series_equal(index, pandas_snapshot(Series({1: 8, 5: 4})))


def test_snapshot():

    with raises(
        snapshot(
            """\
AssertionError:
This version of inline-snapshot-pandas provides only limited snapshot support.
All functions are implemented as noop's, which allows the execution of tests for non-insider users.

The full feature set is currently only available for insiders and can not be installed from PyPI.

You have to become a sponsor first:

    https://github.com/sponsors/15r10nk

and can then install the library from the private github repo:

    https://github.com:15r10nk-insiders/inline-snapshot-pandas.git
"""
        )
    ):
        pandas_snapshot()


def test_setup():
    # setup does nothing but can be called
    setup()
