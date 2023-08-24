from typing import Any, Optional, Mapping
import json
import requests

from src.qbo.qbo_auth import login


# BASE_URL = "https://quickbooks.api.intuit.com/v3/company"
BASE_URL = "https://sandbox-quickbooks.api.intuit.com/v3/company"


def qbo_request(
    path: str,
    body: Optional[Mapping[str, Any]] = None,
    method: str = "GET",
) -> requests.Response:
    token = login()

    try:
        response = requests.request(
            method,
            url=f"{BASE_URL}/{token.realm_id}/{path}",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token.access_token}",
            },
            data=json.dumps(body),
        )
    except Exception as e:
        raise Exception(f"Error making request: {e}")

    # TODO: get intuit_tid from response headers and log it
    if "Fault" in response.json():
        raise Exception(f"Error making request: {response.json()['Fault']}")

    return response
