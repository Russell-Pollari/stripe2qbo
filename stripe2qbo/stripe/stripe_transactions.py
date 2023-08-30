from typing import List, Optional
import os
import stripe
from stripe2qbo.stripe.auth import get_token_from_file

from stripe2qbo.stripe.models import (
    Charge,
    Customer,
    Invoice,
    InvoiceLine,
    Payout,
    Product,
    Transaction,
)

from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")
token = get_token_from_file()
account_id = token.stripe_user_id if token is not None else ""


def get_transactions(
    from_timestamp: Optional[int] = None,
    to_timestamp: Optional[int] = None,
    transaction_type: Optional[str] = None,
    currency: Optional[str] = None,
    limit: Optional[int] = 100,
    starting_after: Optional[str] = None,
) -> List[Transaction]:
    transactions = []

    # TODO: paginatition when N > 100
    txns = stripe.BalanceTransaction.list(
        limit=limit,
        currency=currency,
        created={"gte": from_timestamp, "lte": to_timestamp},
        type=transaction_type,
        expand=[
            "data.source.customer",
            "data.source.invoice",
            "data.source.charge",
            "data.source",
        ],
        starting_after=starting_after,
        stripe_account=account_id,
    )

    for txn in txns:
        transaction = Transaction(**txn.to_dict())

        if transaction.type in ["charge", "payment"]:
            transaction.charge = Charge(**txn.source)
            if txn.source.customer:
                transaction.customer = Customer(**txn.source.customer)
            inv = txn.source.invoice
            if inv:
                lines: List[InvoiceLine] = []
                for line in inv.lines.data:
                    if line.plan:
                        product = stripe.Product.retrieve(
                            line.plan.product, stripe_account=account_id
                        )
                    elif line.price:
                        product = stripe.Product.retrieve(
                            line.price.product, stripe_account=account_id
                        )
                    else:
                        product = {"name": "Unknown"}
                    tax_amounts = []
                    for tax_amount in line.tax_amounts:
                        amt = tax_amount
                        amt.tax_rate = stripe.TaxRate.retrieve(
                            tax_amount.tax_rate, stripe_account=account_id
                        )
                        tax_amounts.append(amt)
                    line.tax_amounts = tax_amounts
                    line = InvoiceLine(**line, product=Product(**product))
                    lines.append(line)
                inv.lines = lines
                transaction.invoice = Invoice(**inv)

            transactions.append(transaction)
        elif transaction.type == "payout":
            transaction.payout = Payout(**txn.source)
            transactions.append(transaction)
        elif transaction.type == "stripe_fee":
            transactions.append(transaction)
        else:
            # TODO: handle refunds and other types
            print(f"Skipping transaction type {txn.type}")

    return transactions
