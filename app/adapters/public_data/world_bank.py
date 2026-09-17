"""Keyless World Bank Open Data adapter."""

import json
from urllib.parse import urlencode
from urllib.request import urlopen

from app.models.public_data import PublicIndicatorRecord

WORLD_BANK_API = "https://api.worldbank.org/v2/country/IND/indicator"
INDICATORS = {
    "population": "SP.POP.TOTL",
    "employment": "SL.EMP.TOTL.SP.ZS",
}


class WorldBankIndicatorAdapter:
    """Fetch public annual India indicators using the documented JSON API."""

    def __init__(self, indicator: str, timeout: int = 10) -> None:
        if indicator not in INDICATORS.values():
            raise ValueError(f"Unsupported World Bank indicator: {indicator}")
        self.indicator = indicator
        self.timeout = timeout

    @property
    def url(self) -> str:
        return f"{WORLD_BANK_API}/{self.indicator}?{urlencode({'format': 'json', 'per_page': 100})}"

    def fetch_records(self) -> list[PublicIndicatorRecord]:
        """Fetch observations; network failure is surfaced to the caller."""
        with urlopen(self.url, timeout=self.timeout) as response:
            payload = json.load(response)
        if not isinstance(payload, list) or len(payload) < 2:
            raise ValueError("Unexpected World Bank response shape")
        records: list[PublicIndicatorRecord] = []
        for observation in payload[1]:
            records.append(
                PublicIndicatorRecord(
                    dataset_id=(
                        "world_bank_india_population"
                        if self.indicator == INDICATORS["population"]
                        else "world_bank_india_employment"
                    ),
                    geography="India",
                    period=str(observation["date"]),
                    indicator=observation["indicator"]["value"],
                    value=observation["value"],
                    source="World Bank Open Data",
                    access_date="2026-09-17",
                )
            )
        return records
