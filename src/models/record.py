"""Record model for storing baby diary records"""

from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from typing import Optional

from src.db.session import Base


# Supported record types (matching existing baby_diary_skill)
RECORD_TYPES = [
    "feeding",      # 喂奶
    "bowel",        # 大便
    "urine",        # 小便
    "medication",   # 营养品
    "bathing",      # 洗澡
    "sleep",        # 睡眠
    "growth",       # 生长指标
    "illness",      # 病情
]

# Record type Chinese names
RECORD_TYPE_NAMES = {
    "feeding": "喂奶",
    "bowel": "大便",
    "urine": "小便",
    "medication": "营养品",
    "bathing": "洗澡",
    "sleep": "睡眠",
    "growth": "生长指标",
    "illness": "病情",
}


class Record(Base):
    """Record model for storing baby diary entries"""

    __tablename__ = "records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(32), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    details = Column(JSONB, nullable=False, default={})
    images = Column(ARRAY(Text), nullable=True, default=[])
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    user = relationship("User", back_populates="records")

    def __repr__(self) -> str:
        return f"<Record {self.id}: type={self.type}, date={self.date}, user_id={self.user_id}>"

    def validate_type(self) -> bool:
        """Validate record type is one of supported types"""
        return self.type in RECORD_TYPES