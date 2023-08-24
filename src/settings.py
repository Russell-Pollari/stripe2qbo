from typing import Optional, List


from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProductSettings(BaseModel):
    product_name: str
    income_account_name: Optional[str] = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    STRIPE_PAYOUT_ACCOUNT: str = "Chequing"
    STRIPE_BANK_ACCOUNT: str = "Stripe"

    STRIPE_VENDOR_NAME: str = "Stripe"
    STRIPE_FEE_EXPENSE_ACCOUNT: str = "Stripe fees"

    DEFAULT_INCOME_ACCOUNT_NAME: Optional[str] = "Stripe Income"
    PRODUCTS: List[ProductSettings] = []

    DEFAULT_TAX_CODE_ID: Optional[str] = "TAX"
    EXEMPT_TAX_CODE_ID: Optional[str] = "NON"
    # TODO: TAXES: List[TaxSettings] = []


# TODO: read settings from json
settings = Settings()  # type: ignore
