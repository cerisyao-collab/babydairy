"""Daily summary API endpoints"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from src.db.session import get_db
from src.api.auth import get_current_user
from src.models.user import User
from src.services.summary_service import SummaryService

router = APIRouter()


class SummaryResponse(BaseModel):
    date: str
    summary: str


class AISummaryResponse(BaseModel):
    date: str
    summary: str
    ai_analysis: Optional[str] = None
    feeding_data: Dict[str, Any]
    recommendations: List[str]
    status: str
    next_feeding: Optional[str] = None


@router.get("/daily", response_model=SummaryResponse, summary="Get daily summary")
async def get_daily_summary(
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to today"),
    birth_date: Optional[str] = Query(None, description="Override birth date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate daily summary report for baby's activities.

    **Features:**
    - Feeding count and milk volume summary
    - Excretion (urine/bowel) statistics
    - Growth metrics tracking
    - Comparison with standard values (if birth_date set)

    **Output format:** Text report suitable for display in mini-program.
    """
    service = SummaryService(db)
    summary = service.generate_daily_summary(
        user_id=str(current_user.id),
        target_date=date,
        birth_date=birth_date,
    )

    target_date = date or datetime.utcnow().strftime("%Y-%m-%d")

    return SummaryResponse(
        date=target_date,
        summary=summary,
    )


@router.get("/daily/ai", response_model=AISummaryResponse, summary="Get AI-enhanced daily summary")
async def get_ai_daily_summary(
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to today"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate AI-enhanced daily summary with personalized analysis.

    **Features:**
    - Traditional formatted summary
    - AI-generated analysis text
    - Feeding data summary
    - Personalized recommendations
    - Suggested next feeding time

    **Output format:** Structured report with AI insights.
    """
    service = SummaryService(db)
    result = service.generate_ai_summary(
        user_id=str(current_user.id),
        target_date=date,
    )

    target_date = date or datetime.utcnow().strftime("%Y-%m-%d")

    return AISummaryResponse(
        date=target_date,
        summary=result["summary"],
        ai_analysis=result["ai_analysis"],
        feeding_data=result["feeding_data"],
        recommendations=result["recommendations"],
        status=result["status"],
        next_feeding=result["next_feeding"],
    )


# Import datetime for default date
from datetime import datetime