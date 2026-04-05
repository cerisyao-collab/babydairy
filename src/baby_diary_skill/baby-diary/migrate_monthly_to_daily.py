#!/usr/bin/env python3
"""
Migration script: Convert monthly record files to daily files

This script reads all monthly JSON files and splits them into daily files.
A backup of the original data is created before migration.

Usage:
    python migrate_monthly_to_daily.py [--backup-dir <path>]
"""

import json
import shutil
from datetime import datetime
from pathlib import Path


def get_records_dir() -> Path:
    """Get the records directory"""
    base_dir = Path(__file__).parent
    documents_dir = Path.home() / "Documents" / "baby-diary" / "records"
    if documents_dir.exists():
        return documents_dir
    return base_dir / "records"


def create_backup(records_dir: Path) -> Path:
    """Create a backup of all monthly files"""
    backup_dir = records_dir / "backup_monthly" / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Copy all monthly files to backup
    for monthly_file in records_dir.glob("*.json"):
        if monthly_file.name == "index.json":
            continue
        shutil.copy2(monthly_file, backup_dir / monthly_file.name)

    print(f"Backup created: {backup_dir}")
    return backup_dir


def migrate_monthly_to_daily(records_dir: Path) -> tuple[int, int]:
    """
    Migrate monthly files to daily files

    Returns:
        (total_records, days_created)
    """
    total_records = 0
    days_created = 0

    # Read all monthly files
    monthly_files = sorted(records_dir.glob("*.json"))
    monthly_files = [f for f in monthly_files if f.name != "index.json"]

    if not monthly_files:
        print("No monthly files found. Nothing to migrate.")
        return 0, 0

    # Process each monthly file
    for monthly_file in monthly_files:
        print(f"Processing: {monthly_file.name}")

        try:
            with open(monthly_file, "r", encoding="utf-8") as f:
                records = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"  Error reading {monthly_file.name}: {e}")
            continue

        # Group records by date
        daily_records: dict[str, list] = {}
        for record in records:
            date = record.get("date", "")
            if not date:
                # Try to extract date from timestamp
                timestamp = record.get("timestamp", "")
                if timestamp:
                    try:
                        date = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d")
                    except Exception:
                        print(f"  Warning: Could not determine date for record {record.get('id', 'unknown')}")
                        continue

            if date not in daily_records:
                daily_records[date] = []
            daily_records[date].append(record)

        # Write daily files
        for date, day_records in daily_records.items():
            daily_file = records_dir / f"{date}.json"
            existing_records = []

            # Merge with existing daily file if it exists
            if daily_file.exists():
                try:
                    with open(daily_file, "r", encoding="utf-8") as f:
                        existing_records = json.load(f)
                except (json.JSONDecodeError, IOError):
                    existing_records = []

            # Add new records (avoid duplicates by ID)
            existing_ids = {r.get("id") for r in existing_records}
            for record in day_records:
                if record.get("id") not in existing_ids:
                    existing_records.append(record)

            # Sort by timestamp
            existing_records.sort(key=lambda x: x.get("timestamp", ""))

            # Write daily file
            with open(daily_file, "w", encoding="utf-8") as f:
                json.dump(existing_records, f, ensure_ascii=False, indent=2)

            days_created += 1
            total_records += len(day_records)

        print(f"  Created {len(daily_records)} daily files with {len(records)} records")

    return total_records, days_created


def rebuild_index(records_dir: Path) -> int:
    """Rebuild the index file based on daily files"""
    index = {"version": "1.0", "updated": datetime.now().isoformat(), "days": {}}

    for daily_file in sorted(records_dir.glob("*.json")):
        if daily_file.name == "index.json":
            continue

        date = daily_file.stem  # YYYY-MM-DD
        try:
            with open(daily_file, "r", encoding="utf-8") as f:
                records = json.load(f)

            # Get record types
            types = list(set(r.get("type", "") for r in records if r.get("type")))

            index["days"][date] = {
                "file": f"{date}.json",
                "count": len(records),
                "sizeBytes": daily_file.stat().st_size,
                "types": types
            }
        except (json.JSONDecodeError, IOError) as e:
            print(f"  Error processing {daily_file.name}: {e}")

    # Save index
    index_file = records_dir / "index.json"
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    return len(index["days"])


def main():
    """Main migration function"""
    print("=" * 60)
    print("Baby Diary: Monthly to Daily Migration")
    print("=" * 60)

    records_dir = get_records_dir()
    print(f"Records directory: {records_dir}")

    if not records_dir.exists():
        print("Error: Records directory does not exist.")
        return

    # Check for monthly files
    monthly_files = list(records_dir.glob("*.json"))
    monthly_files = [f for f in monthly_files if f.name != "index.json"]

    if not monthly_files:
        print("No monthly files found. Migration not needed.")
        return

    print(f"Found {len(monthly_files)} monthly file(s)")

    # Create backup
    print("\nCreating backup...")
    backup_dir = create_backup(records_dir)

    # Migrate
    print("\nMigrating monthly files to daily files...")
    total_records, days_created = migrate_monthly_to_daily(records_dir)

    print(f"\nMigration complete:")
    print(f"  Total records migrated: {total_records}")
    print(f"  Daily files created: {days_created}")

    # Rebuild index
    print("\nRebuilding index...")
    days_indexed = rebuild_index(records_dir)
    print(f"Index built with {days_indexed} days")

    print("\n" + "=" * 60)
    print("Migration completed successfully!")
    print(f"Backup location: {backup_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
