from __future__ import annotations
from typing import Any, Callable, Dict, Iterable


def get_nested(data: Dict[str, Any], path: str) -> Any:
    """Retrieve a value from a nested dictionary using a dot-separated path.

    Args:
        data: The dictionary to retrieve the value from.
    """
    current: Any = data
    keys: Iterable[str] = path.split(".")
    for key in keys:
        if isinstance(current, list) and key.isdigit():
            idx = int(key)
            if 0 <= idx < len(current):
                current = current[idx]
            else:
                return None
        elif isinstance(current, dict):
            current = current.get(key)
        else:
            return None
    return current


def validate_exact(actual: Any, expected: Any) -> None:
    assert actual == expected, f"Expected '{expected}', but got '{actual}'"


def validate_contains(actual: Any, expected_substr: Any) -> None:
    assert (
        isinstance(actual, str) and expected_substr in actual
    ), f"Expected '{actual}' to contain '{expected_substr}'"

VALIDATORS: Dict[str, Callable[[Any, Any], None]] = {
    "exact": validate_exact,
    "contains": validate_contains,
}
