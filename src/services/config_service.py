"""Baby configuration management service"""

from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import Optional
import uuid

from src.models.baby_config import BabyConfig


class ConfigService:
    """Service for managing baby configuration"""

    def __init__(self, db: Session):
        self.db = db

    def get_baby_config(self, user_id: str) -> Optional[BabyConfig]:
        """
        Get baby configuration for a user

        Args:
            user_id: User's UUID

        Returns:
            BabyConfig object if exists, None otherwise
        """
        return self.db.query(BabyConfig).filter(
            BabyConfig.user_id == uuid.UUID(user_id)
        ).first()

    def set_baby_config(
        self,
        user_id: str,
        baby_name: Optional[str] = None,
        birth_date: Optional[str] = None,
        gender: Optional[str] = None,
        birth_weight: Optional[float] = None,
        feeding_type: Optional[str] = None,
    ) -> BabyConfig:
        """
        Set or update baby configuration

        Args:
            user_id: User's UUID
            baby_name: Baby's nickname
            birth_date: Birth date string (YYYY-MM-DD)
            gender: Baby's gender (male/female/unknown)
            birth_weight: Birth weight in kg
            feeding_type: Feeding type (breast/formula/mixed)

        Returns:
            Updated BabyConfig object

        Raises:
            ValueError: If date format is invalid
        """
        # Validate date format
        if birth_date:
            try:
                datetime.strptime(birth_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"无效的日期格式：{birth_date}，请使用 YYYY-MM-DD 格式")

        # Get existing config or create new
        config = self.get_baby_config(user_id)

        if config is None:
            config = BabyConfig(
                id=uuid.uuid4(),
                user_id=uuid.UUID(user_id),
                baby_name=baby_name or "宝宝",
                birth_date=date.fromisoformat(birth_date) if birth_date else None,
                gender=gender or "unknown",
                birth_weight=birth_weight,
                feeding_type=feeding_type or "mixed",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self.db.add(config)
        else:
            if baby_name is not None:
                config.baby_name = baby_name
            if birth_date is not None:
                config.birth_date = date.fromisoformat(birth_date)
            if gender is not None:
                config.gender = gender
            if birth_weight is not None:
                config.birth_weight = birth_weight
            if feeding_type is not None:
                config.feeding_type = feeding_type
            config.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(config)

        return config

    def get_age_days(self, user_id: str, target_date: Optional[date] = None) -> Optional[int]:
        """
        Calculate baby's age in days

        Args:
            user_id: User's UUID
            target_date: Target date, defaults to today

        Returns:
            Age in days if birth_date is set, None otherwise
        """
        config = self.get_baby_config(user_id)

        if config is None or config.birth_date is None:
            return None

        if target_date is None:
            target_date = date.today()

        delta = target_date - config.birth_date
        return delta.days + 1  # Birth day is day 1