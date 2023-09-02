import os
import pytest
import stripe

from dotenv import load_dotenv

stripe.api_key = os.getenv("TEST_STRIPE_API_KEY", "")
ACCOUNT_ID = os.getenv("TEST_STRIPE_ACCOUNT_ID", "")

load_dotenv()


@pytest.fixture
def test_customer():
    stripe_customer = stripe.Customer.create(
        email="test@example.com",
        name="Test Customer",
        source="tok_visa",
        stripe_account=ACCOUNT_ID,
    )

    yield stripe_customer

    stripe.Customer.delete(stripe_customer.id, stripe_account=ACCOUNT_ID)
