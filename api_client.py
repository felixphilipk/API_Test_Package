from typing import Any, Dict, Optional
from time import sleep
import requests
from requests import exceptions as req_exc


class ApiClient:

    def __init__(
        self,
        base_url: str = "",
        default_headers: Optional[Dict[str, str]] = None,
        max_retries: int = 2,
        backoff_factor: float = 0.5,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {}
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 15,
    ) -> Dict[str, Any]:
        method = method.upper()
        if self.base_url and not endpoint.startswith("http"):
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
        else:
            url = endpoint

        # Normalize params so bools become lowercase strings (many APIs expect "true"/"false")
        normalized_params: Optional[Dict[str, Any]]
        if params is None:
            normalized_params = None
        else:
            normalized_params = {}
            for key, value in params.items():
                if isinstance(value, bool):
                    normalized_params[key] = str(value).lower()
                else:
                    normalized_params[key] = value

        # Merge default headers with per-request headers without mutating caller dict
        merged_headers = dict(self.default_headers) if self.default_headers is not None else {}
        if headers:
            merged_headers.update(headers)

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    params=normalized_params,
                    json=payload,
                    headers=merged_headers,
                    timeout=timeout,
                )
                response.raise_for_status()
                return response.json()
            except (req_exc.Timeout, req_exc.ConnectionError) as exc:
                last_error = exc
            except req_exc.HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else None
                # Retry 5xx responses as they are often transient server errors
                if status is not None and status >= 500:
                    last_error = exc
                else:
                    raise

            if attempt < self.max_retries:
                sleep(self.backoff_factor * (2 ** attempt))

        if last_error:
            raise last_error
        raise RuntimeError("Request failed without raising an exception")
