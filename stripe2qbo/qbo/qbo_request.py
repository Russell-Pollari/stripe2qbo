from typing import Any, Optional, Mapping
import os
import json
from dotenv import load_dotenv

import requests

load_dotenv()


def qbo_request(
    path: str,
    method: str = "GET",
    body: Optional[Mapping[str, Any]] = None,
    access_token: str = "",
    realm_id: str = "",
) -> requests.Response:
    if access_token == "":
        raise Exception("No access token provided")

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
        raise Exception(f"Error making request: {response.json()}")

    return response
