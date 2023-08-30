import os
import json
from typing import Optional

from pydantic import BaseModel


def _snake_to_camel(s: str) -> str:
    words = s.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])


class Settings(BaseModel):
    stripe_clearing_account_id: str
    stripe_payout_account_id: str
    stripe_vendor_id: str
    stripe_fee_account_id: str
    default_income_account_id: Optional[str] = None
    default_tax_code_id: str
    exempt_tax_code_id: str
    # product_settings: list[ProductSettings]
    # tax_settings: list[TaxSettings]

    model_config = {
        "alias_generator": _snake_to_camel,
        "populate_by_name": True,
    }


def load_from_file(
    qbo_realm_id: str, path: str = "settings.json"
) -> Optional[Settings]:
    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        all_settings = json.load(f)

        settings = all_settings.get(qbo_realm_id)

    return Settings(**settings) if settings else None


def save(qbo_realm_id: str, settings: Settings, path: str = "settings.json") -> None:
    all_settings = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            all_settings = json.load(f)

    with open(path, "w") as f:
        json.dump({**all_settings, qbo_realm_id: settings.model_dump()}, f, indent=4)
