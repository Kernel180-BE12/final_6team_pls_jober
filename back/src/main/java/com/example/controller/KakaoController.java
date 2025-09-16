package com.example.controller;

import com.example.service.KakaoService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * 카카오 소셜 로그인 컨트롤러
 */
@Slf4j
@RestController
@RequestMapping("/api/auth/kakao")
@RequiredArgsConstructor
public class KakaoController {

    private final KakaoService kakaoService;

    @Value("${KAKAO_CLIENT_ID}")
    private String kakaoClientId;

    @Value("${KAKAO_REDIRECT_URI}")
    private String kakaoRedirectUri;
    
    /**
     * 카카오 로그인 콜백 처리
     * 프론트엔드에서 카카오 인가코드를 받아온 후 호출하는 엔드포인트
     */
    @PostMapping("/login")
    public ResponseEntity<Map<String, String>> kakaoLogin(@RequestParam(value = "code", required = false) String authorizationCode) {
        log.info("카카오 로그인 요청 수신. 인가코드: {}", authorizationCode);

        if (authorizationCode == null || authorizationCode.trim().isEmpty()) {
            log.error("카카오 로그인에서 인가코드가 누락됨");
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "카카오 로그인 실패: 인가코드가 필요합니다"));
        }

        try {
            Map<String, String> tokens = kakaoService.processKakaoLogin(authorizationCode);
            log.info("카카오 로그인 성공. 사용자ID: {}", tokens.get("userId"));
            
            return ResponseEntity.ok(tokens);
        } catch (Exception e) {
            log.error("카카오 로그인 실패", e);
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "카카오 로그인 실패: " + e.getMessage()));
        }
    }
    
    /**
     * 카카오 로그인 URL 생성
     * 프론트엔드에서 카카오 로그인 버튼 클릭 시 리다이렉트할 URL 제공
     */
    @GetMapping("/url")
    public ResponseEntity<Map<String, String>> getKakaoLoginUrl() {
        String kakaoAuthUrl = "https://kauth.kakao.com/oauth/authorize" +
                "?client_id=" + kakaoClientId +
                "&redirect_uri=" + kakaoRedirectUri +
                "&response_type=code" +
                "&scope=profile_nickname,account_email";

        return ResponseEntity.ok(Map.of("url", kakaoAuthUrl));
    }
    
    /**
     * 카카오 OAuth2 콜백 엔드포인트
     * 카카오에서 인가코드를 리다이렉트로 보내주는 엔드포인트
     * 프론트엔드로 리다이렉트하여 토큰 전달
     */
    @GetMapping("/callback")
    public ResponseEntity<Void> kakaoCallback(
            @RequestParam(value = "code", required = false) String authorizationCode,
            @RequestParam(value = "error", required = false) String error) {

        if (error != null) {
            log.error("카카오 OAuth2 에러: {}", error);
            return ResponseEntity.status(302)
                    .header("Location", "http://134.185.106.160?error=" + error)
                    .build();
        }

        if (authorizationCode == null || authorizationCode.trim().isEmpty()) {
            log.error("카카오 콜백에서 인가코드가 누락됨");
            return ResponseEntity.status(302)
                    .header("Location", "http://134.185.106.160?error=missing_authorization_code")
                    .build();
        }

        log.info("카카오 콜백 수신. 인가코드: {}", authorizationCode);

        try {
            Map<String, String> tokens = kakaoService.processKakaoLogin(authorizationCode);
            log.info("카카오 콜백 처리 성공. 사용자ID: {}", tokens.get("userId"));

            // 프론트엔드로 토큰 전달하여 리다이렉트
            String redirectUrl = String.format(
                "http://134.185.106.160?accessToken=%s&refreshToken=%s&userId=%s&role=%s",
                tokens.get("accessToken"),
                tokens.get("refreshToken"),
                tokens.get("userId"),
                tokens.get("role")
            );

            return ResponseEntity.status(302)
                    .header("Location", redirectUrl)
                    .build();
        } catch (Exception e) {
            log.error("카카오 콜백 처리 실패", e);
            return ResponseEntity.status(302)
                    .header("Location", "http://134.185.106.160?error=" + e.getMessage())
                    .build();
        }
    }
}