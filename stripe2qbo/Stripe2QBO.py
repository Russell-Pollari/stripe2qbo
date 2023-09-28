import os
from typing import cast, Dict, Optional
from datetime import datetime

from stripe2qbo.db.models import User
from stripe2qbo.db.schemas import Settings, TransactionSync
from stripe2qbo.exceptions import QBOException
from stripe2qbo.qbo.QBO import QBO
from stripe2qbo.qbo.auth import Token
import stripe2qbo.qbo.models as qbo_models
import stripe2qbo.stripe.models as stripe_models
from stripe2qbo.sync import check_for_existing
from stripe2qbo.transforms import (
    qbo_invoice_from_stripe_invoice,
    transfer_from_payout,
    expense_from_transaction,
    payment_from_charge,
)


def _transfrom_timestamp(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")


class Stripe2QBO:
    _settings: Settings
    _qbo: QBO
    _tax_codes: Dict[str, qbo_models.TaxCode | None] = {}
    _exchange_rate: float = 1.0
    _currency: qbo_models.QBOCurrency

    def __init__(self, settings: Settings, qbo_token: Token) -> None:
        self._settings = settings
        self._qbo = QBO(qbo_token)

        if self._qbo.using_sales_tax:
            self._tax_codes[self._settings.default_tax_code_id] = (
                self._qbo.get_tax_code(self._settings.default_tax_code_id)
                if self._settings.default_tax_code_id != "TAX"
                else None
            )
            self._tax_codes[self._settings.exempt_tax_code_id] = (
                self._qbo.get_tax_code(self._settings.exempt_tax_code_id)
                if self._settings.exempt_tax_code_id != "NON"
                else None
            )

    def sync_invoice(
        self, stripe_invoice: stripe_models.Invoice, qbo_customer: qbo_models.Customer
    ):
        invoice_id = check_for_existing(
            "Invoice",
            qbo_customer_id=qbo_customer.Id,
            date_string=_transfrom_timestamp(stripe_invoice.created),
            private_note=stripe_invoice.id,
            qbo=self._qbo,
        )
        if invoice_id:
            return invoice_id

        qbo_invoice = qbo_invoice_from_stripe_invoice(
            stripe_invoice,
            qbo_customer.Id,
            self._tax_codes,
            self._settings,
            exchange_rate=self._exchange_rate,
        )

        for line in qbo_invoice.Line:
            product = line.SalesItemLineDetail.ItemRef
            if product.value is None and product.name is not None:
                income_account_id = self._qbo.get_or_create_account(
                    product.name, "Income"
                )
                line.SalesItemLineDetail.ItemRef = cast(
                    qbo_models.ProductItemRef,
                    self._qbo.get_or_create_item(
                        product.name,
                        income_account_id,
                    ),
                )

        invoice_id = self._qbo.create_invoice(qbo_invoice)
        return invoice_id

    def sync_charge(
        self,
        stripe_charge: stripe_models.Charge,
        qbo_customer: qbo_models.Customer,
        qbo_invoice_id: Optional[str] = None,
    ) -> str:
        """Create a QBO Payment for a Stripe Charge"""
        date_string = _transfrom_timestamp(stripe_charge.created)
        payment_id = check_for_existing(
            "Payment",
            qbo_customer_id=qbo_customer.Id,
            date_string=date_string,
            private_note=stripe_charge.id,
            qbo=self._qbo,
        )
        if payment_id:
            return payment_id

        payment = payment_from_charge(
            stripe_charge,
            qbo_customer.Id,
            self._settings,
            invoice_id=qbo_invoice_id,
            exchange_rate=self._exchange_rate,
        )
        payment_id = self._qbo.create_payment(payment)
        return payment_id

    def sync_stripe_fee(self, transaction: stripe_models.Transaction) -> str:
        """Create a QBO Expense for a Stripe Transaction"""
        date_string = _transfrom_timestamp(transaction.created)
        expense_id = check_for_existing(
            "Purchase",
            private_note=transaction.id,
            date_string=date_string,
            qbo=self._qbo,
        )
        if expense_id:
            return expense_id

        expense = expense_from_transaction(
            transaction,
            self._settings,
        )
        expense_id = self._qbo.create_expense(expense)
        return expense_id

    def sync_payout(self, payout: stripe_models.Payout) -> str:
        """Create a QBO Transfer for a Stripe Payout"""
        transfer_id = check_for_existing(
            "Transfer", private_note=payout.id, qbo=self._qbo
        )
        if transfer_id:
            return transfer_id

        transfer = transfer_from_payout(payout, self._settings)
        transfer_id = self._qbo.create_transfer(transfer)
        return transfer_id

    def sync(
        self, transaction: stripe_models.Transaction, user: User
    ) -> TransactionSync:
        currency = cast(qbo_models.QBOCurrency, transaction.currency.upper())
        stripe_user_id = os.getenv("STRIPE_ACCOUNT_ID", user.stripe_user_id)

        sync_status = TransactionSync(
            **transaction.model_dump(),
            user_id=user.id,
            stripe_id=cast(str, stripe_user_id),
            status="failed",
        )
        if currency != self._qbo.home_currency:
            # TODO: Actually implement this and test it..
            # Implies Stripe account has another bank account for another currency
            # Would need to ensure QBO has corresponding bank accounts

            # date_string = _transfrom_timestamp(transaction.created)
            # self._exchange_rate = self._qbo.get_exchange_rate(currency, date_string)
            sync_status.status = "failed"
            sync_status.failure_reason = (
                f"Transaction currency ({currency})"
                + f" does not match QBO home currency: {self._qbo.home_currency}"
            )
            return sync_status
        else:
            self._exchange_rate = transaction.exchange_rate or 1.0

        if transaction.type not in ["charge", "payout", "stripe_fee", "payment"]:
            sync_status.status = "failed"
            sync_status.failure_reason = (
                f"Unsupported transaction type: {transaction.type}"
            )
            return sync_status

        try:
            if transaction.type == "stripe_fee":
                sync_status.status = "success"
                sync_status.expense_id = self.sync_stripe_fee(transaction)
                return sync_status

            if transaction.customer:
                assert transaction.charge is not None
                charge_currency = cast(
                    qbo_models.QBOCurrency, transaction.charge.currency.upper()
                )
                qbo_customer = self._qbo.get_or_create_customer(
                    transaction.customer.name or transaction.customer.id,
                    charge_currency,
                )
            else:
                qbo_customer = self._qbo.get_or_create_customer(
                    "Stripe customer", currency
                )

            if transaction.invoice:
                sync_status.invoice_id = self.sync_invoice(
                    transaction.invoice, qbo_customer
                )

            if transaction.charge:
                sync_status.payment_id = self.sync_charge(
                    transaction.charge, qbo_customer, sync_status.invoice_id
                )
                sync_status.expense_id = self.sync_stripe_fee(transaction)

            if transaction.payout:
                sync_status.transfer_id = self.sync_payout(transaction.payout)
        except QBOException as e:
            sync_status.status = "failed"
            sync_status.failure_reason = str(e)
            return sync_status
        except Exception:
            sync_status.status = "failed"
            sync_status.failure_reason = "Server error"
            return sync_status

        sync_status.status = "success"
        return sync_status
