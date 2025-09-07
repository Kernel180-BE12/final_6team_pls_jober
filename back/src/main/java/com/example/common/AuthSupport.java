package com.example.common;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

// 현재 사용자 ID(account_id) 추출 유틸
public class AuthSupport {
    public static Long currentUserId() {
        // SecurityContext에서 Authentication 가져오기
        var context = SecurityContextHolder.getContext();
        Authentication auth = (context != null ? context.getAuthentication() : null);

        // 인증 정보가 없거나, AnonymousAuthenticationToken(익명 사용자)이면 인증 실패 처리
        if (auth == null || auth instanceof org.springframework.security.authentication.AnonymousAuthenticationToken) {
            throw new IllegalStateException("Unauthenticated user");
        }

        // principal(= 사용자 주체 객체) 추출
        Object p = auth.getPrincipal();
        if (p == null) {
            throw new IllegalStateException("Unauthenticated user");
        }

        // principal이 Long 타입인 account의 Id
        if (p instanceof Long id) {
            return id;
        }

        // 예상과 다른 타입이면 지원하지 않는 인증 주체 → 예외 발생
        throw new IllegalStateException("Unsupported principal: " + p.getClass().getName());
    }
}
