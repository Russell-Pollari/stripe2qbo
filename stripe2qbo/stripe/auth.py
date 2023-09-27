import os
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
        + f"&redirect_uri={os.getenv('STRIPE_REDIRECT_URI')}"
    )
    return url


def generate_auth_token(code: str) -> StripeToken:
    resp = stripe.OAuth.token(grant_type="authorization_code", code=code)
    stripe_token = StripeToken(stripe_user_id=resp["stripe_user_id"])
    return stripe_token
