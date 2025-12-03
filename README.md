# API Test Package

Pytest-based harness for running JSON-defined API tests.

## Prerequisites
- Python 3.10+ (uses modern typing)
- Pip; virtualenv optional but recommended

## Installation
```bash
pip install -r requirements.txt
```
If you use a virtual environment:
```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Project Layout
- `api_client.py` - thin wrapper over `requests` with retries/backoff and header merging.
- `auth.py` - optional helper to log in and fetch a token using environment variables.
- `validators.py` - assertion helpers (`exact`, `contains`) used by JSON test definitions.
- `test_loader.py` - loads `test_definition*.json` files into memory.
- `conftest.py` - session fixtures for a shared `ApiClient` and optional auth token handling.
- `test_api.py` - parameterized test that executes each JSON-defined case.
- `test_definition.json` - example test cases; add more `test_definition*.json` files as needed.

## How the Test Runner Works
1) Test cases are read from every `test_definition*.json` file in the repo root. Each file must contain a JSON array.  
2) Pytest parametrizes `test_api.py::test_api_endpoint` with those cases.  
3) For each case, an HTTP request is issued and the response JSON is validated via the chosen validators.  
4) Headers that contain `{{ACCESS_TOKEN}}` are replaced with a session token (see Auth below).

## JSON Test Case Schema
```json
{
  "name": "Readable test name",
  "request": {
    "method": "GET|POST|... (any requests verb)",
    "url": "https://example.com/api",
    "params": {"optional": "query string values"},
    "payload": {"optional": "json body"},
    "headers": {"Authorization": "Bearer {{ACCESS_TOKEN}}"}
  },
  "assertions": {
    "path.to.field": {"validator": "exact", "expected": "value"},
    "listField.1.description": {"validator": "contains", "expected": "substring"}
  }
}
```
- `assertions` keys are dot-separated paths into the response JSON; numeric segments index lists (e.g., `items.0.id`).
- Available validators: `exact` (equality) and `contains` (substring check on strings). Add more in `validators.py` as needed.

### How Validators Are Applied
- `test_api.py` iterates over each `assertions` entry and looks up the validator by name from `VALIDATORS` in `validators.py`.
- Each validator is a simple function that receives `(actual_value, expected_value)` and raises an assertion if the check fails.
- Current validators:
  - `exact` -> `validate_exact`: `actual == expected`
  - `contains` -> `validate_contains`: `expected` substring must be present in `actual` (string)
- Example from `test_definition.json`:
  - `"Name": {"validator": "exact", "expected": "Carbon credits"}` asserts the JSON field `Name` equals `"Carbon credits"`.
  - `"CanRelist": {"validator": "exact", "expected": true}` asserts `CanRelist` is `true`.
  - `"Promotions.1.Description": {"validator": "contains", "expected": "Good position in category"}` asserts the second promotion's description contains the provided substring.

## Auth and Tokens
- If any header uses `{{ACCESS_TOKEN}}`, the test session fetches a token once. Two options:
  1) Provide env vars (or a `.env` file): `LOGIN_URL`, `LOGIN_USERNAME`, `LOGIN_PASSWORD`. `auth.py` will log in and return a token from `access_token` or `token` in the response body.
  2) Include a login test case in your JSON with a URL that matches `/auth.*login/i`; its response must contain `accessToken` or `token`. The token is extracted and applied to subsequent requests.
- If no token placeholder is present, no auth is performed.

## Adding a New Test
1) Create or update a `test_definition*.json` file (e.g., `test_definition_users.json`).  
2) Append a JSON object following the schema above.  
3) Use unique, descriptive `name` values to make Pytest output readable.  
4) Choose validators that match the assertion type; add new ones in `validators.py` if needed.  
5) If the API requires auth, add the token placeholder in headers (`"Authorization": "Bearer {{ACCESS_TOKEN}}"`) and configure auth (see above).  
6) Run `pytest` and confirm the new case passes.

## Maintaining Tests
- Keep each JSON file as a list (`[...]`) and ensure it stays valid JSON.
- Prefer one domain/feature per `test_definition*.json` file to reduce merge conflicts.
- Re-run `pytest` after changes to catch schema or assertion mistakes.
- Extend `validators.py` instead of inlining assertion logic elsewhere to keep cases declarative.

## Running Tests
```bash
pytest
```
Pytest will discover `test_api.py` and automatically load every JSON-defined case.

## Current Test Cases
From `test_definition.json`:
- `Carbon credits category (GET)` - GET `https://api.tmsandbox.co.nz/v1/Categories/6327/Details.json?catalogue=false`; asserts name, relist flag, and promotion description.
