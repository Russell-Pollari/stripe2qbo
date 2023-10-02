from typing import Optional, Literal
from pydantic import BaseModel


def _snake_to_camel(s: str) -> str:
    words = s.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])


class User(BaseModel):
    id: int
    email: str
    qbo_realm_id: Optional[str]
    stripe_user_id: Optional[str]


class Settings(BaseModel):
    stripe_clearing_account_id: str
    stripe_payout_account_id: str
    stripe_vendor_id: str
    stripe_fee_account_id: str
    default_income_account_id: str
    default_tax_code_id: str
    exempt_tax_code_id: str
    # product_settings: list[ProductSettings]
    # tax_settings: list[TaxSettings]

    model_config = {
        "alias_generator": _snake_to_camel,
        "populate_by_name": True,
        "from_attributes": True,
    }


class TransactionSync(BaseModel):
    id: str
    user_id: int
    created: int
    type: str
    amount: int
    fee: int
    currency: str
    description: str = ""
    stripe_id: str
    status: Literal["pending", "success", "syncing", "failed"] = "pending"
    failure_reason: Optional[str] = None
    # QBO ids
    transfer_id: Optional[str] = None
    invoice_id: Optional[str] = None
    payment_id: Optional[str] = None
    expense_id: Optional[str] = None
