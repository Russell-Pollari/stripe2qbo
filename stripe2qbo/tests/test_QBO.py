from pprint import pprint
from typing import Dict, cast
from datetime import datetime
import os

from dotenv import load_dotenv
import stripe

from stripe2qbo.db.schemas import Settings
from stripe2qbo.qbo.auth import Token
from stripe2qbo.qbo.QBO import QBO
from stripe2qbo.qbo.models import ProductItemRef, QBOCurrency, TaxCode
from stripe2qbo.stripe.models import Transaction
from stripe2qbo.stripe.stripe_transactions import get_transaction
from stripe2qbo.transforms import (
    expense_from_transaction,
    qbo_invoice_from_stripe_invoice,
)

load_dotenv()

stripe.api_key = os.getenv("TEST_STRIPE_API_KEY", "")
ACCOUNT_ID = os.getenv("TEST_STRIPE_ACCOUNT_ID", "")


def test_qbo_request(test_qbo: QBO, test_token: Token):
    response = test_qbo._request(
        path=f"/companyinfo/{test_token.realm_id}",
    )

    assert response.status_code == 200
    assert response.json()["CompanyInfo"]["CompanyName"] is not None
    assert response.json()["CompanyInfo"]["Country"] is not None


def test_create_account(test_qbo: QBO):
    account_id = test_qbo.get_or_create_account("Test Expense Account", "Expense")

    response = test_qbo._request(path=f"/account/{account_id}")
    assert response.status_code == 200
    assert response.json()["Account"]["Id"] == account_id
    assert response.json()["Account"]["Name"] == "Test Expense Account"
    assert response.json()["Account"]["AccountType"] == "Expense"
    assert response.json()["Account"]["CurrencyRef"]["value"] == test_qbo.home_currency


def test_create_expense(
    test_qbo: QBO,
    test_settings: Settings,
    test_charge_transaction: Transaction,
):
    expense = expense_from_transaction(test_charge_transaction, test_settings)
    currency = test_charge_transaction.currency.upper()

    expense_id = test_qbo.create_expense(expense)

    response = test_qbo._request(path=f"/purchase/{expense_id}")
    assert response.status_code == 200
    purchase = response.json()["Purchase"]

    pprint(purchase)
    assert purchase is not None
    assert purchase["Id"] == expense_id
    assert purchase["TxnDate"] == datetime.fromtimestamp(
        test_charge_transaction.created
    ).strftime("%Y-%m-%d")
    assert purchase["CurrencyRef"]["value"] == currency
    assert purchase["TotalAmt"] == test_charge_transaction.fee / 100
    if currency == "USD":
        assert purchase["EntityRef"]["value"] == test_settings.stripe_vendor_id
        assert (
            purchase["AccountRef"]["value"] == test_settings.stripe_clearing_account_id
        )
    else:
        assert purchase["EntityRef"]["value"] == test_settings.stripe_vendor_id_cad
        assert (
            purchase["AccountRef"]["value"]
            == test_settings.stripe_clearing_account_id_cad
        )


def test_create_invoice(test_qbo: QBO, test_customer, test_settings: Settings):
    stripe.InvoiceItem.create(
        customer=test_customer.id,
        amount=1000,
        currency="usd",
        description="Product X cad",
        stripe_account=ACCOUNT_ID,
    )
    stripe.InvoiceItem.create(
        customer=test_customer.id,
        amount=500,
        currency="usd",
        description="Product Z cad",
        stripe_account=ACCOUNT_ID,
    )
    test_invoice = stripe.Invoice.create(
        customer=test_customer.id,
        stripe_account=ACCOUNT_ID,
        collection_method="send_invoice",
        currency="usd",
        days_until_due=30,
    )
    stripe.Invoice.pay(test_invoice.id, stripe_account=ACCOUNT_ID)
    txn = stripe.BalanceTransaction.list(limit=1, stripe_account=ACCOUNT_ID).data[0]

    transaction = get_transaction(txn.id, ACCOUNT_ID)
    assert transaction.invoice is not None
    assert transaction.customer is not None
    assert transaction.customer.name is not None

    currency = cast(QBOCurrency, transaction.invoice.currency.upper())
    customer = test_qbo.get_or_create_customer(transaction.customer.name, currency)

    tax_codes: Dict[str, TaxCode | None] = {}
    tax_codes[test_settings.default_tax_code_id] = (
        test_qbo.get_tax_code(test_settings.default_tax_code_id)
        if test_settings.default_tax_code_id != "TAX"
        else None
    )
    tax_codes[test_settings.exempt_tax_code_id] = (
        test_qbo.get_tax_code(test_settings.exempt_tax_code_id)
        if test_settings.exempt_tax_code_id != "NON"
        else None
    )

    invoice = qbo_invoice_from_stripe_invoice(
        transaction.invoice, customer.Id, tax_codes, test_settings
    )

    for line in invoice.Line:
        product = line.SalesItemLineDetail.ItemRef
        if product.value is None and product.name is not None:
            income_account_id = test_qbo.get_or_create_account(product.name, "Income")
            line.SalesItemLineDetail.ItemRef = cast(
                ProductItemRef,
                test_qbo.get_or_create_item(product.name, income_account_id),
            )

    invoice_id = test_qbo.create_invoice(invoice)

    assert invoice_id is not None
