"""Test data factories for creating test fixtures"""

from datetime import datetime, date
from typing import Optional
import uuid

from sqlalchemy.orm import Session

from src.models.user import User
from src.models.record import Record, RECORD_TYPES
from src.models.baby_config import BabyConfig, FEEDING_TYPES, GENDERS


class UserFactory:
    """Factory for creating test User instances"""

    _counter = 0

    @classmethod
    def create(cls, session: Session, **kwargs) -> User:
        """Create a User with default or custom values"""
        cls._counter += 1

        user = User(
            openid=kwargs.get("openid", f"test_openid_{cls._counter}"),
            nickname=kwargs.get("nickname", f"测试用户{cls._counter}"),
            avatar_url=kwargs.get("avatar_url", "https://example.com/avatar.png"),
            is_active=kwargs.get("is_active", True),
        )

        session.add(user)
        session.flush()
        return user

    @classmethod
    def create_batch(cls, session: Session, count: int, **kwargs) -> list[User]:
        """Create multiple Users"""
        return [cls.create(session, **kwargs) for _ in range(count)]


class RecordFactory:
    """Factory for creating test Record instances"""

    _counter = 0

    @classmethod
    def create(cls, session: Session, user: User, **kwargs) -> Record:
        """Create a Record with default or custom values"""
        cls._counter += 1

        # Default to feeding record
        record_type = kwargs.get("type", "feeding")

        # Default details based on type
        default_details = {
            "feeding": {"amount_ml": 100, "feeding_type": "formula"},
            "bowel": {"color": "yellow", "texture": "normal"},
            "urine": {"count": 1},
            "medication": {"name": "维生素D", "amount": "1滴"},
            "bathing": {"duration_minutes": 15},
            "sleep": {"start_time": "22:00", "end_time": "06:00"},
            "growth": {"weight": 4.0, "height": 55},
            "illness": {"symptom": "轻微感冒", "medication": "无"},
        }

        record = Record(
            user_id=user.id,
            type=record_type,
            timestamp=kwargs.get("timestamp", datetime.now()),
            date=kwargs.get("date", date.today()),
            details=kwargs.get("details", default_details.get(record_type, {})),
            images=kwargs.get("images", None),
        )

        session.add(record)
        session.flush()
        return record

    @classmethod
    def create_batch(cls, session: Session, user: User, count: int, **kwargs) -> list[Record]:
        """Create multiple Records for a user"""
        return [cls.create(session, user, **kwargs) for _ in range(count)]

    @classmethod
    def create_daily_records(cls, session: Session, user: User, target_date: date) -> list[Record]:
        """Create a typical day's worth of records"""
        records = []

        # Morning feeding
        records.append(cls.create(
            session, user,
            type="feeding",
            timestamp=datetime.combine(target_date, datetime.min.time().replace(hour=8)),
            date=target_date,
            details={"amount_ml": 120, "feeding_type": "formula"},
        ))

        # Midday feeding
        records.append(cls.create(
            session, user,
            type="feeding",
            timestamp=datetime.combine(target_date, datetime.min.time().replace(hour=12)),
            date=target_date,
            details={"amount_ml": 150, "feeding_type": "formula"},
        ))

        # Afternoon feeding + urine
        records.append(cls.create(
            session, user,
            type="feeding",
            timestamp=datetime.combine(target_date, datetime.min.time().replace(hour=16)),
            date=target_date,
            details={"amount_ml": 120, "feeding_type": "breast"},
        ))
        records.append(cls.create(
            session, user,
            type="urine",
            timestamp=datetime.combine(target_date, datetime.min.time().replace(hour=16, minute=30)),
            date=target_date,
            details={"count": 1},
        ))

        # Evening feeding + bowel
        records.append(cls.create(
            session, user,
            type="feeding",
            timestamp=datetime.combine(target_date, datetime.min.time().replace(hour=20)),
            date=target_date,
            details={"amount_ml": 100, "feeding_type": "formula"},
        ))
        records.append(cls.create(
            session, user,
            type="bowel",
            timestamp=datetime.combine(target_date, datetime.min.time().replace(hour=20, minute=30)),
            date=target_date,
            details={"color": "yellow", "texture": "normal"},
        ))

        return records


class BabyConfigFactory:
    """Factory for creating test BabyConfig instances"""

    _counter = 0

    @classmethod
    def create(cls, session: Session, user: User, **kwargs) -> BabyConfig:
        """Create a BabyConfig with default or custom values"""
        cls._counter += 1

        config = BabyConfig(
            user_id=user.id,
            baby_name=kwargs.get("baby_name", f"测试宝宝{cls._counter}"),
            birth_date=kwargs.get("birth_date", date(2024, 1, 1)),
            gender=kwargs.get("gender", "male"),
            birth_weight=kwargs.get("birth_weight", 3.5),
            feeding_type=kwargs.get("feeding_type", "mixed"),
        )

        session.add(config)
        session.flush()
        return config