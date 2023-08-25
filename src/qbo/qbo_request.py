from typing import Any, Optional, Mapping
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


def qbo_request(
    path: str,
    body: Optional[Mapping[str, Any]] = None,
    method: str = "GET",
    access_token: Optional[str] = None,
    realm_id: Optional[str] = None,
) -> requests.Response:
    try:
        response = requests.request(
            method,
            url=f"{os.getenv('QBO_BASE_URL', '')}/{realm_id}/{path}",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
            data=json.dumps(body),
        )
    except Exception as e:
        raise Exception(f"Error making request: {e}")

    # TODO: get intuit_tid from response headers and log it
    if "Fault" in response.json():
        raise Exception(f"Error making request: {response.json()['Fault']}")

    return response
