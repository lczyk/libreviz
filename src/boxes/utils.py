from typing import TypeVar

_T = TypeVar("_T")


def bounce(p: tuple[_T, ...]) -> tuple[_T, ...]:
    return tuple(list(p) + list(reversed(p[1:-1])))
