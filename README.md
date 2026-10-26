<!-- -8<- [start:Header] -->

# inline-snapshot-pandas

![ci](https://github.com/15r10nk/inline-snapshot-pandas/actions/workflows/ci.yml/badge.svg?branch=main)
[![Docs](https://img.shields.io/badge/docs-mkdocs-green)](https://15r10nk.github.io/inline-snapshot-pandas/latest/)
[![pypi version](https://img.shields.io/pypi/v/inline-snapshot-pandas.svg)](https://pypi.org/project/inline-snapshot-pandas/)
![Python Versions](https://img.shields.io/pypi/pyversions/inline-snapshot-pandas)
[![PyPI - Downloads](https://img.shields.io/pypi/dw/inline-snapshot-pandas)](https://pypacktrends.com/?packages=inline-snapshot-pandas&time_range=2years)
[![coverage](https://img.shields.io/badge/coverage-100%25-blue)](https://15r10nk.github.io/inline-snapshot-pandas/latest/contributing/#coverage)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/15r10nk)](https://github.com/sponsors/15r10nk)

<!-- -8<- [end:Header] -->

Pandas integration for [inline-snapshot](https://github.com/15r10nk/inline-snapshot).

## Installation

This project is currently available to sponsors through the private insiders
repository:

```bash
pip install git+ssh://git@github.com/15r10nk-insiders/inline-snapshot-pandas.git@insiders
```

## Usage

The package provides snapshot-aware versions of Pandas' equality assertions:

```python
from inline_snapshot import snapshot
from inline_snapshot_pandas import assert_frame_equal
from pandas import DataFrame


def test_frame():
    assert_frame_equal(DataFrame({"score": [5, 6]}), snapshot())
```

Create the missing inline snapshot with:

```bash
pytest --inline-snapshot=create
```

The available helpers are `assert_frame_equal`, `assert_series_equal`, and
`assert_index_equal`. Alternatively, call `setup()` from `conftest.py` to patch
the corresponding functions in `pandas.testing`:

```python
from inline_snapshot_pandas import setup

setup()
```

Pandas objects can also be stored in external, human-readable `.pandas.json`
snapshot files:

```python
from inline_snapshot import external
from inline_snapshot_pandas import assert_frame_equal
from pandas import DataFrame


def test_frame():
    assert_frame_equal(DataFrame({"score": [5, 6]}), external())
```

Create the external snapshot with `pytest --inline-snapshot=create`. DataFrames,
Series, regular indices, range indices, and multi-indices are supported. Reports
show changed, inserted, and deleted labeled values instead of a binary diff.

<!-- -8<- [start:Feedback] -->

## Issues

If you encounter any problems, please [report an issue](https://github.com/15r10nk/inline-snapshot-pandas/issues) along with a detailed description.

<!-- -8<- [end:Feedback] -->

## License

Distributed under the terms of the [MIT](http://opensource.org/licenses/MIT)
license, `inline-snapshot-pandas` is free and open source software.
