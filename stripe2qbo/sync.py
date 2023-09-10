from typing import Literal, Optional

from pydantic import BaseModel

from stripe2qbo.qbo.QBO import QBO


class TransactionSync(BaseModel):
    id: str
    created: int
    type: str
    amount: int
    fee: int
    currency: str
    description: Optional[str] = None
    status: Optional[Literal["pending", "success", "failed"]] = None
    transfer_id: Optional[str] = None
    invoice_id: Optional[str] = None
    payment_id: Optional[str] = None
    expense_id: Optional[str] = None


def check_for_existing(
    object_type: str,
    qbo_customer_id: Optional[str] = None,
    date_string: Optional[str] = None,
    private_note: Optional[str] = None,
    qbo: QBO = QBO(),
) -> Optional[str]:
    """Query QBO for an object of type object_type.

    Returns:
        str: QBO object id if found, else None"""
    filter_string = ""
    filters = []

    if date_string is not None:
        filters.append(f"TxnDate = '{date_string}'")
    if qbo_customer_id is not None:
        filters.append(f"CustomerRef = '{qbo_customer_id}'")

    if len(filters) > 0:
        filter_string = "where " + " and ".join(filters)

    response = qbo._query(f"select * from {object_type} {filter_string}")
    qbo_items = response.json()["QueryResponse"].get(object_type, [])

    # Cannot query by PrivateNote, so we filter the returned items
    if private_note is not None:
        qbo_items = [
            item for item in qbo_items if private_note in item.get("PrivateNote", "")
        ]

    if len(qbo_items) == 0:
        return None

    return qbo_items[0]["Id"]
