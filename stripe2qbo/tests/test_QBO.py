from typing import Dict, cast
from datetime import datetime
import os

from dotenv import load_dotenv
import pytest
import stripe

from stripe2qbo.db.schemas import Settings
from stripe2qbo.qbo.QBO import QBO
from stripe2qbo.qbo.models import ProductItemRef, QBOCurrency, TaxCode
from stripe2qbo.stripe.stripe_transactions import build_transaction, get_transaction
from stripe2qbo.transforms import (
    expense_from_transaction,
    qbo_invoice_from_stripe_invoice,
)

load_dotenv()

stripe.api_key = os.getenv("TEST_STRIPE_API_KEY", "")
ACCOUNT_ID = os.getenv("TEST_STRIPE_ACCOUNT_ID", "")


@pytest.fixture
def test_qbo(test_token) -> QBO:
    qbo = QBO()
    qbo.set_token(test_token)
    assert qbo.access_token is not None
    assert qbo.realm_id is not None
    return qbo


def test_qbo_request(test_qbo: QBO, test_token):
    response = test_qbo._request(
        path=f"/companyinfo/{test_token.realm_id}",
    )

    assert response.status_code == 200
    assert response.json()["CompanyInfo"]["CompanyName"] is not None
    assert response.json()["CompanyInfo"]["Country"] is not None


def test_create_expense(test_qbo: QBO, test_customer, test_settings):
    stripe.Charge.create(
        amount=1000,
        currency="usd",
        customer=test_customer.id,
        stripe_account=ACCOUNT_ID,
    )
    txn = stripe.BalanceTransaction.list(
        limit=1,
        type="charge",
        stripe_account=ACCOUNT_ID,
        expand=["data.source", "data.source.customer"],
    ).data[0]
    transaction = build_transaction(txn, ACCOUNT_ID)
    expense = expense_from_transaction(transaction, test_settings)

    expense_id = test_qbo.create_expense(expense)

    response = test_qbo._request(path=f"/purchase/{expense_id}")

    assert response.status_code == 200
    assert response.json()["Purchase"]["Id"] == expense_id
    assert response.json()["Purchase"]["TxnDate"] == datetime.fromtimestamp(
        transaction.created
    ).strftime("%Y-%m-%d")
    assert response.json()["Purchase"]["TotalAmt"] == transaction.fee / 100
    assert (
        response.json()["Purchase"]["EntityRef"]["value"]
        == test_settings.stripe_vendor_id
    )
    assert (
        response.json()["Purchase"]["AccountRef"]["value"]
        == test_settings.stripe_clearing_account_id
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
