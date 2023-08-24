import os
import stripe

from src.qbo.qbo import query
from src.settings import settings

from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")


def get_stripe_balances():
    results = stripe.Balance.retrieve()
    return results


def get_qbo_balance():
    response = query(
        f"select * from Account where Name = '{settings.STRIPE_BANK_ACCOUNT}'"
    )
    accounts = response.json()["QueryResponse"].get("Account", [])

    if len(accounts) == 0:
        return None

    return (
        accounts[0]["CurrentBalanceWithSubAccounts"],
        accounts[0]["CurrencyRef"]["value"],
    )


if __name__ == "__main__":
    stripe_balances = get_stripe_balances()

    usd = 0
    cad = 0
    for balance in [*stripe_balances["available"], *stripe_balances["pending"]]:
        cad += balance["amount"] / 100 if balance["currency"] == "cad" else 0
        usd += balance["amount"] / 100 if balance["currency"] == "usd" else 0

    print("Stripe balances")
    print(f"USD: ${float(usd)}")
    print(f"CAD: ${float(cad)}")

    print("Quick books")
    qbo_balance = get_qbo_balance()
    if qbo_balance is not None:
        print(f"{qbo_balance[1]}: ${float(qbo_balance[0])}")
