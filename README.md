<!-- -8<- [start:Header] -->


![ci](https://github.com/15r10nk/inline-snapshot-pandas/actions/workflows/ci.yml/badge.svg?branch=main)
[![Docs](https://img.shields.io/badge/docs-mkdocs-green)](https://15r10nk.github.io/inline-snapshot-pandas/)
[![pypi version](https://img.shields.io/pypi/v/inline-snapshot-pandas.svg)](https://pypi.org/project/inline-snapshot-pandas/)
![Python Versions](https://img.shields.io/pypi/pyversions/inline-snapshot-pandas)
![PyPI - Downloads](https://img.shields.io/pypi/dw/inline-snapshot-pandas)
[![coverage](https://img.shields.io/badge/coverage-100%25-blue)](https://15r10nk.github.io/inline-snapshot-pandas/contributing/#coverage)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/15r10nk)](https://github.com/sponsors/15r10nk)

<!-- -8<- [end:Header] -->

## Installation


This project is currently only available for insiders, which mean that you can get access to it if you sponsor me.
You should then have access to [this repository](https://github.com/15r10nk-insiders/inline-snapshot-pandas).

``` bash
pip install git+ssh://git@github.com:15r10nk-insiders/inline-snapshot-pandas.git@insiders
```



## Usage

This packages provides special `assert_(frame|series|index)_equal` implementation which accept a snapshot as second argument.

``` python
from pandas import DataFrame
from inline_snapshot_pandas import assert_frame_equal
from inline_snapshot import snapshot


def test_assert_equal():
    df = DataFrame({"col0": [1, 2]})

    assert_frame_equal(df, snapshot())
```

```bash
pytest --inline-snapshot=create
```

``` python
from pandas import DataFrame
from inline_snapshot_pandas import assert_frame_equal
from inline_snapshot import snapshot


def test_assert_equal():
    df = DataFrame({"col0": [1, 2]})

    assert_frame_equal(
        df,
        snapshot(DataFrame([{"col0": 1}, {"col0": 2}])),
    )
```

Another way to use it is to call `setup()` in `conftest.py`, which replaces the implementation which pandas uses.

``` python
from inline_snapshot_pandas import setup

setup()
```

You can then use implementation from pandas with snapshots.

``` python
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
```

## Usage for non-insiders

The version which is currently available on pip provides functions which can be used by non insiders.
They provides a special `snapshot` function which is implemented as `lambda value: value` and can be used with the normal `assert_*_equal` functions of pandas.

The following code can be executed with the insider an non-insider version:

``` python
from pandas import DataFrame
from inline_snapshot_pandas import assert_frame_equal

# importing snapshot from inline_snapshot_pandas is important
from inline_snapshot_pandas import snapshot


def test_assert_equal():
    df = DataFrame({"col0": [1, 2]})

    assert_frame_equal(
        df,
        snapshot(DataFrame([{"col0": 1}, {"col0": 2}])),
    )
```


<!-- -8<- [start:Feedback] -->
## Issues

If you encounter any problems, please [report an issue](https://github.com/15r10nk/inline-snapshot-pandas/issues) along with a detailed description.
<!-- -8<- [end:Feedback] -->

## License

Distributed under the terms of the [MIT](http://opensource.org/licenses/MIT) license, "inline-snapshot-pandas" is free and open source software.
