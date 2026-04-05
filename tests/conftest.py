"""Pytest configuration and fixtures for Baby Diary API tests"""

import os
import pytest
from datetime import datetime, date
from typing import Generator
from unittest.mock import MagicMock, patch

# Set test environment before importing app modules
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5433/baby_diary_test")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
os.environ.setdefault("WECHAT_APP_ID", "test_app_id")
os.environ.setdefault("WECHAT_APP_SECRET", "test_app_secret")
os.environ.setdefault("DASHSCOPE_API_KEY", "test_key")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from fastapi.testclient import TestClient

from src.db.session import Base
from src.models.user import User
from src.models.record import Record
from src.models.baby_config import BabyConfig
from src.api.main import app


# Test database URL
TEST_DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://test:test@localhost:5433/baby_diary_test")


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine (session-scoped)"""
    engine = create_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True,
        echo=False,  # Set to True for SQL debugging
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def test_db(test_engine):
    """Create all tables in test database (session-scoped)"""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    # Drop all tables after all tests
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session(test_db) -> Generator[Session, None, None]:
    """
    Create a database session for each test.
    Rolls back transaction after test for isolation.
    """
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)

    # Create session
    session = SessionLocal()

    # Begin transaction
    session.begin()

    yield session

    # Rollback after test
    session.rollback()
    session.close()


@pytest.fixture
def client() -> TestClient:
    """Create test client for API tests"""
    return TestClient(app)


@pytest.fixture
def test_user_data() -> dict:
    """Test user data fixture"""
    return {
        "openid": "test_openid_123",
        "nickname": "测试用户",
        "avatar_url": "https://example.com/avatar.png",
    }


@pytest.fixture
def test_user(db_session: Session, test_user_data: dict) -> User:
    """Create a test user in database"""
    user = User(
        openid=test_user_data["openid"],
        nickname=test_user_data["nickname"],
        avatar_url=test_user_data["avatar_url"],
    )
    db_session.add(user)
    db_session.flush()  # Get the ID without committing
    return user


@pytest.fixture
def test_baby_config(db_session: Session, test_user: User) -> BabyConfig:
    """Create a test baby config for user"""
    config = BabyConfig(
        user_id=test_user.id,
        baby_name="测试宝宝",
        birth_date=date(2024, 1, 1),
        gender="male",
        birth_weight=3.5,
        feeding_type="mixed",
    )
    db_session.add(config)
    db_session.flush()
    return config


@pytest.fixture
def test_record_data() -> dict:
    """Test record data fixture"""
    return {
        "type": "feeding",
        "timestamp": datetime(2024, 1, 15, 8, 0),
        "date": date(2024, 1, 15),
        "details": {
            "amount_ml": 100,
            "feeding_type": "formula",
        },
    }


@pytest.fixture
def test_record(db_session: Session, test_user: User, test_record_data: dict) -> Record:
    """Create a test record in database"""
    record = Record(
        user_id=test_user.id,
        type=test_record_data["type"],
        timestamp=test_record_data["timestamp"],
        date=test_record_data["date"],
        details=test_record_data["details"],
    )
    db_session.add(record)
    db_session.flush()
    return record


@pytest.fixture
def multiple_records(db_session: Session, test_user: User) -> list[Record]:
    """Create multiple test records for testing queries"""
    records = []
    for i in range(5):
        record = Record(
            user_id=test_user.id,
            type="feeding",
            timestamp=datetime(2024, 1, 15, 8 + i * 4, 0),  # Every 4 hours
            date=date(2024, 1, 15),
            details={"amount_ml": 100 + i * 10, "feeding_type": "formula"},
        )
        db_session.add(record)
        records.append(record)
    db_session.flush()
    return records


# ============== Mock fixtures ==============

@pytest.fixture
def mock_wechat_api():
    """Mock WeChat API for testing without real API calls"""
    with patch("src.services.auth_service.WechatAPI") as mock:
        mock_instance = MagicMock()
        mock_instance.jscode2session.return_value = {
            "openid": "test_openid_123",
            "session_key": "test_session_key",
        }
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing without real API calls"""
    with patch("src.services.llm_service.LLMService") as mock:
        mock_instance = MagicMock()
        mock_instance.chat.return_value = "这是一个测试回复"
        mock_instance.analyze.return_value = {
            "status": "normal",
            "recommendations": ["测试建议"],
        }
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_oss_storage():
    """Mock OSS storage for testing without real OSS"""
    with patch("src.services.oss_storage.get_oss_bucket") as mock:
        mock_bucket = MagicMock()
        mock.return_value = mock_bucket
        yield mock_bucket


# ============== Auth fixtures ==============

@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers for test user"""
    from src.services.jwt_service import JWTService

    jwt_service = JWTService()
    token = jwt_service.create_token(user_id=str(test_user.id))

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def authenticated_client(client: TestClient, auth_headers: dict) -> TestClient:
    """Create authenticated test client"""
    # Note: TestClient doesn't support setting default headers easily
    # Tests should use auth_headers fixture directly
    return client


# ============== Pytest configuration ==============

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test (no database)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires database)"
    )