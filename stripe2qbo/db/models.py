from typing import List
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
    qbo_token: Mapped["QBOToken"] = relationship("QBOToken", uselist=False)

    stripe_accounts: Mapped[List["StripeAccounts"]] = relationship(
        "StripeAccounts", back_populates="user"
    )


class StripeAccounts(Base):
    __tablename__ = "stripe_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    stripe_account_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped[User] = relationship("User", back_populates="stripe_accounts")


class QBOToken(Base):
    __tablename__ = "qbo_tokens"

    realm_id: Mapped[str] = mapped_column(primary_key=True)
    access_token: Mapped[str] = mapped_column(nullable=False)
    refresh_token: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[str] = mapped_column(nullable=False)
    refresh_token_expires_at: Mapped[str] = mapped_column(nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user = relationship("User", back_populates="qbo_token")
