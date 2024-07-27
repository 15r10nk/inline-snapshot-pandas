from pandas.testing import assert_frame_equal
from pandas.testing import assert_index_equal
from pandas.testing import assert_series_equal


def setup():
    pass


def snapshot(value=None):
    assert (
        value is not None
    ), """\
This version of inline-snapshot-pandas provides only limited snapshot support.
All functions are implemented as noop's, which allows the execution of tests for non-insider users.

The full feature set is currently only available for insiders and can not be installed from PyPI.

You have to become a sponsor first:

    https://github.com/sponsors/15r10nk

and can then install the library from the private github repo:

    https://github.com:15r10nk-insiders/inline-snapshot-pandas.git
"""
    return value


__all__ = (
    "assert_frame_equal",
    "assert_index_equal",
    "assert_series_equal",
    "setup",
    "snapshot",
)
