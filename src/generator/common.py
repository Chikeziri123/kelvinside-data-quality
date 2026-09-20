"""
Shared helpers for the generators: the defect manifest, CSV output and
small formatting utilities.
"""

import csv
import random
import string
from datetime import date, timedelta

from .config import RAW_DIR

MANIFEST_FILE = "_defect_manifest.csv"

MANIFEST_FIELDS = [
    "defect_id",
    "source_system",
    "table_name",
    "record_key",
    "field_name",
    "defect_type",
    "quality_dimension",
    "expected_detection_by",
    "business_impact",
]


class DefectManifest:
    """
    Records every defect deliberately injected into the synthetic landscape.

    The manifest is the control against which rule coverage is measured in
    Phase 6. Without it, a passing test suite proves nothing, because there
    is no way to know what it failed to look for.
    """

    def __init__(self):
        self._rows = []
        self._counter = 0

    def record(
        self,
        source_system,
        table_name,
        record_key,
        field_name,
        defect_type,
        quality_dimension,
        expected_detection_by,
        business_impact,
    ):
        self._counter += 1
        self._rows.append(
            {
                "defect_id": f"DEF{self._counter:05d}",
                "source_system": source_system,
                "table_name": table_name,
                "record_key": record_key,
                "field_name": field_name,
                "defect_type": defect_type,
                "quality_dimension": quality_dimension,
                "expected_detection_by": expected_detection_by,
                "business_impact": business_impact,
            }
        )

    def __len__(self):
        return len(self._rows)

    def summary(self):
        counts = {}
        for row in self._rows:
            counts[row["defect_type"]] = counts.get(row["defect_type"], 0) + 1
        return dict(sorted(counts.items()))

    def write(self):
        write_csv(MANIFEST_FILE, MANIFEST_FIELDS, self._rows)


def write_csv(filename, fieldnames, rows):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: iso(row.get(key)) for key in fieldnames})
    return path


def iso(value):
    """Render dates as ISO strings and None as empty, matching a flat extract."""
    if value is None:
        return ""
    if isinstance(value, date):
        return value.isoformat()
    return value


def uk_postcode(rng):
    area = "".join(rng.choice(string.ascii_uppercase) for _ in range(rng.choice([1, 2])))
    district = str(rng.randint(1, 30))
    sector = str(rng.randint(0, 9))
    unit = "".join(rng.choice(string.ascii_uppercase) for _ in range(2))
    return f"{area}{district} {sector}{unit}"


def random_date(rng, start, end):
    span = (end - start).days
    return start + timedelta(days=rng.randint(0, max(span, 0)))


def pick_sample(rng, population, rate):
    """Select a proportion of a population without replacement."""
    count = int(len(population) * rate)
    if count == 0:
        return []
    return rng.sample(population, count)