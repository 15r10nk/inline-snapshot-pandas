import sys

from inline_snapshot import snapshot
from inline_snapshot.extra import raises
from inline_snapshot.testing import Example
from inline_snapshot_pandas import assert_frame_equal
from inline_snapshot_pandas import assert_index_equal
from inline_snapshot_pandas import assert_series_equal
from inline_snapshot_pandas import snapshot as pandas_snapshot
from pandas import DataFrame
from pandas import Index
from pandas import Series


def test_assert_equal():
    df = DataFrame({"col0": [1, 2], "col1": [1, 5j], "col3": ["a", "b"]})

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
    assert_index_equal(index, snapshot(Index([0, 1, 2, 3, 4])))

    # for Series
    index = Series({1: 8, 5: 4})
    assert_series_equal(index, snapshot(Series({1: 8, 5: 4})))


def test_assert_equal_twice():
    df = DataFrame({"col0": [1, 2], "col1": [1, 5j], "col3": ["a", "b"]})

    s = pandas_snapshot(
        DataFrame(
            [
                {"col0": 1, "col1": (1 + 0j), "col3": "a"},
                {"col0": 2, "col1": 5j, "col3": "b"},
            ]
        )
    )

    assert_frame_equal(df, s)

    assert_frame_equal(df, s)


def test_setup():

    Example(
        {
            "conftest.py": """\
from inline_snapshot_pandas import setup
setup()
""",
            "test_pandas.py": """\
from pandas import DataFrame
from pandas.testing import assert_frame_equal
from inline_snapshot import snapshot


def test_assert_equal():
    df = DataFrame({"col0": [1, 2], "col1": [1, 5j], "col3": ["a", "b"]})

    # the second argument can be a snapshot
    assert_frame_equal(
        df,
        snapshot(),
    )
""",
        }
    ).run_pytest(
        ["--inline-snapshot=create"],
        changed_files=snapshot({"test_pandas.py": """\
from pandas import DataFrame
from pandas.testing import assert_frame_equal
from inline_snapshot import snapshot


def test_assert_equal():
    df = DataFrame({"col0": [1, 2], "col1": [1, 5j], "col3": ["a", "b"]})

    # the second argument can be a snapshot
    assert_frame_equal(
        df,
        snapshot(
            DataFrame(
                [
                    {"col0": 1, "col1": (1 + 0j), "col3": "a"},
                    {"col0": 2, "col1": 5j, "col3": "b"},
                ]
            )
        ),
    )
"""}),
        returncode=1,
    )


def test_dataframp_eq():
    df = DataFrame({"col0": [1, 2], "col1": [1, 5j], "col3": ["a", "b"]})

    with raises(
        snapshot(
            "ValueError: The truth value of a DataFrame is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all()."
        )
    ):
        assert df == df


def test_not_equal():
    Example("""\
from pandas import DataFrame
from inline_snapshot_pandas import assert_frame_equal
from inline_snapshot import snapshot


def test_assert_equal():
    df = DataFrame({"col0": [1, 2]})

    # the second argument can be a snapshot
    assert_frame_equal(
        df,
        snapshot(DataFrame({"col0": [1, 3]})),
    )
""").run_inline(
        raises=(
            snapshot("""\
AssertionError:
DataFrame.iloc[:, 0] (column name="col0") are different

DataFrame.iloc[:, 0] (column name="col0") values are different (50.0 %)
[index]: [0, 1]
[left]:  [1, 2]
[right]: [1, 3]
At positional index 1, first diff: 2 != 3\
""")
            if sys.version_info < (3, 9)
            else snapshot("""\
AssertionError:
DataFrame.iloc[:, 0] (column name="col0") are different

DataFrame.iloc[:, 0] (column name="col0") values are different (50.0 %)
[index]: [0, 1]
[left]:  [1, 2]
[right]: [1, 3]\
""")
        )
    ).run_inline(
        ["--inline-snapshot=fix"],
        changed_files=snapshot({"tests/test_something.py": """\
from pandas import DataFrame
from inline_snapshot_pandas import assert_frame_equal
from inline_snapshot import snapshot


def test_assert_equal():
    df = DataFrame({"col0": [1, 2]})

    # the second argument can be a snapshot
    assert_frame_equal(
        df,
        snapshot(DataFrame([{"col0": 1}, {"col0": 2}])),
    )
"""}),
    )
