"""Daily summary generation service"""

from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from collections import defaultdict

from src.models.record import Record, RECORD_TYPE_NAMES
from src.models.baby_config import BabyConfig
from src.services.record_service import RecordService
from src.services.config_service import ConfigService
from src.services.standards_service import get_standard_for_day


class SummaryService:
    """Service for generating daily summary reports"""

    def __init__(self, db: Session):
        self.db = db
        self.record_service = RecordService(db)
        self.config_service = ConfigService(db)

    def generate_ai_summary(
        self,
        user_id: str,
        target_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate AI-powered daily summary with analysis.

        Args:
            user_id: User's UUID
            target_date: Date string (YYYY-MM-DD), defaults to today

        Returns:
            Dict containing:
            - summary: Formatted summary text
            - ai_analysis: AI-generated analysis text
            - feeding_data: Feeding data summary
            - recommendations: List of recommendations
        """
        from src.services.ai_analyzer import FeedingAnalyzer
        from src.services.llm_service import LLMService

        # Parse date
        if target_date is None:
            target_date_obj = date.today()
            target_date = target_date_obj.isoformat()
        else:
            target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()

        # Get traditional summary
        traditional_summary = self.generate_daily_summary(user_id, target_date)

        # Run AI analysis
        analyzer = FeedingAnalyzer(self.db)
        analysis = analyzer.analyze(user_id, target_date)

        # Generate AI summary text
        ai_summary = None
        try:
            llm_service = LLMService()
            ai_summary = llm_service.generate_daily_report_summary(
                analysis.feeding_data_summary,
                analysis
            )
        except Exception:
            # Fallback to rule-based summary
            if analysis.issues:
                ai_summary = f"发现{len(analysis.issues)}个问题，{analysis.recommendations[0] if analysis.recommendations else '请关注喂养情况'}"
            else:
                ai_summary = "喂养情况良好，继续保持当前节奏"

        return {
            "summary": traditional_summary,
            "ai_analysis": ai_summary,
            "feeding_data": analysis.feeding_data_summary,
            "recommendations": analysis.recommendations,
            "status": analysis.status.value,
            "next_feeding": analysis.next_feeding_suggestion.isoformat() if analysis.next_feeding_suggestion else None,
        }

    def generate_daily_summary(
        self,
        user_id: str,
        target_date: Optional[str] = None,
        birth_date: Optional[str] = None,
    ) -> str:
        """
        Generate formatted daily summary report

        Args:
            user_id: User's UUID
            target_date: Date string (YYYY-MM-DD), defaults to today
            birth_date: Baby birth date override (YYYY-MM-DD)

        Returns:
            Formatted summary string
        """
        # Parse date
        if target_date is None:
            target_date_obj = date.today()
            target_date = target_date_obj.isoformat()
        else:
            target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()

        # Get records for the day
        records = self.record_service.list_daily_records(user_id, target_date)

        if not records:
            return f"【{target_date}】 今日无记录\n\n请先添加宝宝的日常记录。"

        # Get baby config
        baby_config = self.config_service.get_baby_config(user_id)

        # Calculate birth day
        birth_day = None
        if birth_date:
            try:
                bd = datetime.strptime(birth_date, "%Y-%m-%d").date()
                birth_day = self._get_birth_day(bd, target_date_obj)
            except ValueError:
                pass
        elif baby_config and baby_config.birth_date:
            birth_day = self._get_birth_day(baby_config.birth_date, target_date_obj)

        # Get baby name
        baby_name = "宝宝"
        if baby_config and baby_config.baby_name:
            baby_name = baby_config.baby_name

        # Build summary
        return self._format_summary(records, target_date, birth_day, baby_name)

    def _get_birth_day(self, birth_date: date, target_date: date) -> int:
        """Calculate baby's age in days"""
        delta = target_date - birth_date
        return delta.days + 1  # Birth day is day 1

    def _format_summary(
        self,
        records: List[Record],
        target_date: str,
        birth_day: Optional[int],
        baby_name: str,
    ) -> str:
        """Format summary report"""
        # Group records by type
        stats = defaultdict(list)
        for r in records:
            stats[r.type].append(r)

        lines = []
        lines.append(f"【{target_date}】 {baby_name}每日近况总结")

        if birth_day:
            lines.append(f"出生天数：第 {birth_day} 天")
        else:
            lines.append("出生天数：未知（请设置宝宝出生日期）")

        lines.append("")
        lines.append(f"今日记录总数：{len(records)} 条")
        lines.append("")

        # Feeding section
        feeding_records = stats["feeding"]
        if feeding_records:
            lines.append("🍼 喂养情况")
            total_feeding = len(feeding_records)
            total_milk = sum(r.details.get("amount_ml", 0) for r in feeding_records)
            breast_count = sum(1 for r in feeding_records if r.details.get("feeding_type") == "breast")
            formula_count = sum(1 for r in feeding_records if r.details.get("feeding_type") in ["formula", "water_formula"])

            lines.append(f"  喂养次数：{total_feeding} 次")
            if total_milk > 0:
                lines.append(f"  总奶量：{total_milk} ml")
            if breast_count > 0:
                lines.append(f"  亲喂：{breast_count} 次")
            if formula_count > 0:
                lines.append(f"  瓶喂：{formula_count} 次")

            if birth_day:
                std_feeding = self._get_standard_for_day(birth_day, "feeding_times")
                std_milk = self._get_standard_for_day(birth_day, "milk_volume_ml")
                if std_feeding:
                    feeding_analysis = self._compare_with_standards(total_feeding, std_feeding)
                    lines.append(f"  对比标准：{feeding_analysis['status']} ({feeding_analysis['difference']})")
                    lines.append(f"  建议：{feeding_analysis['advice']}")
            lines.append("")

        # Excretion section
        urine_records = stats["urine"]
        bowel_records = stats["bowel"]

        if urine_records or bowel_records:
            urine_count = sum(r.details.get("count", 1) for r in urine_records)
            bowel_count = len(bowel_records)

            lines.append("💩 排泄情况")
            if urine_records:
                lines.append(f"  小便：{urine_count} 次")
            if bowel_records:
                colors = [r.details.get("color", "") for r in bowel_records if r.details.get("color")]
                colors_str = ", ".join(colors) if colors else ""
                lines.append(f"  大便：{bowel_count} 次" + (f" ({colors_str})" if colors_str else ""))

            if birth_day:
                if urine_records:
                    std_urine = self._get_standard_for_day(birth_day, "urine_count")
                    if std_urine:
                        urine_analysis = self._compare_with_standards(urine_count, std_urine)
                        lines.append(f"  排尿对比：{urine_analysis['status']} ({urine_analysis['difference']})")
                if bowel_records:
                    std_bowel = self._get_standard_for_day(birth_day, "bowel_count")
                    if std_bowel:
                        bowel_analysis = self._compare_with_standards(bowel_count, std_bowel)
                        lines.append(f"  大便对比：{bowel_analysis['status']} ({bowel_analysis['difference']})")
            lines.append("")

        # Growth section
        growth_records = stats["growth"]
        if growth_records:
            lines.append("📏 生长指标")
            for r in growth_records:
                details = r.details
                ts = r.timestamp.strftime("%Y-%m-%d %H:%M")
                parts = []
                if "weight_kg" in details:
                    parts.append(f"体重 {details['weight_kg']} kg")
                if "height_cm" in details:
                    parts.append(f"身长 {details['height_cm']} cm")
                if "temperature" in details:
                    parts.append(f"体温 {details['temperature']}°C")
                if parts:
                    lines.append(f"  [{ts}] {', '.join(parts)}")

                if birth_day:
                    if "weight_kg" in details:
                        std_weight = self._get_standard_for_day(birth_day, "weight_kg")
                        if std_weight:
                            weight_analysis = self._compare_with_standards(details["weight_kg"], std_weight)
                            lines.append(f"    体重评估：{weight_analysis['status']} - {weight_analysis['advice']}")
                    if "height_cm" in details:
                        std_height = self._get_standard_for_day(birth_day, "height_cm")
                        if std_height:
                            height_analysis = self._compare_with_standards(details["height_cm"], std_height)
                            lines.append(f"    身长评估：{height_analysis['status']} - {height_analysis['advice']}")
            lines.append("")

        # Other sections
        if stats["medication"]:
            lines.append("💊 营养品")
            for r in stats["medication"]:
                details = r.details
                name = details.get("name", "")
                dosage = details.get("dosage", "")
                if name:
                    lines.append(f"  {name}: {dosage}")
            lines.append("")

        if stats["bathing"]:
            lines.append("🛁 洗澡")
            lines.append(f"  {len(stats['bathing'])} 次")
            lines.append("")

        if stats["sleep"]:
            lines.append("😴 睡眠")
            lines.append(f"  {len(stats['sleep'])} 条记录")
            lines.append("")

        if stats["illness"]:
            lines.append("🤒 病情")
            for r in stats["illness"]:
                details = r.details
                symptom = details.get("symptom", "")
                if symptom:
                    lines.append(f"  症状：{symptom}")
            lines.append("")

        # Final advice
        lines.append("💡 综合建议")
        lines.append("  以上数据仅供参考，每个宝宝都有自己的成长节奏。")
        lines.append("  如有疑虑，请咨询儿科医生。")

        return "\n".join(lines)

    def _get_standard_for_day(self, day: int, metric: str) -> Optional[Dict[str, Any]]:
        """Get feeding standard for a specific day from standards data"""
        return get_standard_for_day(day, metric)

    def _compare_with_standards(
        self,
        actual: float,
        standard: Dict[str, Any],
        metric_name: str = "",
    ) -> Dict[str, str]:
        """Compare actual value with standard range"""
        min_val = standard.get("min", 0)
        max_val = standard.get("max", 0)

        if actual < min_val:
            diff = ((min_val - actual) / min_val) * 100 if min_val > 0 else 0
            return {
                "status": "偏低",
                "advice": "略低于标准范围，请持续关注，必要时咨询医生",
                "difference": f"低于标准下限约 {diff:.1f}%",
            }
        elif actual > max_val:
            diff = ((actual - max_val) / max_val) * 100 if max_val > 0 else 0
            return {
                "status": "偏高",
                "advice": "略高于标准范围，请持续关注，必要时咨询医生",
                "difference": f"高于标准上限约 {diff:.1f}%",
            }
        else:
            return {
                "status": "正常",
                "advice": "发育良好，继续保持",
                "difference": f"在标准范围内 ({min_val}-{max_val})",
            }