from typing import Optional, Literal
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SyncSettings(Base):
    __tablename__ = "sync_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    qbo_realm_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    stripe_clearing_account_id: Mapped[str]
    stripe_payout_account_id: Mapped[str]
    stripe_vendor_id: Mapped[str]
    stripe_fee_account_id: Mapped[str]
    default_income_account_id: Mapped[str]
    default_tax_code_id: Mapped[str]
    exempt_tax_code_id: Mapped[str]


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    qbo_realm_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    stripe_user_id: Mapped[str | None] = mapped_column(nullable=True)
    qbo_token: Mapped["QBOToken"] = relationship("QBOToken", uselist=False)

    transactions = relationship("TransactionSync", back_populates="id")


class QBOToken(Base):
    __tablename__ = "qbo_tokens"

    realm_id: Mapped[str] = mapped_column(primary_key=True)
    access_token: Mapped[str] = mapped_column(nullable=False)
    refresh_token: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[str] = mapped_column(nullable=False)
    refresh_token_expires_at: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user = relationship("User", back_populates="qbo_token")


class TransactionSync(Base):
    __tablename__ = "transaction_sync"

    id: Mapped[str] = mapped_column(primary_key=True)
    created: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    stripe_id: Mapped[str] = mapped_column(nullable=False)
    qbo_account_id: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[
        Optional[Literal["pending", "success", "failed"]] | None
    ] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # QBO ids
    transfer_id: Mapped[str | None] = mapped_column(nullable=True)
    invoice_id: Mapped[str | None] = mapped_column(nullable=True)
    payment_id: Mapped[str | None] = mapped_column(nullable=True)
    expense_id: Mapped[str | None] = mapped_column(nullable=True)

    user = relationship("User", back_populates="stripe_user_id")
