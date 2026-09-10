from pathlib import Path

import pytest

from bluewater.config import LocaleGuardConfig
from bluewater.locale_guard import LocaleGuardError, command


def test_missing_locale_guard_is_error(tmp_path: Path) -> None:
    with pytest.raises(LocaleGuardError):
        command(tmp_path, LocaleGuardConfig(), "check")
