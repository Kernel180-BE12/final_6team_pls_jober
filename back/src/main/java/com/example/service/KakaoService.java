package com.example.service;

import com.example.dto.KakaoUserInfo;
import com.example.entity.Account;
import com.example.repository.AccountRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.Map;
import java.util.Optional;

/**
 * 카카오 소셜 로그인 서비스
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class KakaoService {
    
    private final AccountRepository accountRepository;
    private final TokenService tokenService;
    private final WebClient webClient;
    
    @Value("${KAKAO_CLIENT_ID}")
    private String kakaoClientId;

    @Value("${KAKAO_CLIENT_SECRET}")
    private String kakaoClientSecret;

    @Value("${KAKAO_REDIRECT_URI}")
    private String kakaoRedirectUri;
    
    /**
     * 카카오 인가코드로 액세스 토큰 받기
     */
    public String getAccessToken(String authorizationCode) {
        log.info("카카오 액세스 토큰 요청 시작. 인가코드: {}", authorizationCode);
        
        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> response = webClient.post()
                    .uri("https://kauth.kakao.com/oauth/token")
                    .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                    .bodyValue("grant_type=authorization_code" +
                             "&client_id=" + kakaoClientId +
                             "&client_secret=" + kakaoClientSecret +
                             "&redirect_uri=" + kakaoRedirectUri +
                             "&code=" + authorizationCode)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
            
            log.info("카카오 토큰 응답: {}", response);
            return (String) response.get("access_token");
        } catch (Exception e) {
            log.error("카카오 액세스 토큰 요청 실패", e);
            throw new RuntimeException("카카오 액세스 토큰 요청 실패: " + e.getMessage());
        }
    }
    
    /**
     * 카카오 사용자 정보 조회
     */
    public KakaoUserInfo getUserInfo(String accessToken) {
        log.info("카카오 사용자 정보 조회 시작");
        
        try {
            KakaoUserInfo userInfo = webClient.get()
                    .uri("https://kapi.kakao.com/v2/user/me")
                    .header("Authorization", "Bearer " + accessToken)
                    .retrieve()
                    .bodyToMono(KakaoUserInfo.class)
                    .block();
            
            log.info("카카오 사용자 정보 조회 성공. ID: {}, 닉네임: {}, 이메일: {}", 
                     userInfo.getId(), 
                     userInfo.getProperties() != null ? userInfo.getProperties().getNickname() : null,
                     userInfo.getKakaoAccount() != null ? userInfo.getKakaoAccount().getEmail() : null);
            
            return userInfo;
        } catch (Exception e) {
            log.error("카카오 사용자 정보 조회 실패", e);
            throw new RuntimeException("카카오 사용자 정보 조회 실패: " + e.getMessage());
        }
    }
    
    /**
     * 카카오 소셜 로그인 처리
     */
    @Transactional
    public Map<String, String> processKakaoLogin(String authorizationCode) {
        // 1. 인가코드로 액세스 토큰 받기
        String kakaoAccessToken = getAccessToken(authorizationCode);
        
        // 2. 액세스 토큰으로 사용자 정보 받기
        KakaoUserInfo kakaoUserInfo = getUserInfo(kakaoAccessToken);
        
        // 3. 사용자 정보로 계정 처리 (가입/로그인)
        Account account = findOrCreateAccount(kakaoUserInfo);
        
        // 4. JWT 토큰 생성 및 반환
        return tokenService.generateTokenPair(account);
    }
    
    /**
     * 카카오 사용자 정보로 계정 찾기 또는 생성
     */
    @Transactional
    public Account findOrCreateAccount(KakaoUserInfo kakaoUserInfo) {
        String email = extractEmail(kakaoUserInfo);
        String nickname = extractNickname(kakaoUserInfo);
        String kakaoId = kakaoUserInfo.getId().toString();
        
        log.info("카카오 계정 처리 시작. 이메일: {}, 닉네임: {}, 카카오ID: {}", email, nickname, kakaoId);
        
        // 이메일로 기존 계정 조회
        Optional<Account> existingAccount = accountRepository.findByEmail(email);
        
        if (existingAccount.isPresent()) {
            log.info("기존 계정 발견: {}", existingAccount.get().getId());
            return existingAccount.get();
        }
        
        // 신규 계정 생성
        Account newAccount = new Account();
        newAccount.setEmail(email);
        newAccount.setUserName(nickname);
        newAccount.setPasswordHash("KAKAO_" + kakaoId); // 소셜 로그인은 비밀번호 대신 소셜 ID 저장
        newAccount.setRole("USER");
        newAccount.setStatus("ACTIVE");
        
        Account savedAccount = accountRepository.save(newAccount);
        log.info("신규 카카오 계정 생성 완료. ID: {}", savedAccount.getId());
        
        return savedAccount;
    }
    
    private String extractEmail(KakaoUserInfo kakaoUserInfo) {
        if (kakaoUserInfo.getKakaoAccount() != null &&
            kakaoUserInfo.getKakaoAccount().getEmail() != null &&
            !kakaoUserInfo.getKakaoAccount().getEmail().trim().isEmpty()) {
            return kakaoUserInfo.getKakaoAccount().getEmail();
        }

        // 카카오에서 이메일을 제공하지 않는 경우 에러 처리
        log.error("카카오 계정에서 이메일 정보를 가져올 수 없습니다. 사용자 ID: {}", kakaoUserInfo.getId());
        throw new RuntimeException("카카오 계정에서 이메일 정보를 가져올 수 없습니다. 이메일 동의가 필요합니다.");
    }
    
    private String extractNickname(KakaoUserInfo kakaoUserInfo) {
        // 프로필 닉네임 우선
        if (kakaoUserInfo.getKakaoAccount() != null && 
            kakaoUserInfo.getKakaoAccount().getProfile() != null &&
            kakaoUserInfo.getKakaoAccount().getProfile().getNickname() != null) {
            return kakaoUserInfo.getKakaoAccount().getProfile().getNickname();
        }
        
        // properties 닉네임
        if (kakaoUserInfo.getProperties() != null && 
            kakaoUserInfo.getProperties().getNickname() != null) {
            return kakaoUserInfo.getProperties().getNickname();
        }
        
        // 둘 다 없으면 카카오 사용자로 기본값
        return "카카오사용자" + kakaoUserInfo.getId();
    }
}