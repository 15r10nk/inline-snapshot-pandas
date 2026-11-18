import importlib


def test_package_can_be_imported():
    assert importlib.import_module("inline_snapshot_pandas") is not None
