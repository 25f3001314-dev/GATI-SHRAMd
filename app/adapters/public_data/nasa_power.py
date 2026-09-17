"""NASA POWER public rainfall adapter."""

import json
from urllib.parse import urlencode
from urllib.request import urlopen

from app.models.public_data import PublicIndicatorRecord

NASA_POWER_API = "https://power.larc.nasa.gov/api/temporal/daily/point"


class NASAPowerRainfallAdapter:
    """Fetch public point precipitation observations without credentials."""

    def __init__(
        self,
        latitude: float,
        longitude: float,
        start: str,
        end: str,
        timeout: int = 10,
    ) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.start = start
        self.end = end
        self.timeout = timeout

    @property
    def url(self) -> str:
        query = urlencode(
            {
                "parameters": "PRECTOTCORR",
                "community": "AG",
                "longitude": self.longitude,
                "latitude": self.latitude,
                "start": self.start,
                "end": self.end,
                "format": "JSON",
            }
        )
        return f"{NASA_POWER_API}?{query}"

    def fetch_records(self) -> list[PublicIndicatorRecord]:
        """Fetch daily precipitation values for the configured point."""
        with urlopen(self.url, timeout=self.timeout) as response:
            payload = json.load(response)
        parameter = payload["properties"]["parameter"]["PRECTOTCORR"]
        return [
            PublicIndicatorRecord(
                dataset_id="nasa_power_india_rainfall",
                geography=f"{self.latitude},{self.longitude}",
                period=str(period),
                indicator="PRECTOTCORR",
                value=value,
                source="NASA POWER",
                access_date="2026-09-17",
            )
            for period, value in sorted(parameter.items())
        ]
