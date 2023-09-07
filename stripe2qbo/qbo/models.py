from typing import List, Optional, Literal

from pydantic import BaseModel


QBOCurrency = Literal["USD", "CAD"]


class CompanyInfo(BaseModel):
    CompanyName: str
    Country: str


class CurrencyRef(BaseModel):
    value: QBOCurrency


class ItemRef(BaseModel):
    value: str
    name: Optional[str] = None


class TaxCodeRef(BaseModel):
    value: str


class Customer(BaseModel):
    DisplayName: str
    Id: str
    CurrencyRef: CurrencyRef


class TaxRateDetail(BaseModel):
    TaxRateRef: ItemRef


class TaxRateList(BaseModel):
    TaxRateDetail: List[TaxRateDetail]


class TaxCode(BaseModel):
    Id: str
    SalesTaxRateList: TaxRateList


class TaxLineDetail(BaseModel):
    TaxRateRef: Optional[ItemRef] = None
    PercentBased: bool = True
    TaxPercent: float
    NetAmountTaxable: float


class TaxLineModel(BaseModel):
    DetailType: Literal["TaxLineDetail"] = "TaxLineDetail"
    Amount: float
    TaxLineDetail: TaxLineDetail


class TaxDetail(BaseModel):
    TotalTax: float
    TaxLine: Optional[List[TaxLineModel]] = None
    TxnTaxCodeRef: Optional[TaxCodeRef] = None


class Transfer(BaseModel):
    Amount: float
    FromAccountRef: ItemRef
    ToAccountRef: ItemRef
    TxnDate: str
    PrivateNote: str


class AccountBasedExpenseLineDetail(BaseModel):
    AccountRef: ItemRef


class ExpenseLine(BaseModel):
    DetailType: Literal[
        "AccountBasedExpenseLineDetail"
    ] = "AccountBasedExpenseLineDetail"
    Amount: float
    Description: Optional[str] = None
    AccountBasedExpenseLineDetail: AccountBasedExpenseLineDetail


class Expense(BaseModel):
    CurrencyRef: CurrencyRef
    PaymentType: Literal["Check"] = "Check"
    TotalAmt: float
    AccountRef: ItemRef
    EntityRef: ItemRef
    TxnDate: str
    PrivateNote: str
    Line: List[ExpenseLine]


class ProductItemRef(BaseModel):
    value: Optional[str] = None
    name: Optional[str] = None


class SalesItemLineDetail(BaseModel):
    ItemRef: ProductItemRef
    TaxCodeRef: Optional[TaxCodeRef]


class InvoiceLine(BaseModel):
    Amount: float
    Description: Optional[str]
    SalesItemLineDetail: SalesItemLineDetail
    DetailType: Literal["SalesItemLineDetail"] = "SalesItemLineDetail"


class Invoice(BaseModel):
    CustomerRef: ItemRef
    CurrencyRef: CurrencyRef
    TxnDate: Optional[str] = None
    DueDate: Optional[str] = None
    PrivateNote: str
    DocNumber: Optional[str] = None
    TxnTaxDetail: Optional[TaxDetail] = None
    DepositToAccountRef: Optional[ItemRef] = None
    ARAccountRef: Optional[ItemRef] = None
    Line: List[InvoiceLine]


class LinkedTxn(BaseModel):
    TxnId: str
    TxnType: Literal["Invoice"] = "Invoice"


class PaymentLine(BaseModel):
    Amount: float
    LinkedTxn: List["LinkedTxn"]


class Payment(BaseModel):
    TotalAmt: float
    CustomerRef: ItemRef
    TxnDate: str
    DepositToAccountRef: ItemRef
    CurrencyRef: CurrencyRef
    ExchangeRate: float
    Line: Optional[List[PaymentLine]] = None
    PrivateNote: str
