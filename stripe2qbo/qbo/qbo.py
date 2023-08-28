from typing import Literal, Optional, List
import datetime

import requests

from stripe2qbo.qbo.qbo_request import qbo_request
from stripe2qbo.qbo.models import (
    Customer,
    TaxCode,
    TaxDetail,
    ItemRef,
    InvoiceLine,
)


def query(query: str) -> requests.Response:
    response = qbo_request(f"/query?query={query}")
    if "QueryResponse" not in response.json():
        raise Exception(f"Query failed: {response.json()}")
    return response


def get_tax_code(tax_code_id: str) -> TaxCode:
    response = query(f"select * from TaxCode where Id = '{tax_code_id}'")
    tax_codes = response.json()["QueryResponse"].get("TaxCode", [])

    if len(tax_codes) == 0:
        raise Exception(f"Tax code {tax_code_id} not found")

    if len(tax_codes) > 1:
        raise Exception(f"Multiple tax codes found with {tax_code_id}")

    return TaxCode(**tax_codes[0])


def get_customer_by_name(customer_name: str) -> Optional[Customer]:
    response = query(f"select * from customer where DisplayName = '{customer_name}'")
    customers = response.json()["QueryResponse"].get("Customer", [])

    if len(customers) == 0:
        return None

    if len(customers) > 1:
        raise Exception(f"Multiple customers found with {customer_name}")

    return Customer(**customers[0])


def create_customer(customer_name: str, currency: Literal["USD", "CAD"]) -> Customer:
    body = {"DisplayName": customer_name, "CurrencyRef": {"value": currency}}
    response = qbo_request(path="/customer", body=body, method="POST")
    return Customer(**response.json()["Customer"])


def get_or_create_customer(
    customer_name: str, currency: Literal["USD", "CAD"]
) -> Customer:
    customer = get_customer_by_name(customer_name)

    if customer is None:
        return create_customer(customer_name, currency)

    if customer.CurrencyRef.value != currency:
        # if already exists with different currency, create a new one
        return create_customer(f"{customer_name} ({currency})", currency)

    return customer


def create_account(account_name: str, account_type: str) -> str:
    body = {
        "Name": account_name,
        "AccountType": account_type,
    }
    response = qbo_request(path="/account", body=body, method="POST")
    return response.json()["Account"]["Id"]


def get_account_id(account_name: str) -> Optional[str]:
    response = query(f"select * from Account where Name = '{account_name}'")
    accounts = response.json()["QueryResponse"].get("Account", [])

    if len(accounts) == 0:
        return None

    if len(accounts) > 1:
        raise Exception(f"Multiple accounts found with {account_name}")

    return accounts[0]["Id"]


# def get_account_by_id(account_id: str) -> Optional[str]:


def get_or_create_account(account_name: str, account_type: str) -> str:
    acount_id = get_account_id(account_name)
    if acount_id is not None:
        return acount_id
    return create_account(account_name, account_type)


def get_item_by_name(item_name: str) -> Optional[ItemRef]:
    response = query(f"select * from item where Name = '{item_name}'")
    items = response.json()["QueryResponse"].get("Item", [])

    if len(items) == 0:
        return None

    if len(items) > 1:
        raise Exception(f"Multiple items found with {item_name}")

    return ItemRef(
        value=items[0]["Id"],
        name=items[0]["Name"],
    )


def create_item(item_name: str, account_id: str) -> ItemRef:
    response = qbo_request(
        path="/item",
        body={
            "Name": item_name,
            "Type": "Service",
            "IncomeAccountRef": {"value": account_id},
        },
        method="POST",
    )
    item = response.json()["Item"]

    return ItemRef(
        value=item["Id"],
        name=item["Name"],
    )


def get_or_create_item(item_name: str, account_id) -> ItemRef:
    item = get_item_by_name(item_name)
    if item is None:
        item = create_item(item_name, account_id)
    return item


def create_invoice(
    customer_id: str,
    lines: List[InvoiceLine],
    created_date: Optional[datetime.datetime] = None,
    currency: Optional[Literal["USD", "CAD"]] = "USD",
    private_note: Optional[str] = "",
    due_date: Optional[datetime.datetime] = None,
    tax_detail: Optional[TaxDetail] = None,
    inv_number: Optional[str] = None,
) -> str:
    if len(lines) == 0:
        raise Exception("Invoice must have at least one line")

    body = {
        "CustomerRef": {"value": f"{customer_id}"},
        "Line": [lines.model_dump() for lines in lines],
        "CurrencyRef": {"value": currency},
        "PrivateNote": private_note,
        "TxnTaxDetail": tax_detail.model_dump() if tax_detail else None,
        "DocNumber": inv_number if inv_number else None,
    }

    if due_date:
        body["DueDate"] = due_date.strftime("%Y-%m-%d")
    if created_date:
        body["TxnDate"] = created_date.strftime("%Y-%m-%d")

    response = qbo_request(path="/invoice", body=body, method="POST")

    return response.json()["Invoice"]["Id"]


def get_vendor_by_name(vendor_name: str) -> Optional[str]:
    response = query(f"select * from Vendor where DisplayName = '{vendor_name}'")
    vendors = response.json()["QueryResponse"].get("Vendor", [])
    if len(vendors) == 0:
        return None

    if len(vendors) > 1:
        raise Exception(f"Multiple vendors found with {vendor_name}")

    return vendors[0]["Id"]


def create_vendor(vendor_name: str) -> str:
    vendor_id = get_vendor_by_name(vendor_name)

    if vendor_id is not None:
        return vendor_id

    body = {"DisplayName": vendor_name}
    response = qbo_request(path="/vendor", body=body, method="POST")
    return response.json()["Vendor"]["Id"]


def get_or_create_vendor(vendor_name: str) -> str:
    vendor_id = get_vendor_by_name(vendor_name)

    if vendor_id is not None:
        return vendor_id

    return create_vendor(vendor_name)


def create_invoice_payment(
    invoice_id: Optional[str],
    customer_id: str,
    amount: float,
    date: datetime.datetime,
    qbo_account_id: str,
    currency: Literal["USD", "CAD"],
    exchange_rate: Optional[float],
    private_note: str = "",
) -> str:
    # TODO: Payment method?

    body = {
        "TotalAmt": amount,
        "CustomerRef": {"value": customer_id},
        "TxnDate": date.strftime("%Y-%m-%d"),
        "DepositToAccountRef": {"value": qbo_account_id},
        "PrivateNote": private_note,
        "CurrencyRef": {"value": currency},
        "ExchangeRate": exchange_rate or "1",
    }

    if invoice_id:
        body["LINE"] = [
            {
                "Amount": amount,
                "LinkedTxn": [{"TxnId": invoice_id, "TxnType": "Invoice"}],
            }
        ]
    response = qbo_request(path="/payment", body=body, method="POST")

    return response.json()["Payment"]["Id"]


def create_expense(
    amount: float,
    date: datetime.datetime,
    bank_account_id: str,
    vendor_id: str,
    expense_account_id: str,
    private_note: str = "",
    description: str = "",
) -> str:
    body = {
        "TotalAmt": amount,
        "AccountRef": {"value": bank_account_id},
        "PaymentType": "Check",
        "Line": [
            {
                "Amount": amount,
                "DetailType": "AccountBasedExpenseLineDetail",
                "AccountBasedExpenseLineDetail": {
                    "AccountRef": {"value": expense_account_id},
                },
                "Description": description,
            }
        ],
        "EntityRef": {"value": vendor_id},
        "TxnDate": date.strftime("%Y-%m-%d"),
        "PrivateNote": private_note,
    }

    response = qbo_request(path="/purchase", body=body, method="POST")
    return response.json()["Purchase"]["Id"]


def create_transfer(
    amount: float,
    date: datetime.datetime,
    source_account_id: str,
    destination_account_id: str,
    private_note: str = "",
) -> str:
    body = {
        "Amount": amount,
        "FromAccountRef": {"value": source_account_id},
        "ToAccountRef": {"value": destination_account_id},
        "TxnDate": date.strftime("%Y-%m-%d"),
        "PrivateNote": private_note,
    }

    response = qbo_request(path="/transfer", body=body, method="POST")
    return response.json()["Transfer"]["Id"]
