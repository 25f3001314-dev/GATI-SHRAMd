"""Public-coordinate geography with a documented demo fallback."""

import csv
import math
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Coordinate:
    latitude: float
    longitude: float


@dataclass(frozen=True)
class GeographicDistance:
    distance_km: float
    distance_source: str


def haversine_distance(first: Coordinate, second: Coordinate) -> float:
    """Calculate great-circle distance in kilometers."""
    radius_km = 6371.0088
    latitude_delta = math.radians(second.latitude - first.latitude)
    longitude_delta = math.radians(second.longitude - first.longitude)
    first_latitude = math.radians(first.latitude)
    second_latitude = math.radians(second.latitude)
    haversine = (
        math.sin(latitude_delta / 2) ** 2
        + math.cos(first_latitude)
        * math.cos(second_latitude)
        * math.sin(longitude_delta / 2) ** 2
    )
    return round(2 * radius_km * math.asin(math.sqrt(haversine)), 4)


def load_coordinates(path: str | Path) -> dict[str, Coordinate]:
    """Load a public place-coordinate CSV with place,latitude,longitude columns."""
    coordinates: dict[str, Coordinate] = {}
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"place", "latitude", "longitude"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing geography columns: {sorted(missing)}")
        for row_number, row in enumerate(reader, start=2):
            try:
                coordinates[row["place"].strip()] = Coordinate(
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                )
            except (KeyError, ValueError) as error:
                raise ValueError(f"Malformed geography row {row_number}") from error
    return coordinates


def distance_between(
    origin: str,
    destination: str,
    coordinates: dict[str, Coordinate] | None = None,
) -> GeographicDistance:
    """Use public coordinates when available, otherwise the Step 3 demo proxy."""
    if coordinates and origin in coordinates and destination in coordinates:
        return GeographicDistance(
            distance_km=haversine_distance(coordinates[origin], coordinates[destination]),
            distance_source="PUBLIC_DATA",
        )
    return GeographicDistance(
        distance_km=_demo_distance_proxy(origin, destination),
        distance_source="DEMO_PROXY",
    )


def _demo_distance_proxy(origin: str, destination: str) -> float:
    """Use the documented Step 3 proxy without importing feature engineering."""
    proxies = {
        ("Bihar", "Maharashtra"): 1_400.0,
        ("Bihar", "Delhi"): 1_000.0,
        ("Uttar Pradesh", "Maharashtra"): 1_200.0,
        ("Uttar Pradesh", "Delhi"): 500.0,
    }
    return proxies.get((origin, destination), 1_000.0)
