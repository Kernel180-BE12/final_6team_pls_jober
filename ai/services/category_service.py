# services/category_service.py

import logging
import os
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.category import Category

logger = logging.getLogger(__name__)

# 환경변수에서 직접 가져오기
CONFIDENCE_THRESHOLD = int(os.getenv("CATEGORY_CONFIDENCE_THRESHOLD", "70"))
AUTO_CREATE_CATEGORIES = os.getenv("AUTO_CREATE_CATEGORIES", "True").lower() == "true"
MAX_CATEGORY_NAME_LENGTH = int(os.getenv("MAX_CATEGORY_NAME_LENGTH", "50"))

class CategoryService:
    """DB 기반 카테고리 관리 서비스"""

    def __init__(self, db: Session):
        self.db = db

    async def get_all_categories(self) -> List[str]:
        """모든 활성 카테고리 목록 조회"""
        try:
            categories = self.db.query(Category.name) \
                .filter(Category.is_active == True) \
                .order_by(Category.name) \
                .all()

            category_names = [cat.name for cat in categories]
            logger.info(f"DB에서 카테고리 목록 조회 완료: {len(category_names)}개")
            return category_names

        except Exception as e:
            logger.error(f"카테고리 목록 조회 실패: {e}")
            return ["기타", "구매완료", "배송상태", "예약완료"]

    async def get_category_by_name(self, category_name: str) -> Optional[Category]:
        """카테고리명으로 카테고리 조회"""
        try:
            return self.db.query(Category) \
                .filter(Category.name == category_name) \
                .filter(Category.is_active == True) \
                .first()
        except Exception as e:
            logger.error(f"카테고리 조회 실패 ({category_name}): {e}")
            return None

    async def create_category_if_not_exists(self, category_name: str, description: str = None) -> Optional[Category]:
        """카테고리가 존재하지 않으면 생성"""
        try:
            existing_category = await self.get_category_by_name(category_name)
            if existing_category:
                logger.info(f"기존 카테고리 재사용: {category_name}")
                return existing_category

            if not AUTO_CREATE_CATEGORIES:
                logger.warning("카테고리 자동 생성이 비활성화됨")
                return await self.get_category_by_name("기타")

            if not category_name or len(category_name.strip()) == 0:
                logger.error("빈 카테고리명")
                return await self.get_category_by_name("기타")

            if len(category_name) > MAX_CATEGORY_NAME_LENGTH:
                category_name = category_name[:MAX_CATEGORY_NAME_LENGTH]

            new_category = Category(
                name=category_name.strip(),
                description=description or f"자동 생성된 카테고리: {category_name}",
                is_active=True,
                created_by="ai_system"
            )

            self.db.add(new_category)
            self.db.commit()
            self.db.refresh(new_category)

            logger.info(f"신규 카테고리 생성 완료: '{category_name}'")
            return new_category

        except IntegrityError:
            self.db.rollback()
            logger.warning(f"카테고리 중복 생성 시도: {category_name}")
            return await self.get_category_by_name(category_name)

        except Exception as e:
            self.db.rollback()
            logger.error(f"카테고리 생성 실패: {category_name}, 오류: {e}")
            return await self.get_category_by_name("기타")

    async def update_category_usage_count(self, category_id: int):
        """카테고리 사용 횟수 업데이트"""
        try:
            self.db.query(Category) \
                .filter(Category.id == category_id) \
                .update({"usage_count": Category.usage_count + 1})
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"카테고리 사용 횟수 업데이트 실패: {e}")

