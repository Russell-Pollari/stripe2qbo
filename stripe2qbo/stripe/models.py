from typing import Optional, List, Literal

from pydantic import BaseModel


class Product(BaseModel):
    name: str


class TaxRate(BaseModel):
    id: str
    percentage: float


class TaxAmount(BaseModel):
    amount: int
    taxable_amount: int
    tax_rate: Optional[TaxRate]


class InvoiceLine(BaseModel):
    id: str
    amount: int  # cents
    description: str
    quantity: int
    product: Product
    tax_amounts: List[TaxAmount] = []


class Invoice(BaseModel):
    id: str
    created: int  # timestamp
    due_date: Optional[int] = None
    amount_due: int  # cents
    currency: Literal["usd", "cad"]
    lines: List[InvoiceLine] = []
    tax: Optional[int] = None
    number: Optional[str] = None


class Charge(BaseModel):
    id: str
    amount: float  # cents
    created: int  # timestamp
    description: Optional[str]
    currency: Literal["usd", "cad"]


class Customer(BaseModel):
    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None


class Payout(BaseModel):
    id: str
    amount: int
    arrival_date: int  # timestamp
    created: int  # timestamp
    description: str


class Transaction(BaseModel):
    id: str
    created: int  # timestamp
    description: str = ""
    type: str
    amount: float  # cents
    fee: float
    exchange_rate: Optional[float]
    currency: Literal["usd", "cad"]
    charge: Optional[Charge] = None
    customer: Optional[Customer] = None
    invoice: Optional[Invoice] = None
    payout: Optional[Payout] = None


class BusinessProfile(BaseModel):
    name: Optional[str]


class Account(BaseModel):
    id: str
    country: str
    default_currency: str
