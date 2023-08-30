from typing import Any, Optional, Mapping
import os
import json
from dotenv import load_dotenv

import requests

from stripe2qbo.qbo.auth import get_token_from_file

load_dotenv()


def qbo_request(
    path: str,
    method: str = "GET",
    body: Optional[Mapping[str, Any]] = None,
    access_token: Optional[str] = None,
    realm_id: Optional[str] = None,
) -> requests.Response:
    token = get_token_from_file()

    if access_token is None and token is not None:
        access_token = token.access_token
    if realm_id is None and token is not None:
        realm_id = token.realm_id

    if access_token is None:
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
        raise Exception(f"Error making request: {response.json()['Fault']}")

    return response
