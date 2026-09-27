from __future__ import annotations

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import Version

from bluewater import __version__


def satisfies(constraint: str | None) -> tuple[bool, str]:
    if not constraint:
        return True, "no version constraint configured"
    try:
        specifier = SpecifierSet(constraint)
    except InvalidSpecifier as exc:
        return False, f"invalid Bluewater version constraint: {exc}"
    current = Version(__version__)
    ok = specifier.contains(current, prereleases=True)
    return ok, f"{current} {'satisfies' if ok else 'does not satisfy'} {constraint}"
