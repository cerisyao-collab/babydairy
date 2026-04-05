"""BabyConfig model for storing baby configuration per user"""

from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, date
from typing import Optional
import uuid

from src.db.session import Base


# Feeding type constants
FEEDING_TYPES = ["breast", "formula", "mixed"]

# Gender constants
GENDERS = ["male", "female", "unknown"]


class BabyConfig(Base):
    """Baby configuration model - one per user"""

    __tablename__ = "baby_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    baby_name = Column(String(64), nullable=True, default="宝宝")
    birth_date = Column(Date, nullable=True)
    gender = Column(String(16), nullable=True, default="unknown")  # male/female/unknown
    birth_weight = Column(Float, nullable=True)  # kg
    feeding_type = Column(String(16), nullable=True, default="mixed")  # breast/formula/mixed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    user = relationship("User", back_populates="baby_config")

    def __repr__(self) -> str:
        return f"<BabyConfig {self.id}: user_id={self.user_id}, baby_name={self.baby_name}, birth_date={self.birth_date}>"

    def get_age_days(self, target_date: Optional[date] = None) -> Optional[int]:
        """Calculate baby's age in days"""
        if self.birth_date is None:
            return None

        if target_date is None:
            target_date = date.today()

        delta = target_date - self.birth_date
        return delta.days + 1  # Birth day is day 1