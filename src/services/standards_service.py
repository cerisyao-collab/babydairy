"""Feeding standards service for loading and querying baby feeding standards"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from functools import lru_cache


# Path to standards data file
STANDARDS_FILE = Path(__file__).parent.parent / "data" / "feeding_standards.json"


@lru_cache(maxsize=1)
def load_standards() -> Dict[str, Any]:
    """
    Load feeding standards data from JSON file.
    Results are cached for performance.
    """
    if not STANDARDS_FILE.exists():
        return {
            "version": "0.0.0",
            "source": "默认数据",
            "standards": {},
            "notes": {},
            "error": "Standards file not found"
        }

    try:
        with open(STANDARDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {
            "version": "0.0.0",
            "source": "默认数据",
            "standards": {},
            "error": "Failed to parse standards file"
        }


def get_available_days() -> List[int]:
    """
    Get list of available day numbers in standards data.

    Returns:
        Sorted list of day numbers
    """
    standards = load_standards()
    days = []
    for key in standards.get("standards", {}).keys():
        if key.startswith("day_"):
            try:
                day = int(key.replace("day_", ""))
                days.append(day)
            except ValueError:
                continue
    return sorted(days)


def get_standard_for_day(day: int, metric: str) -> Optional[Dict[str, float]]:
    """
    Get standard values for a specific day and metric.

    Args:
        day: Baby's age in days
        metric: Metric name (feeding_times, milk_volume_ml, interval_hours, urine_count, bowel_count)

    Returns:
        Dict with min, max, avg values, or None if not found
    """
    standards = load_standards()
    standards_data = standards.get("standards", {})

    # Try exact match first
    day_key = f"day_{day}"
    if day_key in standards_data:
        return standards_data[day_key].get(metric)

    # Find nearest days for interpolation
    available_days = get_available_days()
    if not available_days:
        return None

    # Find surrounding days
    lower_day = None
    upper_day = None

    for d in available_days:
        if d < day:
            lower_day = d
        elif d > day and upper_day is None:
            upper_day = d
            break

    # If day is before first available, use first day's values
    if lower_day is None and upper_day is not None:
        return standards_data.get(f"day_{upper_day}", {}).get(metric)

    # If day is after last available, use last day's values
    if upper_day is None and lower_day is not None:
        return standards_data.get(f"day_{lower_day}", {}).get(metric)

    # Interpolate between lower and upper
    if lower_day is not None and upper_day is not None:
        return interpolate_standard(
            lower_day,
            upper_day,
            day,
            metric,
            standards_data
        )

    return None


def interpolate_standard(
    lower_day: int,
    upper_day: int,
    target_day: int,
    metric: str,
    standards_data: Dict[str, Any]
) -> Dict[str, float]:
    """
    Interpolate standard values between two days.

    Args:
        lower_day: Lower bound day number
        upper_day: Upper bound day number
        target_day: Target day to interpolate to
        metric: Metric name
        standards_data: Standards data dictionary

    Returns:
        Interpolated standard values
    """
    lower_data = standards_data.get(f"day_{lower_day}", {}).get(metric, {})
    upper_data = standards_data.get(f"day_{upper_day}", {}).get(metric, {})

    if not lower_data or not upper_data:
        return lower_data or upper_data or {}

    # Linear interpolation
    ratio = (target_day - lower_day) / (upper_day - lower_day)

    def interpolate_value(key: str) -> float:
        lower_val = lower_data.get(key, 0)
        upper_val = upper_data.get(key, 0)
        return lower_val + ratio * (upper_val - lower_val)

    return {
        "min": interpolate_value("min"),
        "max": interpolate_value("max"),
        "avg": interpolate_value("avg"),
    }


def get_all_standards_for_day(day: int) -> Dict[str, Dict[str, float]]:
    """
    Get all standard metrics for a specific day.

    Args:
        day: Baby's age in days

    Returns:
        Dict of all metrics with their min/max/avg values
    """
    metrics = ["feeding_times", "milk_volume_ml", "interval_hours", "urine_count", "bowel_count"]
    result = {}

    for metric in metrics:
        value = get_standard_for_day(day, metric)
        if value:
            result[metric] = value

    return result


def get_notes() -> Dict[str, str]:
    """
    Get notes and disclaimers from standards data.

    Returns:
        Dict of notes
    """
    standards = load_standards()
    return standards.get("notes", {})


def get_source() -> str:
    """
    Get the source attribution for standards data.

    Returns:
        Source string
    """
    standards = load_standards()
    return standards.get("source", "未知来源")