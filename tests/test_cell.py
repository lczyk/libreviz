from conftest import Subtests  # type: ignore[import-not-found]

from src.boxes import cell


def test_str_ij_conversion(subtests: Subtests) -> None:
    """Test that ij2str and str2ij work correctly."""
    test_cases = [
        ((0, 0), "A:1"),
        ((1, 0), "B:1"),
        ((0, 1), "A:2"),
        ((1, 1), "B:2"),
        ((25, 0), "Z:1"),
        ((26, 0), "AA:1"),
        ((0, 25), "A:26"),
    ]

    for ij, expected_str in test_cases:
        with subtests.test(ij=ij, expected_str=expected_str):
            assert cell.ij2str(ij) == expected_str
            assert cell.str2ij(expected_str) == ij
