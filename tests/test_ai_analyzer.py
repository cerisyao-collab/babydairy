"""Tests for AI Feeding Analyzer"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, date, timedelta
from typing import Dict, Any

from src.services.ai_analyzer import (
    FeedingAnalyzer,
    AnalysisResult,
    MetricAnalysis,
    Issue,
    Status,
)


@pytest.fixture
def mock_db():
    """Create mock database session"""
    return MagicMock()


@pytest.fixture
def mock_record_service():
    """Create mock record service"""
    mock = MagicMock()

    # Create mock feeding records
    mock_record1 = MagicMock()
    mock_record1.type = "feeding"
    mock_record1.timestamp = datetime(2024, 1, 15, 8, 0)
    mock_record1.details = {"amount_ml": 100, "feeding_type": "formula"}

    mock_record2 = MagicMock()
    mock_record2.type = "feeding"
    mock_record2.timestamp = datetime(2024, 1, 15, 12, 0)
    mock_record2.details = {"amount_ml": 120, "feeding_type": "formula"}

    mock_record3 = MagicMock()
    mock_record3.type = "feeding"
    mock_record3.timestamp = datetime(2024, 1, 15, 16, 0)
    mock_record3.details = {"amount_ml": 100, "feeding_type": "breast"}

    mock.list_daily_records.return_value = [mock_record1, mock_record2, mock_record3]
    return mock


@pytest.fixture
def mock_config_service():
    """Create mock config service"""
    mock = MagicMock()

    mock_config = MagicMock()
    mock_config.birth_date = date(2024, 1, 1)  # 15 days old
    mock_config.baby_name = "测试宝宝"
    mock_config.get_age_days.return_value = 15

    mock.get_baby_config.return_value = mock_config
    return mock


class TestFeedingAnalyzer:
    """Tests for FeedingAnalyzer class"""

    @patch("src.services.ai_analyzer.RecordService")
    @patch("src.services.ai_analyzer.ConfigService")
    def test_analyze_with_records(
        self,
        mock_config_cls,
        mock_record_cls,
        mock_db,
        mock_record_service,
        mock_config_service,
    ):
        """Test analyze with feeding records"""
        mock_record_cls.return_value = mock_record_service
        mock_config_cls.return_value = mock_config_service

        analyzer = FeedingAnalyzer(mock_db)
        result = analyzer.analyze("test-user-id", "2024-01-15")

        assert result is not None
        assert result.status in [Status.NORMAL, Status.LOW, Status.HIGH]
        assert result.feeding_data_summary["total_milk"] == 320
        assert result.feeding_data_summary["feeding_count"] == 3
        assert result.baby_age_days == 15

    def test_analyze_milk_volume_normal(self, mock_db):
        """Test milk volume analysis when within normal range"""
        with patch("src.services.ai_analyzer.get_standard_for_day") as mock_std:
            mock_std.return_value = {"min": 300, "max": 500, "avg": 400}

            analyzer = FeedingAnalyzer(mock_db)
            result = analyzer.analyze_milk_volume(400, 15)

            assert result.status == Status.NORMAL
            assert result.value == 400
            assert "正常范围" in result.description

    def test_analyze_milk_volume_low(self, mock_db):
        """Test milk volume analysis when below standard"""
        with patch("src.services.ai_analyzer.get_standard_for_day") as mock_std:
            mock_std.return_value = {"min": 500, "max": 900, "avg": 700}

            analyzer = FeedingAnalyzer(mock_db)
            result = analyzer.analyze_milk_volume(400, 15)

            assert result.status == Status.LOW
            assert result.difference_percent > 0

    def test_analyze_milk_volume_high(self, mock_db):
        """Test milk volume analysis when above standard"""
        with patch("src.services.ai_analyzer.get_standard_for_day") as mock_std:
            mock_std.return_value = {"min": 500, "max": 900, "avg": 700}

            analyzer = FeedingAnalyzer(mock_db)
            result = analyzer.analyze_milk_volume(1000, 15)

            assert result.status == Status.HIGH

    def test_analyze_feeding_frequency_normal(self, mock_db):
        """Test feeding frequency analysis"""
        with patch("src.services.ai_analyzer.get_standard_for_day") as mock_std:
            mock_std.return_value = {"min": 6, "max": 10, "avg": 8}

            analyzer = FeedingAnalyzer(mock_db)
            result = analyzer.analyze_feeding_frequency(8, 15)

            assert result.status == Status.NORMAL

    def test_analyze_intervals(self, mock_db):
        """Test feeding interval analysis"""
        with patch("src.services.ai_analyzer.get_standard_for_day") as mock_std:
            mock_std.return_value = {"min": 2.0, "max": 4.0, "avg": 3.0}

            analyzer = FeedingAnalyzer(mock_db)
            result = analyzer.analyze_intervals(3.5, 15)

            assert result.status == Status.NORMAL
            assert "间隔" in result.description

    def test_identify_issues(self, mock_db):
        """Test issue identification"""
        analyzer = FeedingAnalyzer(mock_db)

        metrics = {
            "milk_volume": MetricAnalysis(
                value=400, min=500, max=900, avg=700,
                status=Status.LOW,
                difference_percent=20.0,
                description="奶量偏低"
            ),
            "feeding_frequency": MetricAnalysis(
                value=5, min=6, max=10, avg=8,
                status=Status.LOW,
                description="次数偏少"
            ),
        }

        feeding_data = {
            "total_milk": 400,
            "feeding_count": 5,
            "avg_interval": 4.0,
        }

        issues = analyzer.identify_issues(metrics, feeding_data)

        assert len(issues) > 0
        assert any(i.type == "low_milk_volume" for i in issues)

    def test_generate_recommendations(self, mock_db):
        """Test recommendation generation"""
        with patch("src.services.ai_analyzer.get_standard_for_day") as mock_std:
            mock_std.return_value = {"min": 500, "max": 900, "avg": 700}

            analyzer = FeedingAnalyzer(mock_db)

            issues = [
                Issue(
                    type="low_milk_volume",
                    severity="medium",
                    description="奶量偏低",
                    metric="milk_volume"
                ),
            ]

            metrics = {
                "milk_volume": MetricAnalysis(
                    value=400, min=500, max=900, avg=700,
                    status=Status.LOW,
                    difference_percent=20.0,
                    description="奶量偏低"
                ),
            }

            feeding_data = {"total_milk": 400, "feeding_count": 5}

            recommendations = analyzer.generate_recommendations(metrics, issues, feeding_data, 15)

            assert len(recommendations) > 0
            assert any("奶量" in r for r in recommendations)

    def test_calculate_next_feeding(self, mock_db):
        """Test next feeding time calculation"""
        analyzer = FeedingAnalyzer(mock_db)

        mock_record = MagicMock()
        mock_record.timestamp = datetime(2024, 1, 15, 16, 0)

        with patch("src.services.ai_analyzer.get_standard_for_day") as mock_std:
            mock_std.return_value = {"min": 2.0, "max": 4.0, "avg": 3.5}

            result = analyzer.calculate_next_feeding([mock_record], 15)

            assert result is not None
            # Should be 3.5 hours after last feeding
            expected = datetime(2024, 1, 15, 19, 30)
            assert result == expected

    def test_determine_overall_status(self, mock_db):
        """Test overall status determination"""
        analyzer = FeedingAnalyzer(mock_db)

        metrics = {
            "milk_volume": MetricAnalysis(
                value=400, min=500, max=900, avg=700,
                status=Status.NORMAL,
                description="正常"
            ),
            "frequency": MetricAnalysis(
                value=8, min=6, max=10, avg=8,
                status=Status.NORMAL,
                description="正常"
            ),
        }

        result = analyzer._determine_overall_status(metrics)
        assert result == Status.NORMAL

        metrics["milk_volume"].status = Status.LOW
        result = analyzer._determine_overall_status(metrics)
        assert result == Status.LOW


class TestMetricAnalysis:
    """Tests for MetricAnalysis dataclass"""

    def test_metric_creation(self):
        """Test creating metric analysis"""
        metric = MetricAnalysis(
            value=500,
            min=400,
            max=600,
            avg=500,
            status=Status.NORMAL,
            description="测试描述"
        )

        assert metric.value == 500
        assert metric.status == Status.NORMAL

    def test_metric_with_difference(self):
        """Test metric with difference percentage"""
        metric = MetricAnalysis(
            value=300,
            min=400,
            max=600,
            avg=500,
            status=Status.LOW,
            difference_percent=25.0,
            description="低于标准25%"
        )

        assert metric.difference_percent == 25.0


class TestIssue:
    """Tests for Issue dataclass"""

    def test_issue_creation(self):
        """Test creating an issue"""
        issue = Issue(
            type="low_milk_volume",
            severity="medium",
            description="奶量不足",
            metric="milk_volume"
        )

        assert issue.type == "low_milk_volume"
        assert issue.severity == "medium"


class TestAnalysisResult:
    """Tests for AnalysisResult dataclass"""

    def test_result_creation(self):
        """Test creating analysis result"""
        result = AnalysisResult(
            status=Status.NORMAL,
            confidence=0.8,
            metrics={},
            issues=[],
            recommendations=["保持当前节奏"],
            baby_age_days=15,
            feeding_data_summary={"total_milk": 500},
        )

        assert result.status == Status.NORMAL
        assert result.confidence == 0.8
        assert len(result.recommendations) == 1


class TestStatusEnum:
    """Tests for Status enum"""

    def test_status_values(self):
        """Test status enum values"""
        assert Status.NORMAL.value == "normal"
        assert Status.LOW.value == "low"
        assert Status.HIGH.value == "high"