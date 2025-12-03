from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def load_test_cases() -> List[Dict[str, Any]]:
    """Load all test case definitions from JSON files in this directory."""
    base = Path(__file__).parent
    files = sorted(base.glob("test_definition*.json"))
    if not files:
        default = base / "test_definitions.json"
        if default.exists():
            files = [default]

    test_cases: List[Dict[str, Any]] = []
    for fp in files:
        with fp.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError(
                f"Test definitions file {fp} does not contain a list of test cases"
            )
        test_cases.extend(data)
    return test_cases
