from typing import Any, Optional, Mapping
import os
import json
import requests
from dotenv import load_dotenv

from src.qbo.qbo_auth import login


load_dotenv()


def qbo_request(
    path: str,
    body: Optional[Mapping[str, Any]] = None,
    method: str = "GET",
) -> requests.Response:
    token = login()

    try:
        response = requests.request(
            method,
            url=f"{os.getenv('QBO_BASE_URL', '')}/{token.realm_id}/{path}",
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
