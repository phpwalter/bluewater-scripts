from importlib.resources import files
from pathlib import Path


def test_public_and_packaged_schema_match() -> None:
    root = Path(__file__).resolve().parents[1]
    public_schema = (root / "schemas" / "bluewater.schema.json").read_text(encoding="utf-8")
    packaged_schema = files("bluewater").joinpath("bluewater.schema.json").read_text(encoding="utf-8")
    assert public_schema == packaged_schema
