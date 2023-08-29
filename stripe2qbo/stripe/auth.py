import os
import json
from pydantic import BaseModel
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")


class StripeToken(BaseModel):
    stripe_user_id: str


def get_auth_url() -> str:
    url = (
        "https://connect.stripe.com/oauth/authorize?"
        + "&response_type=code&"
        + f"&client_id={os.getenv('STRIPE_CLIENT_ID')}"
        + "&scope=read_write"
    )
    return url


def generate_auth_token(code: str) -> StripeToken:
    resp = stripe.OAuth.token(grant_type="authorization_code", code=code)
    stripe_token = StripeToken(stripe_user_id=resp["stripe_user_id"])
    save_token_to_file(stripe_token)
    return stripe_token


# TODO: replace with simple SQL db
def get_token_from_file(path: str = "stripe_token.json") -> StripeToken:
    with open(path, "r") as f:
        return StripeToken(**json.load(f))


def save_token_to_file(token: StripeToken, path: str = "stripe_token.json") -> None:
    with open(path, "w") as f:
        json.dump(token.model_dump(), f, indent=4)


def delete_token_file(path: str = "stripe_token.json") -> None:
    os.remove(path)
