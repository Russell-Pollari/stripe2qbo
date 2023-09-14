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
    currency: Literal[
        "aed",
        "afn",
        "all",
        "amd",
        "ang",
        "aoa",
        "ars",
        "aud",
        "awd",
        "azn",
        "bam",
        "bbd",
        "bdt",
        "bgn",
        "bif",
        "bmd",
        "bnd",
        "bob",
        "brl",
        "bsd",
        "btc",
        "btn",
        "bwp",
        "bws",
        "byn",
        "bzd",
        "cad",
        "cdf",
        "chf",
        "clp",
        "crc",
        "cup",
        "cve",
        "czk",
        "djf",
        "dkk",
        "dop",
        "dzd",
        "egp",
        "ern",
        "eur",
        "etb",
        "eth",
        "fjd",
        "fkp",
        "gbp",
        "gel",
        "ghs",
        "gip",
        "gmd",
        "gnd",
        "gtq",
        "gyd",
        "hkd",
        "hnl",
        "htg",
        "huf",
        "idr",
        "ils",
        "inr",
        "iqd",
        "irr",
        "isk",
        "jmd",
        "jod",
        "jpy",
        "kes",
        "kgs",
        "khr",
        "kmf",
        "kgs",
        "khr",
        "kmf",
        "kpw",
        "krw",
        "kwd",
        "ktd",
        "kzt",
        "lak",
        "lbp",
        "lkr",
        "lrd",
        "lsl",
        "ltc",
        "lyd",
        "mad",
        "mdl",
        "mga",
        "mkd",
        "mmk",
        "mnt",
        "mop",
        "mro",
        "mur",
        "mvr",
        "mwk",
        "mxn",
        "myr",
        "mzn",
        "nad",
        "ngn",
        "nio",
        "nok",
        "npr",
        "omr",
        "pab",
        "pen",
        "pgk",
        "php",
        "pkr",
        "pln",
        "pyg",
        "qar",
        "ron",
        "rsd",
        "rub",
        "rwf",
        "sar",
        "scr",
        "sdg",
        "sek",
        "sgd",
        "shp",
        "sll",
        "sos",
        "srd",
        "std",
        "svc",
        "syp",
        "szl",
        "thb",
        "tjs",
        "tmt",
        "tnd",
        "top",
        "try",
        "ttd",
        "twd",
        "tzs",
        "uah",
        "ugx",
        "usd",
        "uyu",
        "uzs",
        "vef",
        "vuv",
        "wst",
        "xaf",
        "xcd",
        "xof",
        "xpf",
        "yer",
        "zar",
        "zmw",
    ]
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
    description: Optional[str] = None
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
