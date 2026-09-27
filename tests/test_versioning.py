from bluewater.versioning import satisfies


def test_current_development_version_satisfies_foundation_range() -> None:
    ok, _ = satisfies(">=1.0.0.dev0,<2.0")
    assert ok


def test_incompatible_version_fails() -> None:
    ok, detail = satisfies(">=2.0")
    assert not ok
    assert "does not satisfy" in detail


def test_invalid_constraint_fails_closed() -> None:
    ok, detail = satisfies("not-a-version-range")
    assert not ok
    assert "invalid" in detail.lower()
