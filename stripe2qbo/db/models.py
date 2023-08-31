from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
