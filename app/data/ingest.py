"""CLI for validating and processing a public mobility CSV."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from app.adapters.public_data.csv_mobility import CSVMobilityAdapter


def process_file(input_path: str, output_path: str) -> int:
    """Validate a public CSV and write sanitized-free source records as JSON."""
    records = CSVMobilityAdapter(input_path).fetch_records()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with Path(output_path).open("w", encoding="utf-8") as handle:
        json.dump([asdict(record) for record in records], handle, indent=2)
    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Process a public mobility CSV")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()
    count = process_file(arguments.input, arguments.output)
    print(f"Processed {count} public mobility records")


if __name__ == "__main__":
    main()
