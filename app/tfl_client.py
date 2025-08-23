from __future__ import annotations

from typing import Final

import requests

BASE_URL: Final[str] = "https://api.tfl.gov.uk/Line"


def fetch_disruptions(lines: str) -> str:
    """Fetch disruptions for the given tube line IDs from TfL API.

    Args:
        lines: Comma-separated tube line IDs (e.g., "victoria,central").

    Returns:
        str: The raw JSON-encoded payload returned by the TfL API.

    Raises:
        requests.HTTPError: If the TfL API returns a non-success status code.
        requests.RequestException: For other network-level failures.
    """
    url = f"{BASE_URL}/{lines}/Disruption"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text
