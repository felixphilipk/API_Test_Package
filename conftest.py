import os
import re
from typing import Any, Dict, Iterable, Optional

import pytest

from api_client import ApiClient
from auth import login_and_get_token
from test_loader import load_test_cases


def _find_login_test_case(test_cases: Iterable[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Locate a login test case once so auth handling is centralized."""
    for case in test_cases:
        if not isinstance(case, dict):
            continue
        request = case.get("request", {})
        if isinstance(request, dict) and re.search(
            r"auth.*login", request.get("url", ""), re.IGNORECASE
        ):
            return case
    return None


def _requires_access_token(test_cases: Iterable[Dict[str, Any]]) -> bool:
    """Return True if any test case uses an ACCESS_TOKEN placeholder."""
    for case in test_cases:
        request = case.get("request", {})
        headers = (request.get("headers") or {}) if isinstance(request, dict) else {}
        for value in headers.values():
            if isinstance(value, str) and "{{ACCESS_TOKEN}}" in value:
                return True
    return False


@pytest.fixture(scope="session")
def session_token() -> Optional[str]:
    """Resolve an access token once per session for consistent headers."""
    test_cases = load_test_cases()
    if not _requires_access_token(test_cases):
        return None

    if os.getenv("LOGIN_URL"):
        return login_and_get_token()

    login_case = _find_login_test_case(test_cases)
    if not login_case:
        raise RuntimeError(
            "ACCESS_TOKEN placeholder found but no login configuration or login test case is available"
        )

    client = ApiClient()
    req = login_case["request"]
    response = client.request(
        method=req["method"],
        endpoint=req["url"],
        params=req.get("params"),
        payload=req.get("payload"),
        headers=req.get("headers"),
    )
    token = response.get("accessToken") or response.get("token")
    if not token:
        raise RuntimeError("Failed to obtain access token from login test case response")
    return token


@pytest.fixture(scope="session")
def api_client(session_token: Optional[str]) -> ApiClient:
    # Keep client header-agnostic; token application is handled per-request in tests
    return ApiClient()
