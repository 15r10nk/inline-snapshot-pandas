import json
from difflib import SequenceMatcher
from io import StringIO
from pathlib import Path
from typing import Any, Union

import pandas
from inline_snapshot import Format, register_format
from rich.text import Text

from ._pandas import PandasValue

PandasObject = Union[pandas.DataFrame, pandas.Series, pandas.Index]


def _table(value: pandas.DataFrame, *, index: bool = True) -> Any:
    encoded = value.to_json(
        orient="table", date_format="iso", date_unit="ns", index=index
    )
    assert encoded is not None
    return json.loads(encoded)


def _from_table(value: Any) -> pandas.DataFrame:
    return pandas.read_json(StringIO(json.dumps(value)), orient="table")


def _encode(value: PandasObject) -> dict[str, Any]:
    if isinstance(value, pandas.DataFrame):
        return {"kind": "dataframe", "table": _table(value)}
    if isinstance(value, pandas.Series):
        return {
            "kind": "series",
            "name": value.name,
            "table": _table(value.to_frame(name="__value__")),
        }
    if isinstance(value, pandas.MultiIndex):
        return {
            "kind": "multiindex",
            "names": value.names,
            "table": _table(value.to_frame(index=False), index=False),
        }
    if isinstance(value, pandas.RangeIndex):
        return {
            "kind": "rangeindex",
            "name": value.name,
            "start": value.start,
            "stop": value.stop,
            "step": value.step,
        }
    assert isinstance(value, pandas.Index)
    return {
        "kind": "index",
        "name": value.name,
        "table": _table(
            pandas.Series(value.array, name="__value__").to_frame(), index=False
        ),
    }


def _decode(payload: dict[str, Any]) -> PandasObject:
    kind = payload["kind"]
    if kind == "dataframe":
        return _from_table(payload["table"])
    if kind == "series":
        result = _from_table(payload["table"])["__value__"]
        result.name = payload["name"]
        return result
    if kind == "multiindex":
        multiindex = pandas.MultiIndex.from_frame(_from_table(payload["table"]))
        multiindex.names = payload["names"]
        return multiindex
    if kind == "rangeindex":
        return pandas.RangeIndex(
            start=payload["start"],
            stop=payload["stop"],
            step=payload["step"],
            name=payload["name"],
        )
    assert kind == "index"
    values = _from_table(payload["table"])["__value__"]
    return pandas.Index(values.array, name=payload["name"])


def _value_repr(value: object) -> str:
    item = getattr(value, "item", None)
    if item is not None:
        value = item()
    return repr(value)


def _entries(value: PandasObject) -> list[tuple[str, str]]:
    if isinstance(value, pandas.DataFrame):
        return [
            (f"({index!r}, {column!r})", _value_repr(value.iloc[row, col]))
            for row, index in enumerate(value.index)
            for col, column in enumerate(value.columns)
        ]
    if isinstance(value, pandas.Series):
        return [
            (f"({index!r},)", _value_repr(item))
            for index, item in zip(value.index, value.array)
        ]
    return [
        (f"({position},)", _value_repr(item)) for position, item in enumerate(value)
    ]


def _metadata(value: PandasObject) -> tuple[object, ...]:
    if isinstance(value, pandas.DataFrame):
        return value.shape, tuple(map(str, value.dtypes))
    if isinstance(value, pandas.Series):
        return value.shape, str(value.dtype), value.name
    return value.shape, str(value.dtype), value.names


def _pandas_text(value: PandasObject) -> str:
    rendered = repr(value) if isinstance(value, pandas.Index) else value.to_string()
    return f"{type(value).__name__}:\n{rendered}"


def _pandas_diff(original: PandasObject, new: PandasObject) -> Text:
    result = Text()

    def add_line(*parts: tuple[str, str]) -> None:
        if result:
            result.append("\n")
        for text, style in parts:
            result.append(text, style)

    if type(original) is not type(new) or _metadata(original) != _metadata(new):
        add_line((f"- {type(original).__name__}: {_metadata(original)!r}", "red"))
        add_line((f"+ {type(new).__name__}: {_metadata(new)!r}", "green"))

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
class PandasFormat(Format[PandasObject]):
    """Store Pandas objects as non-pickled, human-readable JSON files."""

    suffix = ".pandas.json"

    def is_format_for(self, value: object) -> bool:
        return isinstance(
            value, (PandasValue, pandas.DataFrame, pandas.Series, pandas.Index)
        )

    def encode(self, value: Union[PandasObject, PandasValue], path: Path) -> None:
        if isinstance(value, PandasValue):
            value = value.value
        assert isinstance(value, (pandas.DataFrame, pandas.Series, pandas.Index))
        with path.open("w", encoding="utf-8", newline="\n") as file:
            json.dump(_encode(value), file, ensure_ascii=False, indent=2)
            file.write("\n")

    def decode(self, path: Path) -> PandasObject:
        with path.open(encoding="utf-8") as file:
            return _decode(json.load(file))

    def rich_show(self, path: Path) -> str:
        return _pandas_text(self.decode(path))

    def rich_diff(self, original: Path, new: Path) -> Text:
        return _pandas_diff(self.decode(original), self.decode(new))
