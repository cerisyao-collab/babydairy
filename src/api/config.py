"""Configuration management API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from src.db.session import get_db
from src.api.auth import get_current_user
from src.models.user import User
from src.models.baby_config import GENDERS, FEEDING_TYPES
from src.services.config_service import ConfigService

router = APIRouter()


class BabyConfigResponse(BaseModel):
    baby_name: str
    birth_date: Optional[str] = None
    age_days: Optional[int] = None
    gender: Optional[str] = None
    birth_weight: Optional[float] = None
    feeding_type: Optional[str] = None
    updated_at: str


class UpdateBabyConfigRequest(BaseModel):
    baby_name: Optional[str] = Field(None, description="Baby's nickname")
    birth_date: Optional[str] = Field(None, description="Birth date (YYYY-MM-DD)")
    gender: Optional[str] = Field(None, description=f"Gender: {GENDERS}")
    birth_weight: Optional[float] = Field(None, description="Birth weight in kg")
    feeding_type: Optional[str] = Field(None, description=f"Feeding type: {FEEDING_TYPES}")


@router.get("/baby", response_model=BabyConfigResponse, summary="Get baby configuration")
async def get_baby_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get baby's configuration including birth date and nickname.

    **Returns:**
    - baby_name: Baby's nickname
    - birth_date: Birth date if set
    - age_days: Current age in days if birth_date set
    - gender: Baby's gender
    - birth_weight: Birth weight in kg
    - feeding_type: Feeding type (breast/formula/mixed)
    """
    service = ConfigService(db)
    config = service.get_baby_config(str(current_user.id))

    if config is None:
        return BabyConfigResponse(
            baby_name="宝宝",
            birth_date=None,
            age_days=None,
            gender="unknown",
            birth_weight=None,
            feeding_type="mixed",
            updated_at=datetime.utcnow().isoformat(),
        )

    age_days = service.get_age_days(str(current_user.id))

    return BabyConfigResponse(
        baby_name=config.baby_name,
        birth_date=config.birth_date.isoformat() if config.birth_date else None,
        age_days=age_days,
        gender=config.gender,
        birth_weight=config.birth_weight,
        feeding_type=config.feeding_type,
        updated_at=config.updated_at.isoformat(),
    )


@router.put("/baby", response_model=BabyConfigResponse, summary="Update baby configuration")
async def update_baby_config(
    request: UpdateBabyConfigRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update baby's configuration.

    **Fields:**
    - baby_name: Baby's nickname (optional)
    - birth_date: Birth date in YYYY-MM-DD format (optional)
    - gender: Gender - male/female/unknown (optional)
    - birth_weight: Birth weight in kg (optional)
    - feeding_type: Feeding type - breast/formula/mixed (optional)

    **Note:** Birth date is used for growth standard comparisons.
    """
    try:
        service = ConfigService(db)

        # Validate fields
        if request.gender and request.gender not in GENDERS:
            raise ValueError(f"Invalid gender: {request.gender}. Must be one of {GENDERS}")
        if request.feeding_type and request.feeding_type not in FEEDING_TYPES:
            raise ValueError(f"Invalid feeding_type: {request.feeding_type}. Must be one of {FEEDING_TYPES}")

        config = service.set_baby_config(
            user_id=str(current_user.id),
            baby_name=request.baby_name,
            birth_date=request.birth_date,
            gender=request.gender,
            birth_weight=request.birth_weight,
            feeding_type=request.feeding_type,
        )

        age_days = service.get_age_days(str(current_user.id))

        return BabyConfigResponse(
            baby_name=config.baby_name,
            birth_date=config.birth_date.isoformat() if config.birth_date else None,
            age_days=age_days,
            gender=config.gender,
            birth_weight=config.birth_weight,
            feeding_type=config.feeding_type,
            updated_at=config.updated_at.isoformat(),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Import datetime for default timestamp
from datetime import datetime