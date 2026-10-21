#!/usr/bin/env python3
"""Download every external source consumed by the city-climate analysis.

Uses only the Python standard library. Existing snapshots are retained unless
``--force`` is supplied, making the default safe for the bundled repository.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
USER_AGENT = "Australian-city-climate-reproducibility/1.0 (+public data download)"

GHCN_STATIONS = (
    "ASN00009021", "ASN00014015", "ASN00015590", "ASN00023013",
    "ASN00023034", "ASN00040004", "ASN00040211", "ASN00066037",
    "ASN00086282", "ASN00094029",
)

def sources() -> list[tuple[str, str, str]]:
    items = [
        (f"{station}.dly", f"https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/{station}.dly", station)
        for station in GHCN_STATIONS
    ]
    items.extend([
        ("soi_monthly.txt", "https://www.bom.gov.au/clim_data/IDCKGSH000/soi_monthly.txt", ","),
        (
            "population_all.xlsx",
            "https://www.abs.gov.au/statistics/people/population/regional-population/2024-25/32180DS0003_2001-25.xlsx",
            "xlsx",
        ),
        (
            "population_sua.xlsx",
            "https://www.abs.gov.au/statistics/people/population/regional-population/2024-25/32180DS0004_2001-25.xlsx",
            "xlsx",
        ),
    ])
    return items


def validate(data: bytes, marker: str, filename: str) -> None:
    if len(data) < 100:
        raise ValueError(f"{filename}: response is unexpectedly small ({len(data)} bytes)")
    if marker == "xlsx":
        if not data.startswith(b"PK"):
            raise ValueError(f"{filename}: response is not an XLSX/ZIP file")
        return
    text = data[:200_000].decode("utf-8", errors="ignore")
    if marker not in text:
        raise ValueError(f"{filename}: expected marker {marker!r} was not found")


def download(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:
        return response.read()


def atomic_write(target: Path, data: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=target.name + ".", dir=target.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(temporary, target)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="replace existing snapshots")
    parser.add_argument("--dry-run", action="store_true", help="print the manifest without downloading")
    args = parser.parse_args()

    failures = []
    for filename, url, marker in sources():
        target = RAW / filename
        if args.dry_run:
            print(f"{filename}\t{url}")
            continue
        if target.exists() and not args.force:
            try:
                validate(target.read_bytes(), marker, filename)
                print(f"kept       {filename}")
            except Exception as exc:
                failures.append(str(exc))
            continue
        try:
            data = download(url)
            validate(data, marker, filename)
            atomic_write(target, data)
            print(f"downloaded {filename} ({len(data):,} bytes)")
        except Exception as exc:
            failures.append(f"{filename}: {exc}")

    if failures:
        print("\nDownload/validation failures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
