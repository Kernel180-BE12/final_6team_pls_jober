package com.example.controller;

import com.example.dto.LoginRequest;
import com.example.dto.RefreshTokenRequest;
import com.example.dto.SignupRequest;
import com.example.entity.Account;
import com.example.service.AuthService;
import com.example.service.TokenService;
import lombok.RequiredArgsConstructor;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;
    private final TokenService tokenService;

    /**
     * 현재 인증된 사용자 정보 조회
     * @param authentication
     * @return
     */
    @GetMapping("/me")
    public ResponseEntity<?> getCurrentUser(Authentication authentication) {
        // 인증되지 않은 경우 처리 
        if(authentication == null || !authentication.isAuthenticated()) {
            // 401 Unauthorized 응답 반환
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Unauthorized");
        }
        
        // 인증된 사용자는 사용자 정보 반환
        // TODO: 권한 반환 추가?
        Long accountId = (Long) authentication.getPrincipal();
        return ResponseEntity.ok(Map.of("userId", accountId));
    }

    // 회원가입
    @PostMapping("/signup")
    public ResponseEntity<?> signup(@RequestBody SignupRequest request) {
        Account account = authService.registerUser(request);
        return ResponseEntity.ok(Map.of(
                "message", "회원가입 성공",
                "username", account.getUserName()
        ));
    }

    // 로그인 → JWT 반환
    @PostMapping("/login")
    public Map<String, String> login(@RequestBody LoginRequest request) {
        return authService.login(request);
    }

    // Refresh Token으로 Access Token 갱신
    @PostMapping("/refresh")
    public Map<String, String> refreshToken(@RequestBody RefreshTokenRequest request) {
        return tokenService.refreshAccessToken(request.getRefreshToken());
    }

    // 로그아웃
    @PostMapping("/logout")
    public ResponseEntity<?> logout(@RequestHeader("Authorization") String authHeader,
                                   @RequestBody(required = false) RefreshTokenRequest request) {
        String accessToken = null;
        String refreshToken = null;

        // Authorization 헤더에서 Access Token 추출
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            accessToken = authHeader.substring(7);
        }

        // Request Body에서 Refresh Token 추출
        if (request != null) {
            refreshToken = request.getRefreshToken();
        }

        tokenService.logout(accessToken, refreshToken);
        return ResponseEntity.ok(Map.of("message", "로그아웃 성공"));
    }
}
