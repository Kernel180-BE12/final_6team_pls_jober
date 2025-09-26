package com.example.config;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.util.Date;

@Component
public class JwtTokenProvider {

    private final SecretKey key;
    private final long accessTokenValidity;   // ms 단위
    private final long refreshTokenValidity;  // ms 단위

    public JwtTokenProvider(
            @Value("${jwt.secret}") String secretKey,
            @Value("${jwt.access-expiration}") long accessTokenValidity,
            @Value("${jwt.refresh-expiration}") long refreshTokenValidity
    ) {
        this.key = Keys.hmacShaKeyFor(secretKey.getBytes());
        this.accessTokenValidity = accessTokenValidity;
        this.refreshTokenValidity = refreshTokenValidity;
    }

    // Access Token 생성 - 사용자 정보를 포함하여 DB 조회 최소화
    public String createAccessToken(String email, String role, Long accountId, String userName) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + accessTokenValidity);

        return Jwts.builder()
                .subject(email)               // sub: 사용자 식별자
                .claim("role", role)             // 사용자 권한
                .claim("account_id", accountId)  // 계정 ID (인증에 필요)
                .claim("user_name", userName)    // 사용자 이름
                .claim("type", "access")      // 토큰 타입 구분
                .issuedAt(now)                // iat
                .expiration(expiry)           // exp
                .signWith(key)
                .compact();
    }

    // Refresh Token 생성
    public String createRefreshToken(String email, Long accountId) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + refreshTokenValidity);

        return Jwts.builder()
                .subject(email)               // sub: 사용자 식별자
                .claim("account_id", accountId)  // 계정 ID
                .claim("type", "refresh")     // 토큰 타입 구분
                .issuedAt(now)
                .expiration(expiry)
                .signWith(key)
                .compact();
    }

    // 이메일 추출
    public String getEmail(String token) {
        return Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload()
                .getSubject();
    }

    // 토큰 유효성 검사
    public boolean validateToken(String token) {
        try {
            Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(token);
            return true;
        } catch (Exception e) {
            System.out.println("JWT 토큰 유효성 검사 실패: " + e.getMessage());
            return false;
        }
    }

    // 토큰에서 계정 ID 추출
    public Long getAccountId(String token) {
        try {
            return Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload()
                    .get("account_id", Long.class);
        } catch (Exception e) {
            return null;
        }
    }

    // 토큰 타입 확인
    public String getTokenType(String token) {
        try {
            return Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload()
                    .get("type", String.class);
        } catch (Exception e) {
            return null;
        }
    }

    // 토큰에서 사용자 이름 추출
    public String getUserName(String token) {
        try {
            return Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload()
                    .get("user_name", String.class);
        } catch (Exception e) {
            return null;
        }
    }

    // 토큰에서 역할 추출
    public String getRole(String token) {
        try {
            return Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload()
                    .get("role", String.class);
        } catch (Exception e) {
            return null;
        }
    }
}
