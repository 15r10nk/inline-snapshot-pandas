from inline_snapshot import snapshot
from inline_snapshot.extra import raises


def test_nothing():

    with raises(
        snapshot(
            """\
AssertionError:

This project is currently only available for insiders and can not be installed from PyPI.

You have to become a sponsor first:

    https://github.com/sponsors/15r10nk

and can then install the library from the private github repo:

    https://github.com:15r10nk-insiders/inline-snapshot-pandas.git
"""
        )
    ):
        pass
