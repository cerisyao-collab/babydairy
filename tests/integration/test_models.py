"""Integration tests for database models"""

import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session

from src.models.user import User
from src.models.record import Record
from src.models.baby_config import BabyConfig
from tests.fixtures.factories import UserFactory, RecordFactory, BabyConfigFactory


@pytest.mark.integration
class TestUserModel:
    """Integration tests for User model"""

    def test_create_user(self, db_session: Session):
        """Test creating a user in database"""
        user = UserFactory.create(db_session, openid="test_create_user")

        # Verify user was created
        assert user.id is not None
        assert user.openid == "test_create_user"
        assert user.is_active is True

    def test_query_user_by_id(self, db_session: Session):
        """Test querying user by ID"""
        user = UserFactory.create(db_session)

        # Query user
        found_user = db_session.query(User).filter_by(id=user.id).first()

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.openid == user.openid

    def test_query_user_by_openid(self, db_session: Session):
        """Test querying user by openid"""
        user = UserFactory.create(db_session, openid="unique_openid")

        found_user = db_session.query(User).filter_by(openid="unique_openid").first()

        assert found_user is not None
        assert found_user.id == user.id

    def test_user_unique_openid(self, db_session: Session):
        """Test that openid must be unique"""
        UserFactory.create(db_session, openid="same_openid")

        # Try to create another user with same openid
        with pytest.raises(Exception):  # IntegrityError
            user2 = User(openid="same_openid", nickname="Another user")
            db_session.add(user2)
            db_session.flush()

    def test_update_user(self, db_session: Session):
        """Test updating user attributes"""
        user = UserFactory.create(db_session)

        # Update user
        user.nickname = "Updated Nickname"
        user.avatar_url = "https://example.com/new_avatar.png"
        db_session.flush()

        # Verify update
        found_user = db_session.query(User).filter_by(id=user.id).first()
        assert found_user.nickname == "Updated Nickname"

    def test_delete_user(self, db_session: Session):
        """Test deleting user"""
        user = UserFactory.create(db_session)
        user_id = user.id

        db_session.delete(user)
        db_session.flush()

        # Verify deleted
        found_user = db_session.query(User).filter_by(id=user_id).first()
        assert found_user is None


@pytest.mark.integration
class TestRecordModel:
    """Integration tests for Record model"""

    def test_create_record(self, db_session: Session, test_user: User):
        """Test creating a record in database"""
        record = RecordFactory.create(db_session, test_user)

        assert record.id is not None
        assert record.user_id == test_user.id
        assert record.type == "feeding"

    def test_query_records_by_user(self, db_session: Session, test_user: User):
        """Test querying records by user"""
        RecordFactory.create_batch(db_session, test_user, 3)

        records = db_session.query(Record).filter_by(user_id=test_user.id).all()

        assert len(records) == 3

    def test_query_records_by_date(self, db_session: Session, test_user: User):
        """Test querying records by date"""
        target_date = date(2024, 1, 15)
        RecordFactory.create_daily_records(db_session, test_user, target_date)

        # Create records for different date
        RecordFactory.create(
            db_session, test_user,
            date=date(2024, 1, 16),
            timestamp=datetime(2024, 1, 16, 8, 0)
        )

        records = db_session.query(Record).filter_by(date=target_date, user_id=test_user.id).all()

        # Should have 6 records (5 from daily records + urine/bowel)
        assert len(records) >= 5

    def test_query_records_by_type(self, db_session: Session, test_user: User):
        """Test querying records by type"""
        RecordFactory.create(db_session, test_user, type="feeding")
        RecordFactory.create(db_session, test_user, type="feeding")
        RecordFactory.create(db_session, test_user, type="urine")

        feeding_records = db_session.query(Record).filter_by(
            user_id=test_user.id, type="feeding"
        ).all()

        assert len(feeding_records) == 2

    def test_record_user_relationship(self, db_session: Session, test_user: User):
        """Test record-user relationship"""
        record = RecordFactory.create(db_session, test_user)

        # Access relationship
        assert record.user is not None
        assert record.user.id == test_user.id
        assert record.user.openid == test_user.openid

    def test_record_details_jsonb(self, db_session: Session, test_user: User):
        """Test record details JSONB field"""
        details = {
            "amount_ml": 150,
            "feeding_type": "breast",
            "notes": "宝宝吃得很香",
        }

        record = RecordFactory.create(
            db_session, test_user,
            type="feeding",
            details=details
        )

        # Query and verify
        found_record = db_session.query(Record).filter_by(id=record.id).first()
        assert found_record.details["amount_ml"] == 150
        assert found_record.details["feeding_type"] == "breast"
        assert found_record.details["notes"] == "宝宝吃得很香"


@pytest.mark.integration
class TestBabyConfigModel:
    """Integration tests for BabyConfig model"""

    def test_create_baby_config(self, db_session: Session, test_user: User):
        """Test creating baby config"""
        config = BabyConfigFactory.create(db_session, test_user)

        assert config.id is not None
        assert config.user_id == test_user.id
        assert config.baby_name is not None

    def test_query_baby_config_by_user(self, db_session: Session, test_user: User):
        """Test querying baby config by user"""
        config = BabyConfigFactory.create(db_session, test_user)

        found_config = db_session.query(BabyConfig).filter_by(user_id=test_user.id).first()

        assert found_config is not None
        assert found_config.id == config.id

    def test_baby_config_user_relationship(self, db_session: Session, test_user: User):
        """Test baby config-user relationship"""
        config = BabyConfigFactory.create(db_session, test_user)

        assert config.user is not None
        assert config.user.id == test_user.id

    def test_baby_config_age_calculation(self, db_session: Session, test_user: User):
        """Test baby age calculation"""
        birth_date = date(2024, 1, 1)
        config = BabyConfigFactory.create(
            db_session, test_user,
            birth_date=birth_date
        )

        # Test age calculation
        target_date = date(2024, 1, 15)
        age_days = config.get_age_days(target_date)

        assert age_days == 15  # 15 days old

    def test_baby_config_one_per_user(self, db_session: Session, test_user: User):
        """Test that only one baby config per user"""
        BabyConfigFactory.create(db_session, test_user)

        # Try to create another config for same user
        with pytest.raises(Exception):  # IntegrityError due to unique constraint
            config2 = BabyConfig(user_id=test_user.id, baby_name="Another config")
            db_session.add(config2)
            db_session.flush()


@pytest.mark.integration
class TestUserRecordRelationship:
    """Integration tests for User-Record relationship"""

    def test_user_records_relationship(self, db_session: Session, test_user: User):
        """Test accessing records through user relationship"""
        RecordFactory.create_batch(db_session, test_user, 3)

        # Access through relationship
        assert len(test_user.records) == 3

    def test_cascade_delete_records(self, db_session: Session):
        """Test that records are deleted when user is deleted"""
        user = UserFactory.create(db_session)
        records = RecordFactory.create_batch(db_session, user, 3)
        record_ids = [r.id for r in records]
        user_id = user.id

        # Delete user
        db_session.delete(user)
        db_session.flush()

        # Verify records are deleted
        remaining_records = db_session.query(Record).filter(
            Record.id.in_(record_ids)
        ).all()
        assert len(remaining_records) == 0

    def test_user_baby_config_relationship(self, db_session: Session, test_user: User):
        """Test accessing baby config through user relationship"""
        config = BabyConfigFactory.create(db_session, test_user)

        # Access through relationship
        assert test_user.baby_config is not None
        assert test_user.baby_config.id == config.id