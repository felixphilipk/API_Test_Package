import os
import requests
import dotenv


# Load environment variables from .env (if present)
dotenv.load_dotenv()


def login_and_get_token() -> str:
    """Log in using environment variables and return an auth token.

    Expects `LOGIN_URL`, `LOGIN_USERNAME`, and `LOGIN_PASSWORD` to be provided via
    environment variables or a `.env` file. Raises a clear error if any are missing
    or if the HTTP request fails.
    """
    login_url = os.getenv("LOGIN_URL")
    username = os.getenv("LOGIN_USERNAME")
    password = os.getenv("LOGIN_PASSWORD")
    if not login_url:
        raise RuntimeError("Missing configuration: LOGIN_URL must be set as an environment variable or in a .env file")
    if not username:
        raise RuntimeError("Missing configuration: LOGIN_USERNAME must be set as an environment variable or in a .env file")
    if not password:
        raise RuntimeError("Missing configuration: LOGIN_PASSWORD must be set as an environment variable or in a .env file")

    # Perform the request and wrap network errors for clarity
    try:
        response = requests.post(
            login_url, 
            json={"username": username, 
                  "password": password}, 
                  timeout=10
                )
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Failed to contact login URL '{login_url}': {exc}") from exc

    # Parse token from common fields
    data = response.json()
    token = data.get("access_token") or data.get("token")
    if not token:
        raise ValueError("Authentication response did not contain 'access_token' or 'token'")
    return token
