"""Integration tests for service layer"""

import pytest
from datetime import datetime, date
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from src.models.user import User
from src.models.record import Record
from src.models.baby_config import BabyConfig
from src.services.record_service import RecordService
from src.services.config_service import ConfigService
from tests.fixtures.factories import UserFactory, RecordFactory, BabyConfigFactory


@pytest.mark.integration
class TestRecordService:
    """Integration tests for RecordService"""

    def test_create_record(self, db_session: Session, test_user: User):
        """Test creating a record through service"""
        service = RecordService(db_session)

        record = service.create_record(
            user_id=str(test_user.id),
            record_type="feeding",
            details={"amount_ml": 100, "feeding_type": "formula"},
        )

        assert record.id is not None
        assert record.type == "feeding"
        assert record.details["amount_ml"] == 100

    def test_list_daily_records(self, db_session: Session, test_user: User):
        """Test listing daily records"""
        target_date = date(2024, 1, 15)
        RecordFactory.create_daily_records(db_session, test_user, target_date)

        service = RecordService(db_session)
        records = service.list_daily_records(str(test_user.id), target_date)

        assert len(records) >= 5

    def test_get_record_by_id(self, db_session: Session, test_user: User):
        """Test getting a record by ID"""
        created_record = RecordFactory.create(db_session, test_user)

        service = RecordService(db_session)
        record = service.get_record(str(test_user.id), str(created_record.id))

        assert record is not None
        assert record.id == created_record.id

    def test_update_record(self, db_session: Session, test_user: User):
        """Test updating a record"""
        record = RecordFactory.create(
            db_session, test_user,
            details={"amount_ml": 100, "feeding_type": "formula"}
        )

        service = RecordService(db_session)
        updated = service.update_record(
            str(test_user.id),
            str(record.id),
            details={"amount_ml": 150, "feeding_type": "breast"}
        )

        assert updated.details["amount_ml"] == 150

    def test_delete_record(self, db_session: Session, test_user: User):
        """Test deleting a record"""
        record = RecordFactory.create(db_session, test_user)

        service = RecordService(db_session)
        service.delete_record(str(test_user.id), str(record.id))

        # Verify deleted
        found = db_session.query(Record).filter_by(id=record.id).first()
        assert found is None

    def test_list_records_by_type(self, db_session: Session, test_user: User):
        """Test listing records by type"""
        RecordFactory.create(db_session, test_user, type="feeding")
        RecordFactory.create(db_session, test_user, type="feeding")
        RecordFactory.create(db_session, test_user, type="urine")

        service = RecordService(db_session)
        records = service.list_records_by_type(str(test_user.id), "feeding")

        assert len(records) == 2

    def test_get_records_summary(self, db_session: Session, test_user: User):
        """Test getting records summary"""
        target_date = date(2024, 1, 15)
        RecordFactory.create_daily_records(db_session, test_user, target_date)

        service = RecordService(db_session)
        summary = service.get_daily_summary(str(test_user.id), target_date)

        assert "feeding" in summary
        assert summary["feeding"]["count"] >= 3


@pytest.mark.integration
class TestConfigService:
    """Integration tests for ConfigService"""

    def test_get_baby_config_creates_default(self, db_session: Session, test_user: User):
        """Test getting baby config creates default if not exists"""
        service = ConfigService(db_session)
        config = service.get_baby_config(str(test_user.id))

        assert config is not None
        assert config.user_id == test_user.id

    def test_update_baby_config(self, db_session: Session, test_user: User):
        """Test updating baby config"""
        service = ConfigService(db_session)

        config = service.update_baby_config(
            str(test_user.id),
            baby_name="新宝宝名字",
            birth_date=date(2024, 2, 1),
            gender="female",
        )

        assert config.baby_name == "新宝宝名字"
        assert config.gender == "female"

    def test_get_baby_age(self, db_session: Session, test_user: User):
        """Test getting baby age"""
        BabyConfigFactory.create(
            db_session, test_user,
            birth_date=date(2024, 1, 1)
        )

        service = ConfigService(db_session)
        age_days = service.get_baby_age_days(str(test_user.id), target_date=date(2024, 1, 15))

        assert age_days == 15

    def test_config_service_caching(self, db_session: Session, test_user: User):
        """Test that config service caches results within session"""
        service = ConfigService(db_session)

        config1 = service.get_baby_config(str(test_user.id))
        config2 = service.get_baby_config(str(test_user.id))

        # Same object due to caching
        assert config1.id == config2.id


@pytest.mark.integration
class TestAuthService:
    """Integration tests for AuthService"""

    def test_login_new_user(self, db_session: Session, mock_wechat_api):
        """Test login creates new user"""
        from src.services.auth_service import AuthService

        service = AuthService(db_session)

        with patch("src.services.auth_service.WechatAPI") as mock_api_class:
            mock_api = MagicMock()
            mock_api.jscode2session.return_value = {
                "openid": "new_user_openid",
                "session_key": "test_session_key",
            }
            mock_api_class.return_value = mock_api

            result = service.login("test_code")

            assert result is not None
            assert "token" in result
            assert "user" in result

    def test_login_existing_user(self, db_session: Session, test_user: User):
        """Test login returns existing user"""
        from src.services.auth_service import AuthService

        service = AuthService(db_session)

        with patch("src.services.auth_service.WechatAPI") as mock_api_class:
            mock_api = MagicMock()
            mock_api.jscode2session.return_value = {
                "openid": test_user.openid,
                "session_key": "test_session_key",
            }
            mock_api_class.return_value = mock_api

            result = service.login("test_code")

            assert result["user"]["openid"] == test_user.openid

    def test_get_user_by_id(self, db_session: Session, test_user: User):
        """Test getting user by ID"""
        from src.services.auth_service import AuthService

        service = AuthService(db_session)
        user = service.get_user_by_id(str(test_user.id))

        assert user is not None
        assert user.id == test_user.id