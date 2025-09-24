# core/database.py (간단한 버전)

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

def convert_jdbc_to_mysql_url(jdbc_url: str) -> str:
    """JDBC URL을 SQLAlchemy MySQL URL로 변환"""
    if jdbc_url.startswith("jdbc:mysql://"):
        url_part = jdbc_url.replace("jdbc:mysql://", "")

        if "?" in url_part:
            db_part, params = url_part.split("?", 1)
        else:
            db_part = url_part

        host_port, database = db_part.rsplit("/", 1)

        username = os.getenv("DB_USERNAME", "root")
        password = os.getenv("DB_PASSWORD", "")

        mysql_url = f"mysql+pymysql://{username}:{password}@{host_port}/{database}?charset=utf8mb4"
        return mysql_url

    return jdbc_url

# 환경변수에서 직접 가져오기
JDBC_URL = os.getenv("DB_URL", "")
DATABASE_URL = convert_jdbc_to_mysql_url(JDBC_URL) if JDBC_URL else \
    "mysql+pymysql://root:@138.2.119.75:3306/final_project?charset=utf8mb4"

# SQLAlchemy 설정
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
