"""AI Feeding Analyzer Service

Analyzes baby feeding data and provides recommendations.
Uses rule-based analysis combined with LLM for natural language output.
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from src.services.record_service import RecordService
from src.services.config_service import ConfigService
from src.services.standards_service import get_standard_for_day, get_all_standards_for_day


class Status(str, Enum):
    """Analysis status levels"""
    NORMAL = "normal"
    LOW = "low"
    HIGH = "high"


@dataclass
class MetricAnalysis:
    """Analysis result for a single metric"""
    value: float
    min: float
    max: float
    avg: float
    status: Status
    difference_percent: Optional[float] = None
    description: str = ""


@dataclass
class Issue:
    """Identified feeding issue"""
    type: str
    severity: str  # low, medium, high
    description: str
    metric: str


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    status: Status
    confidence: float
    metrics: Dict[str, MetricAnalysis]
    issues: List[Issue]
    recommendations: List[str]
    ai_summary: Optional[str] = None
    next_feeding_suggestion: Optional[datetime] = None
    baby_age_days: Optional[int] = None
    feeding_data_summary: Dict[str, Any] = field(default_factory=dict)


class FeedingAnalyzer:
    """Analyzes feeding data against standards"""

    def __init__(self, db: Session):
        self.db = db
        self.record_service = RecordService(db)
        self.config_service = ConfigService(db)

    def analyze(self, user_id: str, target_date: Optional[str] = None) -> AnalysisResult:
        """
        Perform complete feeding analysis for a user.

        Args:
            user_id: User's UUID
            target_date: Date to analyze (YYYY-MM-DD), defaults to today

        Returns:
            AnalysisResult with all analysis data
        """
        # Parse target date
        if target_date is None:
            target_date_obj = date.today()
            target_date = target_date_obj.isoformat()
        else:
            target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()

        # Get baby config and age
        baby_config = self.config_service.get_baby_config(user_id)
        baby_age_days = None
        if baby_config and baby_config.birth_date:
            baby_age_days = baby_config.get_age_days(target_date_obj)

        # Get feeding records for the day
        records = self.record_service.list_daily_records(user_id, target_date)
        feeding_records = [r for r in records if r.type == "feeding"]

        # Calculate metrics
        feeding_data = self._calculate_feeding_data(feeding_records)

        # Analyze against standards
        metrics = {}
        issues = []

        if baby_age_days:
            # Analyze milk volume
            milk_analysis = self.analyze_milk_volume(
                feeding_data["total_milk"], baby_age_days
            )
            metrics["milk_volume"] = milk_analysis

            # Analyze frequency
            frequency_analysis = self.analyze_feeding_frequency(
                feeding_data["feeding_count"], baby_age_days
            )
            metrics["feeding_frequency"] = frequency_analysis

            # Analyze interval
            if feeding_data["avg_interval"]:
                interval_analysis = self.analyze_intervals(
                    feeding_data["avg_interval"], baby_age_days
                )
                metrics["interval"] = interval_analysis

            # Identify issues
            issues = self.identify_issues(metrics, feeding_data)

        # Determine overall status
        overall_status = self._determine_overall_status(metrics)

        # Generate recommendations
        recommendations = self.generate_recommendations(metrics, issues, feeding_data, baby_age_days)

        # Calculate next feeding suggestion
        next_feeding = self.calculate_next_feeding(feeding_records, baby_age_days)

        return AnalysisResult(
            status=overall_status,
            confidence=0.8 if baby_age_days else 0.3,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            baby_age_days=baby_age_days,
            next_feeding_suggestion=next_feeding,
            feeding_data_summary=feeding_data,
        )

    def _calculate_feeding_data(self, feeding_records: List[Any]) -> Dict[str, Any]:
        """Calculate feeding data from records"""
        total_milk = sum(r.details.get("amount_ml", 0) for r in feeding_records)
        feeding_count = len(feeding_records)

        # Calculate intervals
        intervals = []
        if len(feeding_records) >= 2:
            timestamps = sorted([r.timestamp for r in feeding_records])
            for i in range(1, len(timestamps)):
                interval = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600
                intervals.append(interval)

        avg_interval = sum(intervals) / len(intervals) if intervals else None
        max_interval = max(intervals) if intervals else None

        # Determine feeding types
        breast_count = sum(1 for r in feeding_records if r.details.get("feeding_type") == "breast")
        formula_count = sum(1 for r in feeding_records if r.details.get("feeding_type") in ["formula", "water_formula"])

        return {
            "total_milk": total_milk,
            "feeding_count": feeding_count,
            "avg_interval": avg_interval,
            "max_interval": max_interval,
            "intervals": intervals,
            "breast_count": breast_count,
            "formula_count": formula_count,
        }

    def analyze_milk_volume(self, volume_ml: float, age_days: int) -> MetricAnalysis:
        """Analyze milk volume against standards"""
        standard = get_standard_for_day(age_days, "milk_volume_ml")

        if not standard:
            return MetricAnalysis(
                value=volume_ml,
                min=0, max=0, avg=0,
                status=Status.NORMAL,
                description="无标准数据参考"
            )

        status = Status.NORMAL
        diff_percent = None

        if volume_ml < standard["min"]:
            status = Status.LOW
            diff_percent = ((standard["min"] - volume_ml) / standard["min"]) * 100
        elif volume_ml > standard["max"]:
            status = Status.HIGH
            diff_percent = ((volume_ml - standard["max"]) / standard["max"]) * 100

        return MetricAnalysis(
            value=volume_ml,
            min=standard["min"],
            max=standard["max"],
            avg=standard["avg"],
            status=status,
            difference_percent=diff_percent,
            description=self._describe_metric("奶量", volume_ml, standard, status)
        )

    def analyze_feeding_frequency(self, count: int, age_days: int) -> MetricAnalysis:
        """Analyze feeding frequency against standards"""
        standard = get_standard_for_day(age_days, "feeding_times")

        if not standard:
            return MetricAnalysis(
                value=count,
                min=0, max=0, avg=0,
                status=Status.NORMAL,
                description="无标准数据参考"
            )

        status = Status.NORMAL
        diff_percent = None

        if count < standard["min"]:
            status = Status.LOW
            diff_percent = ((standard["min"] - count) / standard["min"]) * 100
        elif count > standard["max"]:
            status = Status.HIGH
            diff_percent = ((count - standard["max"]) / standard["max"]) * 100

        return MetricAnalysis(
            value=count,
            min=standard["min"],
            max=standard["max"],
            avg=standard["avg"],
            status=status,
            difference_percent=diff_percent,
            description=self._describe_metric("喂养次数", count, standard, status)
        )

    def analyze_intervals(self, avg_interval: float, age_days: int) -> MetricAnalysis:
        """Analyze feeding interval against standards"""
        standard = get_standard_for_day(age_days, "interval_hours")

        if not standard:
            return MetricAnalysis(
                value=avg_interval,
                min=0, max=0, avg=0,
                status=Status.NORMAL,
                description="无标准数据参考"
            )

        status = Status.NORMAL
        diff_percent = None

        # Interval is problematic if too long (not enough feedings)
        if avg_interval > standard["max"]:
            status = Status.HIGH
            diff_percent = ((avg_interval - standard["max"]) / standard["max"]) * 100
        elif avg_interval < standard["min"]:
            status = Status.LOW
            diff_percent = ((standard["min"] - avg_interval) / standard["min"]) * 100

        return MetricAnalysis(
            value=avg_interval,
            min=standard["min"],
            max=standard["max"],
            avg=standard["avg"],
            status=status,
            difference_percent=diff_percent,
            description=self._describe_metric("喂养间隔", avg_interval, standard, status, unit="小时")
        )

    def identify_issues(
        self,
        metrics: Dict[str, MetricAnalysis],
        feeding_data: Dict[str, Any]
    ) -> List[Issue]:
        """Identify feeding issues from analysis"""
        issues = []

        # Low milk volume
        if "milk_volume" in metrics and metrics["milk_volume"].status == Status.LOW:
            diff = metrics["milk_volume"].difference_percent or 0
            severity = "high" if diff > 25 else "medium" if diff > 15 else "low"
            issues.append(Issue(
                type="low_milk_volume",
                severity=severity,
                description=f"今日奶量{feeding_data['total_milk']}ml，低于建议下限约{diff:.0f}%",
                metric="milk_volume"
            ))

        # High milk volume
        if "milk_volume" in metrics and metrics["milk_volume"].status == Status.HIGH:
            issues.append(Issue(
                type="high_milk_volume",
                severity="low",
                description=f"今日奶量{feeding_data['total_milk']}ml，高于建议上限",
                metric="milk_volume"
            ))

        # Low frequency
        if "feeding_frequency" in metrics and metrics["feeding_frequency"].status == Status.LOW:
            issues.append(Issue(
                type="low_frequency",
                severity="medium",
                description=f"今日喂养{feeding_data['feeding_count']}次，次数偏少",
                metric="feeding_frequency"
            ))

        # Long interval
        if "interval" in metrics and metrics["interval"].status == Status.HIGH:
            issues.append(Issue(
                type="long_interval",
                severity="medium",
                description=f"平均喂养间隔{feeding_data['avg_interval']:.1f}小时，间隔偏长",
                metric="interval"
            ))

        # Max interval too long (no feeding for extended period)
        if feeding_data.get("max_interval") and feeding_data["max_interval"] > 5:
            issues.append(Issue(
                type="extended_gap",
                severity="high",
                description=f"最长喂养间隔{feeding_data['max_interval']:.1f}小时，建议缩短间隔",
                metric="interval"
            ))

        return issues

    def generate_recommendations(
        self,
        metrics: Dict[str, MetricAnalysis],
        issues: List[Issue],
        feeding_data: Dict[str, Any],
        age_days: Optional[int]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if not issues:
            recommendations.append("喂养情况良好，继续保持当前节奏")
            return recommendations

        for issue in issues:
            if issue.type == "low_milk_volume":
                if age_days:
                    standard = get_standard_for_day(age_days, "milk_volume_ml")
                    if standard:
                        suggested = standard["min"]
                        diff = suggested - feeding_data["total_milk"]
                        recommendations.append(f"建议增加奶量，每日目标{suggested}ml，可每次增加{diff // feeding_data['feeding_count'] + 20}ml")

            elif issue.type == "low_frequency":
                recommendations.append("建议增加喂养次数，可在夜间增加1-2次")

            elif issue.type == "long_interval":
                recommendations.append("建议缩短喂养间隔至3小时左右，避免宝宝过度饥饿")

            elif issue.type == "extended_gap":
                recommendations.append("注意观察宝宝饥饿信号，避免长时间未喂养")

            elif issue.type == "high_milk_volume":
                recommendations.append("奶量充足，注意观察宝宝是否有吐奶或腹胀")

        # Add general advice
        if any(i.severity == "high" for i in issues):
            recommendations.append("如有疑虑，建议咨询儿科医生")

        return recommendations

    def calculate_next_feeding(
        self,
        feeding_records: List[Any],
        age_days: Optional[int]
    ) -> Optional[datetime]:
        """Calculate suggested next feeding time"""
        if not feeding_records:
            return None

        # Get last feeding time
        last_feeding = max(r.timestamp for r in feeding_records)

        # Get suggested interval
        if age_days:
            standard = get_standard_for_day(age_days, "interval_hours")
            interval = standard["avg"] if standard else 3.5
        else:
            interval = 3.5

        next_feeding = last_feeding + timedelta(hours=interval)
        return next_feeding

    def _determine_overall_status(self, metrics: Dict[str, MetricAnalysis]) -> Status:
        """Determine overall analysis status"""
        if not metrics:
            return Status.NORMAL

        statuses = [m.status for m in metrics.values()]

        if any(s == Status.LOW for s in statuses):
            return Status.LOW
        if any(s == Status.HIGH for s in statuses):
            return Status.HIGH
        return Status.NORMAL

    def _describe_metric(
        self,
        name: str,
        value: float,
        standard: Dict[str, float],
        status: Status,
        unit: str = ""
    ) -> str:
        """Generate description for a metric"""
        if status == Status.NORMAL:
            return f"{name}{value}{unit}，处于正常范围"
        elif status == Status.LOW:
            return f"{name}{value}{unit}，低于标准范围({standard['min']}-{standard['max']}{unit})"
        else:
            return f"{name}{value}{unit}，高于标准范围({standard['min']}-{standard['max']}{unit})"