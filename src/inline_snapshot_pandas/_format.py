from difflib import SequenceMatcher
from pathlib import Path
from typing import Union

import pandas
from inline_snapshot import Format, register_format
from rich.text import Text

from ._pandas import PandasValue


def _value_repr(value: object) -> str:
    item = getattr(value, "item", None)
    if item is not None:
        value = item()
    return repr(value)


def _entries(value: pandas.DataFrame) -> list[tuple[str, str]]:
    return [
        (f"({index!r}, {column!r})", _value_repr(value.iloc[row, col]))
        for row, index in enumerate(value.index)
        for col, column in enumerate(value.columns)
    ]


def _metadata(value: pandas.DataFrame) -> tuple[object, ...]:
    return value.shape, tuple(map(str, value.dtypes))


def _pandas_text(value: pandas.DataFrame) -> str:
    return f"DataFrame:\n{value.to_string()}"


def _pandas_diff(original: pandas.DataFrame, new: pandas.DataFrame) -> Text:
    result = Text()

    def add_line(*parts: tuple[str, str]) -> None:
        if result:
            result.append("\n")
        for text, style in parts:
            result.append(text, style)

    if _metadata(original) != _metadata(new):
        add_line((f"- DataFrame: {_metadata(original)!r}", "red"))
        add_line((f"+ DataFrame: {_metadata(new)!r}", "green"))

    original_entries = _entries(original)
    new_entries = _entries(new)
    for operation, old_start, old_end, new_start, new_end in SequenceMatcher(
        None, original_entries, new_entries, autojunk=False
    ).get_opcodes():
        if operation == "equal":
            continue
        if operation == "replace":
            changed = min(old_end - old_start, new_end - new_start)
            for offset in range(changed):
                old_location, old_value = original_entries[old_start + offset]
                new_location, new_value = new_entries[new_start + offset]
                location = (
                    old_location
                    if old_location == new_location
                    else f"{old_location} -> {new_location}"
                )
                add_line(
                    (f"~ {location}: ", "yellow"),
                    (old_value, "red"),
                    (" -> ", "yellow"),
                    (new_value, "green"),
                )
            old_start += changed
            new_start += changed
        for location, value in original_entries[old_start:old_end]:
            add_line((f"- {location}: {value}", "red"))
        for location, value in new_entries[new_start:new_end]:
            add_line((f"+ {location}: {value}", "green"))

    return result


@register_format
class PandasFormat(Format[pandas.DataFrame]):
    """Store Pandas DataFrames as Parquet files."""

    suffix = ".parquet"

    def is_format_for(self, value: object) -> bool:
        if isinstance(value, PandasValue):
            value = value.value
        return isinstance(value, pandas.DataFrame)

    def encode(self, value: Union[pandas.DataFrame, PandasValue], path: Path) -> None:
        if isinstance(value, PandasValue):
            value = value.value
        assert isinstance(value, pandas.DataFrame)
        value.to_parquet(path)

    def decode(self, path: Path) -> pandas.DataFrame:
        return pandas.read_parquet(path)

    def rich_show(self, path: Path) -> str:
        return _pandas_text(self.decode(path))

    def rich_diff(self, original: Path, new: Path) -> Text:
        return _pandas_diff(self.decode(original), self.decode(new))
