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
    currency = test_charge_transaction.currency.upper()
    date = datetime.fromtimestamp(test_charge_transaction.created).strftime("%Y-%m-%d")
    exchange_rate = test_qbo._request(
        path=f"/exchangerate?sourcecurrencycode={currency}&asofdate={date}"
    ).json()["ExchangeRate"]["Rate"]

    expense = expense_from_transaction(
        test_charge_transaction, test_settings, exchange_rate
    )
    expense_id = test_qbo.create_expense(expense)

    response = test_qbo._request(path=f"/purchase/{expense_id}")
    assert response.status_code == 200
    purchase = response.json()["Purchase"]

    assert purchase is not None
    assert purchase["Id"] == expense_id
    assert purchase["TxnDate"] == datetime.fromtimestamp(
        test_charge_transaction.created
    ).strftime("%Y-%m-%d")
    assert purchase["CurrencyRef"]["value"] == currency
    assert purchase["TotalAmt"] == test_charge_transaction.fee / 100

    if currency != test_qbo.home_currency:
        assert purchase["ExchangeRate"] == exchange_rate
    else:
        assert purchase["ExchangeRate"] == 1.0

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


def test_create_invoice(
    test_qbo: QBO, test_invoice_transaction: Transaction, test_settings: Settings
):
    assert test_invoice_transaction.invoice is not None
    assert test_invoice_transaction.invoice.due_date is not None
    assert test_invoice_transaction.customer is not None
    assert test_invoice_transaction.customer.name is not None

    currency = cast(QBOCurrency, test_invoice_transaction.invoice.currency.upper())
    customer = test_qbo.get_or_create_customer(
        test_invoice_transaction.customer.name, currency
    )

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

    invoice_body = qbo_invoice_from_stripe_invoice(
        test_invoice_transaction.invoice, customer.Id, tax_codes, test_settings
    )

    for line in invoice_body.Line:
        product = line.SalesItemLineDetail.ItemRef
        if product.value is None and product.name is not None:
            income_account_id = test_qbo.get_or_create_account(product.name, "Income")
            line.SalesItemLineDetail.ItemRef = cast(
                ProductItemRef,
                test_qbo.get_or_create_item(product.name, income_account_id),
            )

    invoice_id = test_qbo.create_invoice(invoice_body)

    assert invoice_id is not None

    response = test_qbo._request(path=f"/invoice/{invoice_id}")

    assert response.status_code == 200

    invoice = response.json()["Invoice"]

    assert invoice is not None
    assert invoice["Id"] == invoice_id
    assert invoice["CustomerRef"]["value"] == customer.Id
    assert invoice["CurrencyRef"]["value"] == currency
    assert invoice["TotalAmt"] == test_invoice_transaction.invoice.amount_due / 100
    assert invoice["DocNumber"] == test_invoice_transaction.invoice.number
    assert invoice["TxnDate"] == datetime.fromtimestamp(
        test_invoice_transaction.created
    ).strftime("%Y-%m-%d")
    assert invoice["DueDate"] == datetime.fromtimestamp(
        test_invoice_transaction.invoice.due_date
    ).strftime("%Y-%m-%d")
    assert (
        invoice["PrivateNote"]
        == f"{test_invoice_transaction.invoice.number}\n{test_invoice_transaction.invoice.id}"  # noqa
    )
    assert len(invoice["Line"]) == len(test_invoice_transaction.invoice.lines) + 1
