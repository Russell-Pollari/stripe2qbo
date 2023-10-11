from typing import Any, Optional, Mapping
import os
from dotenv import load_dotenv

import httpx
from httpx import Response

from stripe2qbo.exceptions import QBOException

load_dotenv()


async def qbo_request(
    path: str,
    method: str = "GET",
    body: Optional[Mapping[str, Any]] = None,
    access_token: str = "",
    realm_id: str = "",
) -> Response:
    if access_token == "":
        raise Exception("No access token provided")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method,
                url=f"{os.getenv('QBO_BASE_URL', '')}/{realm_id}/{path}",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                },
                json=body,
            )
        except Exception as e:
            raise Exception(f"Error making request: {e}")

    # TODO: get intuit_tid from response headers and log it
    if "Fault" in response.json():
        raise QBOException(response.json()["Fault"]["Error"][0]["Detail"])

    return response
