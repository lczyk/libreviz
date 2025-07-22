from src.boxes.colors import _ij2other


def test_ij2other() -> None:
    # up and to the right
    other = _ij2other((0, 0), (3, 0), (0, 3))
    assert other == [(3, 1), (3, 2), (3, 3)]

    other = _ij2other((0, 0), (0, 3), (3, 0))
    assert other == [(1, 3), (2, 3), (3, 3)]

    # down and to the right
    other = _ij2other((10, 10), (13, 10), (10, 7))
    assert other == [(13, 9), (13, 8), (13, 7)]

    other = _ij2other((10, 10), (10, 7), (13, 10))
    print(other)
