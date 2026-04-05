"""Record management API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

from src.db.session import get_db
from src.api.auth import get_current_user
from src.models.user import User
from src.models.record import RECORD_TYPES, RECORD_TYPE_NAMES
from src.services.record_service import RecordService, DuplicateRecordError

router = APIRouter()


# Request/Response models
class RecordDetails(BaseModel):
    """Flexible record details structure"""
    feeding_type: Optional[str] = None
    duration_minutes: Optional[int] = None
    amount_ml: Optional[int] = None
    side: Optional[str] = None
    count: Optional[int] = None
    amount: Optional[str] = None
    type: Optional[str] = None
    color: Optional[str] = None
    name: Optional[str] = None
    dosage: Optional[str] = None
    notes: Optional[str] = None
    water_temperature: Optional[str] = None
    sleep_start: Optional[str] = None
    sleep_end: Optional[str] = None
    nap: Optional[bool] = None
    temperature: Optional[float] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    symptom: Optional[str] = None
    cause: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    severity: Optional[str] = None
    hospital_visit: Optional[bool] = None

    class Config:
        extra = "allow"  # Allow additional fields


class CreateRecordRequest(BaseModel):
    type: str = Field(..., description=f"Record type: {RECORD_TYPES}")
    details: RecordDetails
    timestamp: Optional[str] = Field(None, description="ISO timestamp, defaults to now")
    images: Optional[List[str]] = None
    skip_duplicate_check: Optional[bool] = False


class RecordResponse(BaseModel):
    id: str
    type: str
    type_name: str
    timestamp: str
    date: str
    details: dict
    images: List[str]
    created_at: str
    updated_at: str


class DuplicateWarningResponse(BaseModel):
    warning: str
    similar_records: List[RecordResponse]
    message: str


class RecordListResponse(BaseModel):
    total: int
    records: List[RecordResponse]


def record_to_response(record) -> RecordResponse:
    """Convert Record model to response format"""
    return RecordResponse(
        id=str(record.id),
        type=record.type,
        type_name=RECORD_TYPE_NAMES.get(record.type, record.type),
        timestamp=record.timestamp.isoformat(),
        date=record.date.isoformat(),
        details=record.details,
        images=record.images,
        created_at=record.created_at.isoformat(),
        updated_at=record.updated_at.isoformat(),
    )


@router.post("/", response_model=RecordResponse, summary="Create a new record")
async def create_record(
    request: CreateRecordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new baby diary record.

    **Record Types:**
    - feeding: 喂奶
    - bowel: 大便
    - urine: 小便
    - medication: 营养品
    - bathing: 洗澡
    - sleep: 睡眠
    - growth: 生长指标
    - illness: 病情
    """
    try:
        service = RecordService(db)
        record = service.create_record(
            user_id=str(current_user.id),
            record_type=request.type,
            details=request.details.model_dump(exclude_none=True),
            timestamp=request.timestamp,
            images=request.images,
            skip_duplicate_check=request.skip_duplicate_check,
        )
        return record_to_response(record)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except DuplicateRecordError as e:
        similar = [record_to_response(r) for r in e.similar_records]
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "warning": "duplicate_detected",
                "similar_records": similar,
                "message": f"Found {len(similar)} similar records in time window. Set skip_duplicate_check=true to proceed.",
            },
        )


@router.get("/", response_model=RecordListResponse, summary="List records by date range")
async def list_records(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    type: Optional[str] = Query(None, description=f"Filter by type: {RECORD_TYPES}"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Query records by date range and type.

    All parameters are optional:
    - Without params: returns all records for current user
    - With date range: returns records within that range
    - With type: filters by specific record type
    """
    service = RecordService(db)
    records = service.query_records(
        user_id=str(current_user.id),
        start_date=start_date,
        end_date=end_date,
        record_type=type,
    )
    return RecordListResponse(
        total=len(records),
        records=[record_to_response(r) for r in records],
    )


@router.get("/daily", response_model=RecordListResponse, summary="List daily records")
async def daily_records(
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to today"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all records for a specific day.

    Defaults to today if date not specified.
    """
    service = RecordService(db)
    records = service.list_daily_records(
        user_id=str(current_user.id),
        date=date,
    )
    return RecordListResponse(
        total=len(records),
        records=[record_to_response(r) for r in records],
    )


@router.get("/{record_id}", response_model=RecordResponse, summary="Get single record")
async def get_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a single record by ID.

    Returns 404 if record doesn't exist or belongs to another user.
    """
    service = RecordService(db)
    record = service.get_record_by_id(str(current_user.id), record_id)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found",
        )

    return record_to_response(record)


@router.put("/{record_id}", response_model=RecordResponse, summary="Update record")
async def update_record(
    record_id: str,
    details: Optional[RecordDetails] = None,
    timestamp: Optional[str] = None,
    images: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing record.

    All fields are optional - only provided fields will be updated.
    """
    try:
        service = RecordService(db)

        update_details = None
        if details is not None:
            update_details = details.model_dump(exclude_none=True)

        record = service.update_record(
            user_id=str(current_user.id),
            record_id=record_id,
            details=update_details,
            timestamp=timestamp,
            images=images,
        )
        return record_to_response(record)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete record")
async def delete_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a record by ID.

    Returns 404 if record doesn't exist or belongs to another user.
    """
    try:
        service = RecordService(db)
        service.delete_record(str(current_user.id), record_id)
        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )