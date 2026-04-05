"""
FC (函数计算) 专用数据库连接配置

针对 FC 环境优化的数据库连接池配置：
- 小连接池：避免连接泄漏和资源浪费
- 短超时：适应 FC 实例短生命周期
- 健康检查：处理冷启动后的连接失效
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging
import time

from src.config import settings

logger = logging.getLogger(__name__)

# FC 专用数据库连接参数
FC_DB_CONFIG = {
    # 小连接池配置
    "pool_size": 2,           # 小连接池，FC 单实例并发低
    "max_overflow": 0,        # 无溢出，避免连接泄漏

    # 连接生命周期配置
    "pool_recycle": 60,       # 60秒回收连接，适应 FC 实例生命周期
    "pool_timeout": 5,        # 5秒等待连接超时

    # 连接健康检查
    "pool_pre_ping": True,    # 获取连接前检查有效性

    # 连接超时配置
    "connect_args": {
        "connect_timeout": 5,  # 5秒连接超时
        "options": "-c statement_timeout=10000",  # 10秒查询超时
    },

    # 其他配置
    "echo": settings.debug,   # 调试模式打印 SQL
}


def create_fc_engine():
    """创建 FC 优化的数据库引擎"""
    engine = create_engine(settings.database_url, **FC_DB_CONFIG)

    # 添加连接事件监听器
    @event.listens_for(engine, "connect")
    def on_connect(dbapi_connection, connection_record):
        logger.debug("Database connection established")

    @event.listens_for(engine, "checkout")
    def on_checkout(dbapi_connection, connection_record, connection_proxy):
        logger.debug("Database connection checked out from pool")

    @event.listens_for(engine, "checkin")
    def on_checkin(dbapi_connection, connection_record):
        logger.debug("Database connection returned to pool")

    return engine


# 创建引擎（模块级别，FC 实例复用）
_engine = None


def get_engine():
    """获取数据库引擎（延迟初始化，支持 FC 冷启动）"""
    global _engine
    if _engine is None:
        _engine = create_fc_engine()
    return _engine


# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

# 创建声明基类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话（用于依赖注入）

    FC 环境下每个请求获取新会话，请求结束后关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_with_retry(max_retries: int = 3, retry_delay: float = 0.5) -> Session:
    """
    获取数据库会话（带重试机制）

    用于处理 FC 冷启动后的连接失败

    Args:
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）

    Returns:
        数据库会话

    Raises:
        Exception: 重试失败后抛出异常
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # 测试连接
            db.execute("SELECT 1")
            return db
        except Exception as e:
            last_error = e
            logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")

            # 等待后重试
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # 指数退避

    raise Exception(f"Failed to connect to database after {max_retries} attempts: {last_error}")


def init_db() -> None:
    """初始化数据库 - 创建所有表"""
    from src.models import User, Record, BabyConfig  # noqa: F401
    Base.metadata.create_all(bind=get_engine())


def close_db() -> None:
    """关闭数据库连接池（FC 实例销毁时调用）"""
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
        logger.info("Database connection pool closed")