"""AI analysis API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.db.session import get_db
from src.api.auth import get_current_user
from src.models.user import User
from src.services.ai_analyzer import FeedingAnalyzer, AnalysisResult, Status, MetricAnalysis, Issue
from src.services.llm_service import LLMService


router = APIRouter()


# Request/Response models
class AnalyzeRequest(BaseModel):
    date: Optional[str] = Field(None, description="Date to analyze (YYYY-MM-DD), defaults to today")


class MetricAnalysisResponse(BaseModel):
    value: float
    min: float
    max: float
    avg: float
    status: str
    difference_percent: Optional[float] = None
    description: str


class IssueResponse(BaseModel):
    type: str
    severity: str
    description: str
    metric: str


class AnalyzeResponse(BaseModel):
    status: str
    confidence: float
    metrics: Dict[str, MetricAnalysisResponse]
    issues: List[IssueResponse]
    recommendations: List[str]
    ai_summary: Optional[str] = None
    next_feeding_suggestion: Optional[str] = None
    baby_age_days: Optional[int] = None
    feeding_data_summary: Dict[str, Any]


class ChatRequest(BaseModel):
    question: str = Field(..., description="User's question about feeding")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context (baby info, feeding data)")


class ChatResponse(BaseModel):
    response: str


def analysis_to_response(analysis: AnalysisResult, ai_summary: Optional[str] = None) -> AnalyzeResponse:
    """Convert AnalysisResult to response format"""
    metrics_response = {}
    for key, metric in analysis.metrics.items():
        metrics_response[key] = MetricAnalysisResponse(
            value=metric.value,
            min=metric.min,
            max=metric.max,
            avg=metric.avg,
            status=metric.status.value,
            difference_percent=metric.difference_percent,
            description=metric.description,
        )

    issues_response = [
        IssueResponse(
            type=issue.type,
            severity=issue.severity,
            description=issue.description,
            metric=issue.metric,
        )
        for issue in analysis.issues
    ]

    next_feeding_str = None
    if analysis.next_feeding_suggestion:
        next_feeding_str = analysis.next_feeding_suggestion.isoformat()

    return AnalyzeResponse(
        status=analysis.status.value,
        confidence=analysis.confidence,
        metrics=metrics_response,
        issues=issues_response,
        recommendations=analysis.recommendations,
        ai_summary=ai_summary,
        next_feeding_suggestion=next_feeding_str,
        baby_age_days=analysis.baby_age_days,
        feeding_data_summary=analysis.feeding_data_summary,
    )


@router.post("/analyze", response_model=AnalyzeResponse, summary="Analyze feeding data")
async def analyze_feeding(
    request: AnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyze feeding data for a specific date using AI.

    **Returns:**
    - status: Overall feeding status (normal/low/high)
    - confidence: Analysis confidence level
    - metrics: Detailed analysis for each metric (milk volume, frequency, interval)
    - issues: List of identified issues
    - recommendations: Actionable suggestions
    - ai_summary: AI-generated summary text
    - next_feeding_suggestion: Suggested next feeding time
    - baby_age_days: Baby's age in days
    - feeding_data_summary: Summary of feeding data analyzed

    **Note:** Requires baby birth_date to be set for age-based analysis.
    """
    try:
        # Run rule-based analysis
        analyzer = FeedingAnalyzer(db)
        analysis = analyzer.analyze(
            user_id=str(current_user.id),
            target_date=request.date,
        )

        # Generate AI summary using LLM
        ai_summary = None
        try:
            llm_service = LLMService()
            ai_summary = llm_service.generate_analysis_text(analysis)
        except Exception as e:
            # LLM failed, use fallback summary
            ai_summary = analysis.feeding_data_summary.get("fallback_summary")

        return analysis_to_response(analysis, ai_summary)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )


@router.post("/chat", response_model=ChatResponse, summary="Chat with AI assistant")
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Chat with AI feeding assistant.

    **Input:**
    - question: User's question about feeding
    - context: Optional additional context (baby_age_days, today_milk, feeding_count)

    **Returns:**
    - response: AI-generated response to the question

    **Note:** This is for informational purposes only, not medical advice.
    """
    try:
        # If context not provided, get from user's data
        context = request.context or {}

        if not context:
            # Get baby config and today's feeding data
            from src.services.config_service import ConfigService
            from src.services.record_service import RecordService
            from datetime import date as date_type

            config_service = ConfigService(db)
            baby_config = config_service.get_baby_config(str(current_user.id))

            if baby_config and baby_config.birth_date:
                context["baby_age_days"] = baby_config.get_age_days(date_type.today())

            # Get today's feeding summary
            record_service = RecordService(db)
            records = record_service.list_daily_records(str(current_user.id))
            feeding_records = [r for r in records if r.type == "feeding"]

            if feeding_records:
                total_milk = sum(r.details.get("amount_ml", 0) for r in feeding_records)
                context["today_milk"] = total_milk
                context["feeding_count"] = len(feeding_records)

        # Generate response using LLM
        llm_service = LLMService()
        response = llm_service.chat(request.question, context)

        return ChatResponse(response=response)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}",
        )