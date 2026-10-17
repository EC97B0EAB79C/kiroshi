import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TIMEOUT = 10

# Shared session: retry with backoff (1s, 2s, 4s) on network and server errors
session = requests.Session()
session.mount(
    "https://",
    HTTPAdapter(
        max_retries=Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=None,
        )
    ),
)


def request(method: str, url: str, **kwargs) -> requests.Response:
    """Send a request with timeout and retry. Raise on HTTP error."""
    response = session.request(method, url, timeout=TIMEOUT, **kwargs)
    response.raise_for_status()
    return response
