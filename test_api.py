from __future__ import annotations

from typing import Any, Dict

import pytest
from api_client import ApiClient
from test_loader import load_test_cases
from validators import VALIDATORS, get_nested


TEST_CASES = load_test_cases()


def _apply_access_token(headers: Dict[str, Any] | None, session_token: str | None) -> Dict[str, Any] | None:
    """Replace token placeholders using a session-scoped token from fixtures."""
    if not headers:
        return None
    resolved = dict(headers)
    for header, value in (resolved.items()):
        if isinstance(value, str) and "{{ACCESS_TOKEN}}" in value:
            if not session_token:
                raise RuntimeError("ACCESS_TOKEN placeholder found but no session token is available")
            resolved[header] = value.replace("{{ACCESS_TOKEN}}", session_token)
    return resolved

@pytest.mark.parametrize(
    "test_case",
    TEST_CASES,
    ids=lambda case: case.get("name", "Unnamed test case"),
)
def test_api_endpoint(
    api_client: ApiClient, session_token: str | None, test_case: Dict[str, Any]
) -> None:
    req = test_case["request"]
    headers = _apply_access_token(req.get("headers"), session_token)

    response_data = api_client.request(
        method=req["method"],
        endpoint=req["url"],
        params=req.get("params"),
        payload=req.get("payload"),
        headers=headers,
    )

    for path, assertion in test_case.get("assertions", {}).items():
        actual_value = get_nested(response_data, path)
        validator_name =  assertion["validator"]
        expected = assertion["expected"]
        validator_fn = VALIDATORS[validator_name]
        validator_fn(actual_value, expected)
