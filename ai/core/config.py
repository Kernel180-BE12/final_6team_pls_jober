from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MySQL 데이터베이스 설정
    DB_URL: str = "jdbc:mysql://138.2.119.75:3306/final_project?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=Asia/Seoul"
    DB_USERNAME: str = "root"
    DB_PASSWORD: str = ""

    # 애플리케이션 설정
    APP_NAME: str = "AlimTalk Template Generator"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # OpenAI 설정
    OPENAI_API_KEY: str

    # ChromaDB 설정
    CHROMA_DB_HOST: str = "138.2.119.75"
    CHROMA_DB_PORT: int = 8001

    # 카테고리 관련 설정
    CATEGORY_CONFIDENCE_THRESHOLD: int = 70
    AUTO_CREATE_CATEGORIES: bool = True
    MAX_CATEGORY_NAME_LENGTH: int = 50

    class Config:
        env_file = ".env"
        case_sensitive = True

# 전역 설정 인스턴스
settings = Settings()
