from typing import Optional
import argparse
from datetime import datetime

from dotenv import load_dotenv

from src.stripe_transactions import get_transactions
from src.sync import sync_transaction
from src.qbo.qbo_auth import logout


load_dotenv()


args = argparse.ArgumentParser()

args.add_argument(
    "command",
    choices=["sync", "logout"],
    help="Command to run ('sync', 'logout')",
)

args.add_argument(
    "--from_date",
    help="From date (YYYY-MM-DD)",
    default="2023-01-01",
    required=False,
)
args.add_argument("--to_date", help="To date (YYYY--DD)", default=None, required=False)
args.add_argument("--type", help="Type of transaction", default=None, required=False)
args.add_argument(
    "--currency", help="Currency of transactions", default=None, required=False
)


def _str_to_timestamp(date_string: str) -> int:
    return int(datetime.strptime(date_string, "%Y-%m-%d").timestamp())


def sync(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    transaction_type: Optional[str] = None,
    currency: Optional[str] = None,
):
    from_timestamp = _str_to_timestamp(from_date) if from_date else None
    to_timestamp = _str_to_timestamp(to_date) if to_date else None

    starting_after = None  # for pagination
    while True:
        transactions = get_transactions(
            from_timestamp,
            to_timestamp,
            transaction_type=transaction_type,
            currency=currency,
            starting_after=starting_after,
        )

        if (len(transactions)) == 0:
            print("Done syncing")
            break

        print("Syncing", len(transactions), "transactions..")
        for transaction in transactions:
            sync_transaction(transaction)

        starting_after = transactions[-1].id
    pass


if __name__ == "__main__":
    args = args.parse_args()

    # TODO: if no currency is specified, check QBO settings for multicurrency
    # TODO get and validate settings (e.g. if tax is enables or required)
    #
    if args.command == "sync":
        sync(
            from_date=args.from_date,
            to_date=args.to_date,
            transaction_type=args.type,
            currency=args.currency,
        )

    if args.command == "logout":
        logout()
