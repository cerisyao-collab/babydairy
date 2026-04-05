"""Tests for Standards Service"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import json
from typing import Dict, Any

from src.services.standards_service import (
    load_standards,
    get_standard_for_day,
    interpolate_standard,
    get_all_standards_for_day,
)


@pytest.fixture
def mock_standards_data():
    """Create mock standards data"""
    return {
        "metadata": {
            "source": "测试数据来源",
            "version": "1.0",
        },
        "standards": {
            "day_1": {
                "feeding_times": {"min": 8, "max": 12, "avg": 10},
                "milk_volume_ml": {"min": 30, "max": 60, "avg": 45},
                "interval_hours": {"min": 1.5, "max": 3.0, "avg": 2.0},
            },
            "day_7": {
                "feeding_times": {"min": 7, "max": 10, "avg": 8},
                "milk_volume_ml": {"min": 150, "max": 200, "avg": 175},
                "interval_hours": {"min": 2.0, "max": 4.0, "avg": 3.0},
            },
            "day_15": {
                "feeding_times": {"min": 6, "max": 9, "avg": 7},
                "milk_volume_ml": {"min": 300, "max": 500, "avg": 400},
                "interval_hours": {"min": 2.5, "max": 4.0, "avg": 3.5},
            },
            "day_30": {
                "feeding_times": {"min": 6, "max": 8, "avg": 7},
                "milk_volume_ml": {"min": 500, "max": 800, "avg": 650},
                "interval_hours": {"min": 3.0, "max": 4.5, "avg": 3.5},
            },
        },
    }


class TestLoadStandards:
    """Tests for load_standards function"""

    @patch("builtins.open", create=True)
    @patch("json.load")
    def test_load_standards_success(self, mock_json_load, mock_open, mock_standards_data):
        """Test successful standards loading"""
        mock_json_load.return_value = mock_standards_data
        mock_file = MagicMock()
        mock_open.return_value = mock_file

        result = load_standards()

        assert result is not None
        assert "standards" in result

    @patch("builtins.open", create=True)
    def test_load_standards_file_not_found(self, mock_open):
        """Test standards loading when file not found"""
        mock_open.side_effect = FileNotFoundError()

        result = load_standards()

        # Should return empty dict or handle gracefully
        assert result is not None


class TestGetStandardForDay:
    """Tests for get_standard_for_day function"""

    @patch("src.services.standards_service.load_standards")
    def test_get_standard_exact_day(self, mock_load, mock_standards_data):
        """Test getting standard for exact day"""
        mock_load.return_value = mock_standards_data

        result = get_standard_for_day(15, "milk_volume_ml")

        assert result is not None
        assert result["min"] == 300
        assert result["max"] == 500
        assert result["avg"] == 400

    @patch("src.services.standards_service.load_standards")
    def test_get_standard_interpolated_day(self, mock_load, mock_standards_data):
        """Test getting standard for day requiring interpolation"""
        mock_load.return_value = mock_standards_data

        # Day 10 is between day_7 and day_15
        result = get_standard_for_day(10, "milk_volume_ml")

        assert result is not None
        # Should be interpolated between day_7 (175 avg) and day_15 (400 avg)
        # Linear interpolation: 175 + (400-175) * (10-7)/(15-7) = 175 + 225 * 3/8 ≈ 259
        assert result["avg"] > 175
        assert result["avg"] < 400

    @patch("src.services.standards_service.load_standards")
    def test_get_standard_before_range(self, mock_load, mock_standards_data):
        """Test getting standard for day before data range"""
        mock_load.return_value = mock_standards_data

        # Day 0 (before day_1)
        result = get_standard_for_day(0, "milk_volume_ml")

        # Should return day_1 standard as fallback
        assert result is not None
        assert result["min"] == 30

    @patch("src.services.standards_service.load_standards")
    def test_get_standard_after_range(self, mock_load, mock_standards_data):
        """Test getting standard for day after data range"""
        mock_load.return_value = mock_standards_data

        # Day 100 (after day_30)
        result = get_standard_for_day(100, "milk_volume_ml")

        # Should return day_30 standard as fallback
        assert result is not None
        assert result["min"] == 500

    @patch("src.services.standards_service.load_standards")
    def test_get_standard_invalid_metric(self, mock_load, mock_standards_data):
        """Test getting standard for invalid metric"""
        mock_load.return_value = mock_standards_data

        result = get_standard_for_day(15, "invalid_metric")

        assert result is None


class TestInterpolateStandard:
    """Tests for interpolate_standard function"""

    def test_interpolate_between_values(self):
        """Test interpolation between two values"""
        lower = {"min": 100, "max": 200, "avg": 150}
        upper = {"min": 200, "max": 400, "avg": 300}

        # Interpolate at 50% between
        result = interpolate_standard(lower, upper, lower_day=7, upper_day=14, target_day=10)

        assert result is not None
        # 10 is 3/7 of the way from 7 to 14
        # min: 100 + (200-100) * 3/7 ≈ 143
        expected_min = 100 + (200 - 100) * (10 - 7) / (14 - 7)
        assert abs(result["min"] - expected_min) < 1

    def test_interpolate_same_days(self):
        """Test interpolation when days are the same"""
        lower = {"min": 100, "max": 200, "avg": 150}
        upper = {"min": 200, "max": 400, "avg": 300}

        result = interpolate_standard(lower, upper, lower_day=7, upper_day=7, target_day=7)

        # Should return lower bound
        assert result["min"] == 100

    def test_interpolate_outside_range(self):
        """Test interpolation outside the range"""
        lower = {"min": 100, "max": 200, "avg": 150}
        upper = {"min": 200, "max": 400, "avg": 300}

        # Target before lower day
        result = interpolate_standard(lower, upper, lower_day=7, upper_day=14, target_day=5)

        # Should clamp to lower
        assert result["min"] == 100


class TestGetAllStandardsForDay:
    """Tests for get_all_standards_for_day function"""

    @patch("src.services.standards_service.load_standards")
    def test_get_all_standards(self, mock_load, mock_standards_data):
        """Test getting all standards for a day"""
        mock_load.return_value = mock_standards_data

        result = get_all_standards_for_day(15)

        assert result is not None
        assert "feeding_times" in result
        assert "milk_volume_ml" in result
        assert "interval_hours" in result

    @patch("src.services.standards_service.load_standards")
    def test_get_all_standards_interpolated(self, mock_load, mock_standards_data):
        """Test getting all standards for interpolated day"""
        mock_load.return_value = mock_standards_data

        result = get_all_standards_for_day(10)

        assert result is not None
        assert "feeding_times" in result
        assert "milk_volume_ml" in result
        # All metrics should be interpolated


class TestStandardsDataIntegrity:
    """Tests for standards data integrity"""

    @patch("src.services.standards_service.load_standards")
    def test_standards_have_required_fields(self, mock_load, mock_standards_data):
        """Test that standards have required min/max/avg fields"""
        mock_load.return_value = mock_standards_data

        for day_key, day_data in mock_standards_data["standards"].items():
            for metric_name, metric_data in day_data.items():
                assert "min" in metric_data
                assert "max" in metric_data
                assert "avg" in metric_data
                assert metric_data["min"] <= metric_data["avg"] <= metric_data["max"]

    @patch("src.services.standards_service.load_standards")
    def test_standards_progression(self, mock_load, mock_standards_data):
        """Test that standards show expected progression"""
        mock_load.return_value = mock_standards_data

        # Milk volume should increase with age
        days = sorted([int(k.replace("day_", "")) for k in mock_standards_data["standards"].keys()])
        volumes = []

        for day in days:
            std = get_standard_for_day(day, "milk_volume_ml")
            volumes.append(std["avg"])

        # Check that volumes generally increase
        for i in range(1, len(volumes)):
            assert volumes[i] >= volumes[i-1], f"Volume should increase: day {days[i-1]} to {days[i]}"