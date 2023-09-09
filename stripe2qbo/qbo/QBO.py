from typing import Any, Optional, Mapping
from requests import Response

from stripe2qbo.qbo.auth import Token
from stripe2qbo.qbo.qbo_request import qbo_request
from stripe2qbo.qbo.models import (
    Customer,
    Expense,
    Invoice,
    ItemRef,
    Payment,
    QBOCurrency,
    TaxCode,
    Transfer,
)


class QBO:
    realm_id: str | None = None
    access_token: str | None = None
    home_currency: QBOCurrency | None = None
    using_sales_tax: bool = False

    def __init__(self, token: Optional[Token] = None) -> None:
        if token is not None:
            self.set_token(token)

    def set_token(self, token: Token) -> None:
        self.realm_id = token.realm_id
        self.access_token = token.access_token
        self._set_preferences()

    def _request(
        self, path: str, method: str = "GET", body: Optional[Mapping[str, Any]] = None
    ) -> Response:
        if self.access_token is None or self.realm_id is None:
            raise Exception("QBO token not set")

        response = qbo_request(
            path=path,
            method=method,
            body=body,
            access_token=self.access_token,
            realm_id=self.realm_id,
        )
        return response

    def _query(self, query: str) -> Response:
        response = self._request(f"/query?query={query}")
        if "QueryResponse" not in response.json():
            raise Exception(f"Query failed: {response.json()}")
        return response

    def _set_preferences(self) -> None:
        response = self._request(path="/preferences")
        currency_prefs = response.json()["Preferences"]["CurrencyPrefs"]
        tax_prefs = response.json()["Preferences"]["TaxPrefs"]

        self.home_currency = currency_prefs["HomeCurrency"]["value"]
        self.using_sales_tax = tax_prefs["UsingSalesTax"]

    def get_exchange_rate(self, currency: QBOCurrency, date: str) -> float:
        if self.home_currency == currency:
            return 1.0

        response = self._request(
            path=f"/exchangerate?sourcecurrencycode={currency}&asofdate={date}"
        )
        return response.json()["ExchangeRate"]["Rate"]

    def get_tax_code(self, tax_code_id: str) -> Optional[TaxCode]:
        response = self._query(f"select * from TaxCode where Id = '{tax_code_id}'")
        tax_codes = response.json()["QueryResponse"].get("TaxCode", [])
        if len(tax_codes) == 0:
            return None
        else:
            return TaxCode(**tax_codes[0])

    def get_or_create_vendor(
        self, vendor_name: str, currency: Optional[QBOCurrency] = None
    ) -> str:
        if currency is None:
            currency = self.home_currency

        response = self._query(
            f"select * from Vendor where DisplayName = '{vendor_name}'"
        )
        vendors = response.json()["QueryResponse"].get("Vendor", [])
        if len(vendors) > 0:
            if vendors[0]["CurrencyRef"]["value"] != currency:
                # if already exists with different currency, create a new one
                return self.get_or_create_vendor(
                    f"{vendor_name} ({currency})", currency
                )
            else:
                return vendors[0]["Id"]

        response = self._request(
            path="vendor",
            method="POST",
            body={
                "DisplayName": vendor_name,
                "CurrencyRef": {
                    "value": currency or self.home_currency,
                },
            },
        )
        return response.json()["Vendor"]["Id"]

    def get_customer_by_name(self, customer_name: str) -> Optional[Customer]:
        response = self._query(
            f"select * from Customer where DisplayName = '{customer_name}'"
        )
        customers = response.json()["QueryResponse"].get("Customer", [])
        if len(customers) == 0:
            return None
        else:
            return Customer(**customers[0])

    def create_customer(self, customer_name: str, currency: QBOCurrency) -> Customer:
        response = self._request(
            path="customer",
            method="POST",
            body={
                "DisplayName": customer_name,
                "CurrencyRef": {
                    "value": currency,
                },
            },
        )
        if "Customer" not in response.json():
            raise Exception(f"Error creating customer: {response.json()}")
        return Customer(**response.json()["Customer"])

    def get_or_create_customer(
        self, customer_name: str, currency: QBOCurrency
    ) -> Customer:
        customer = self.get_customer_by_name(customer_name)
        if customer is None:
            customer = self.create_customer(customer_name, currency)

        if customer.CurrencyRef.value != currency:
            # if already exists with different currency, create a new one
            return self.get_or_create_customer(
                f"{customer_name} ({currency})", currency
            )

        return customer

    def get_item_by_name(self, item_name: str) -> Optional[ItemRef]:
        response = self._query(f"select * from Item where Name = '{item_name}'")
        items = response.json()["QueryResponse"].get("Item", [])
        if len(items) == 0:
            return None

        return ItemRef(
            value=items[0]["Id"],
            name=items[0]["Name"],
        )

    def create_item(self, item_name: str, account_id: str) -> ItemRef:
        response = self._request(
            path="item",
            method="POST",
            body={
                "Name": item_name,
                "Type": "Service",
                "IncomeAccountRef": {
                    "value": account_id,
                },
            },
        )

        return ItemRef(
            value=response.json()["Item"]["Id"],
            name=response.json()["Item"]["Name"],
        )

    def get_or_create_item(self, item_name: str, account_id: str) -> ItemRef:
        item = self.get_item_by_name(item_name)
        if item is None:
            item = self.create_item(item_name, account_id)
        return item

    def create_account(
        self,
        account_name: str,
        account_type: str,
        account_sub_type: Optional[str] = None,
        currency: Optional[QBOCurrency] = None,
    ) -> str:
        body = {
            "Name": account_name,
            "AccountType": account_type,
            "CurrencyRef": {
                "value": currency or self.home_currency,
            },
        }
        if account_sub_type is not None:
            body["AccountSubType"] = account_sub_type
        response = self._request(path="/account", body=body, method="POST")
        return response.json()["Account"]["Id"]

    def get_account_id(
        self, account_name: str, currency: Optional[QBOCurrency] = None
    ) -> Optional[str]:
        if currency is None:
            currency = self.home_currency

        response = self._query(f"select * from Account where Name = '{account_name}'")
        accounts = response.json()["QueryResponse"].get("Account", [])
        accounts = [
            account
            for account in accounts
            if account["CurrencyRef"]["value"] == currency
        ]
        if len(accounts) == 0:
            return None

        return accounts[0]["Id"]

    def get_or_create_account(
        self,
        account_name: str,
        account_type: str,
        account_sub_type: Optional[str] = None,
        currency: Optional[QBOCurrency] = None,
    ) -> str:
        if currency is None:
            currency = self.home_currency
        account_id = self.get_account_id(account_name, currency=currency)
        if account_id is not None:
            return account_id
        return self.create_account(
            account_name,
            account_type,
            currency=currency,
            account_sub_type=account_sub_type,
        )

    def create_invoice(self, invoice: Invoice) -> str:
        response = self._request(
            path="invoice",
            method="POST",
            body=invoice.model_dump(),
        )
        return response.json()["Invoice"]["Id"]

    def create_payment(
        self,
        payment: Payment,
    ) -> str:
        # TODO: Payment method?
        response = self._request(
            path="/payment", body=payment.model_dump(), method="POST"
        )
        return response.json()["Payment"]["Id"]

    def create_expense(self, expense: Expense) -> str:
        response = self._request(
            path="/purchase", body=expense.model_dump(), method="POST"
        )
        return response.json()["Purchase"]["Id"]

    def create_transfer(self, transfer: Transfer) -> str:
        response = self._request(
            path="/transfer", body=transfer.model_dump(), method="POST"
        )
        return response.json()["Transfer"]["Id"]
