import os
import json
from datetime import datetime, timedelta

from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from pydantic import BaseModel


class Token(BaseModel):
    realm_id: str  # company id
    access_token: str
    expires_at: str
    refresh_token: str
    refresh_token_expires_at: str


def auth_client() -> AuthClient:
    return AuthClient(
        client_id=os.getenv("QBO_CLIENT_ID"),
        client_secret=os.getenv("QBO_CLIENT_SECRET"),
        redirect_uri=os.getenv("QBO_REDIRECT_URI"),
        environment="sandbox",  # TODO: env variable
    )


def create_token(auth_client: AuthClient, realm_id: str) -> Token:
    assert auth_client.access_token is not None
    assert auth_client.refresh_token is not None
    assert auth_client.x_refresh_token_expires_in is not None
    assert auth_client.expires_in is not None

    token = Token(
        access_token=auth_client.access_token,
        refresh_token=auth_client.refresh_token,
        refresh_token_expires_at=(
            datetime.now() + timedelta(seconds=auth_client.x_refresh_token_expires_in)
        ).isoformat(),
        expires_at=(
            datetime.now() + timedelta(seconds=auth_client.expires_in)
        ).isoformat(),
        realm_id=realm_id,
    )

    return token


def get_auth_url() -> str:
    client = auth_client()
    return client.get_authorization_url([Scopes.ACCOUNTING])


def generate_auth_token(code: str, realm_id: str) -> Token:
    client = auth_client()
    client.get_bearer_token(code)
    token = create_token(client, realm_id)
    save_token_to_file(token)
    return Token(**token.model_dump())


def refresh_auth_token(refresh_token: str, realm_id: str) -> Token:
    client = auth_client()
    client.refresh(refresh_token=refresh_token)
    token = create_token(client, realm_id)
    save_token_to_file(token)
    return Token(**token.model_dump())


# TODO: replace with simple SQL db
def get_token_from_file(path: str = "token.json") -> Token:
    with open(path, "r") as f:
        return Token(**json.load(f))


def save_token_to_file(token: Token, path: str = "token.json") -> None:
    with open(path, "w") as f:
        json.dump(token.model_dump(), f, indent=4)


def delete_token_file(path: str = "token.json") -> None:
    os.remove(path)
