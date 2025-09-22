from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
import os
from datetime import datetime

# JWT 설정
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"

security = HTTPBearer()

class AuthMiddleware:
    """AI 서비스용 JWT 인증 미들웨어"""
    
    @staticmethod
    def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
        """
        JWT 토큰을 검증하고 사용자 정보를 반환합니다.
        
        Args:
            credentials: HTTP Bearer 토큰
            
        Returns:
            dict: 사용자 정보 (account_id, email, role, user_name, company_name)
            
        Raises:
            HTTPException: 토큰이 유효하지 않은 경우
        """
        try:
            token = credentials.credentials
            
            # JWT 토큰 디코딩
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            # 토큰 타입 확인 (access token만 허용)
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="잘못된 토큰 타입입니다."
                )
            
            # 토큰 만료 확인
            exp = payload.get("exp")
            if exp and datetime.utcnow().timestamp() > exp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="토큰이 만료되었습니다."
                )
            
            # 사용자 정보 추출
            user_info = {
                "account_id": payload.get("account_id"),
                "email": payload.get("sub"),  # subject는 email
                "role": payload.get("role"),
                "user_name": payload.get("user_name"),
                "company_name": payload.get("company_name")
            }
            
            # 필수 정보 확인
            if not user_info["account_id"] or not user_info["email"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="토큰에 필수 사용자 정보가 없습니다."
                )
            
            return user_info
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었습니다."
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"인증 오류: {str(e)}"
            )

# 의존성 함수들
def get_current_user(user_info: dict = Depends(AuthMiddleware.verify_token)) -> dict:
    """현재 사용자 정보를 반환합니다."""
    return user_info



