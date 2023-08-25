from typing import Optional
import os
import sys
import datetime
import json

from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from pydantic import BaseModel


class Token(BaseModel):
    realm_id: str  # company id
    access_token: str
    expires_at: str
    refresh_token: str
    refresh_token_expires_at: str


def logout() -> None:
    if os.path.exists("token.json"):
        os.remove("token.json")


def get_token() -> Optional[Token]:
    if not os.path.exists("token.json"):
        return None

    with open("token.json", "r") as f:
        content = f.read()
        token = json.loads(content)

    return Token(**token)


def save_token(auth_client: AuthClient, realm_id: str) -> Token:
    assert auth_client.access_token is not None
    assert auth_client.refresh_token is not None
    assert auth_client.x_refresh_token_expires_in is not None
    assert auth_client.expires_in is not None

    token = Token(
        access_token=auth_client.access_token,
        refresh_token=auth_client.refresh_token,
        refresh_token_expires_at=(
            datetime.datetime.now()
            + datetime.timedelta(seconds=auth_client.x_refresh_token_expires_in)
        ).isoformat(),
        expires_at=(
            datetime.datetime.now() + datetime.timedelta(seconds=auth_client.expires_in)
        ).isoformat(),
        realm_id=realm_id,
    )

    with open("token.json", "w") as f:
        f.write(json.dumps(token.model_dump(), indent=2))

    return token


def login() -> Token:
    token = get_token()

    if (
        token is not None
        and datetime.datetime.fromisoformat(token.expires_at) > datetime.datetime.now()
    ):
        return token

    auth_client = AuthClient(
        client_id=os.getenv("QBO_CLIENT_ID"),
        client_secret=os.getenv("QBO_CLIENT_SECRET"),
        redirect_uri=os.getenv("QBO_REDIRECT_URI"),
        environment="sandbox",  # TODO: env variable
    )

    if (
        token is not None
        and datetime.datetime.fromisoformat(token.refresh_token_expires_at)
        > datetime.datetime.now()
    ):
        print("Refreshing token")
        auth_client.refresh(refresh_token=token.refresh_token)
        return save_token(auth_client, token.realm_id)

    url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
    print(url)
    url = input("After authorizing, past the url here ")
    code = url.split("code=")[1].split("&")[0]
    realm_id = url.split("realmId=")[1].split("&")[0]
    token = get_auth_token(code, realm_id)
    return token


def get_auth_url() -> str:
    auth_client = AuthClient(
        client_id=os.getenv("QBO_CLIENT_ID"),
        client_secret=os.getenv("QBO_CLIENT_SECRET"),
        redirect_uri=os.getenv("QBO_REDIRECT_URI"),
        environment="sandbox",  # TODO: env variable
    )

    return auth_client.get_authorization_url([Scopes.ACCOUNTING])


def get_auth_token(code: str, realm_id: str) -> Token:
    auth_client = AuthClient(
        client_id=os.getenv("QBO_CLIENT_ID"),
        client_secret=os.getenv("QBO_CLIENT_SECRET"),
        redirect_uri=os.getenv("QBO_REDIRECT_URI"),
        environment="sandbox",  # TODO: env variable
    )
    auth_client.get_bearer_token(code)
    token = save_token(auth_client, realm_id)
    return Token(**token.model_dump())


if __name__ == "__main__":
    command = sys.argv[1]
    if command == "logout":
        logout()
        print("Logged out of QBO")
    elif command == "login":
        token = login()
        print("Logged into QBO as company", token.realm_id)
