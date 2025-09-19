package com.example.controller;

import com.example.service.KakaoService;
import com.example.service.TokenService;
import com.example.repository.AccountRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Disabled;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.HashMap;
import java.util.Map;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * 카카오 컨트롤러 테스트
 * - @WebMvcTest: 웹 레이어만 테스트 (컨트롤러 계층 단위 테스트)
 * - @MockBean: 스프링 컨텍스트에 Mock 객체 등록
 * - MockMvc: HTTP 요청/응답을 시뮬레이션
 */
@WebMvcTest(KakaoController.class)
@Import(KakaoControllerTestConfig.class)
@DisplayName("카카오 로그인 컨트롤러 테스트")
@TestPropertySource(properties = {
        "KAKAO_CLIENT_ID=test_client_id",

        "KAKAO_REDIRECT_URI=http://test.158.179.169.48:8080/api/auth/kakao/callback"

})
@Disabled("카카오 컨트롤러 테스트 임시 비활성화 - 의존성 문제")
class KakaoControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    /**
     * @MockBean: 실제 KakaoService 대신 Mock 객체를 스프링 컨텍스트에 등록
     * - 실제 카카오 API 호출 없이 테스트 가능
     * - 원하는 동작을 시뮬레이션할 수 있음
     */
    @MockBean
    private KakaoService kakaoService;

    @MockBean
    private TokenService tokenService;

    @MockBean
    private AccountRepository accountRepository;

    @MockBean
    private WebClient webClient;

    private Map<String, String> mockTokenResponse;

    @BeforeEach
    void setUp() {
        // 목 응답 데이터 준비
        mockTokenResponse = new HashMap<>();
        mockTokenResponse.put("accessToken", "mock_access_token");
        mockTokenResponse.put("refreshToken", "mock_refresh_token");
        mockTokenResponse.put("userId", "12345");
        mockTokenResponse.put("role", "USER");
    }

    @Test
    @DisplayName("카카오 로그인 URL 조회 성공")
    void 카카오_로그인_URL_조회_성공() throws Exception {
        // Given - 특별한 설정 없이 컨트롤러 로직만 테스트

        // When & Then
        mockMvc.perform(get("/api/auth/kakao/url")
                        .contentType(MediaType.APPLICATION_JSON))
                .andDo(print()) // 요청/응답 출력
                .andExpect(status().isOk()) // HTTP 200 상태 확인
                .andExpect(jsonPath("$.url").exists()) // url 필드 존재 확인
                .andExpect(jsonPath("$.url").value(org.hamcrest.Matchers.containsString("kauth.kakao.com"))) // URL 내용 확인
                .andExpect(jsonPath("$.url").value(org.hamcrest.Matchers.containsString("client_id")))
                .andExpect(jsonPath("$.url").value(org.hamcrest.Matchers.containsString("redirect_uri")))
                .andExpect(jsonPath("$.url").value(org.hamcrest.Matchers.containsString("response_type=code")));
    }

    @Test
    @DisplayName("카카오 로그인 성공 - 정상적인 인가코드로 토큰 반환")

    void 카카오_로그인_성공() throws Exception {
        // Given
        String authorizationCode = "valid_authorization_code";

        // Mock 객체 동작 정의: processKakaoLogin 호출 시 mockTokenResponse 반환
        when(kakaoService.processKakaoLogin(authorizationCode))
                .thenReturn(mockTokenResponse);

        // When & Then
        mockMvc.perform(post("/api/auth/kakao/login")
                        .param("code", authorizationCode) // 쿼리 파라미터로 인가코드 전달
                        .contentType(MediaType.APPLICATION_JSON))
                .andDo(print())
                .andExpect(status().isOk()) // HTTP 200 상태 확인
                .andExpect(jsonPath("$.accessToken").value("mock_access_token")) // 응답 데이터 검증
                .andExpect(jsonPath("$.refreshToken").value("mock_refresh_token"))
                .andExpect(jsonPath("$.userId").value("12345"))
                .andExpect(jsonPath("$.role").value("USER"));

        // Mock 객체 호출 검증
        verify(kakaoService, times(1)).processKakaoLogin(authorizationCode);
    }

    @Test
    @DisplayName("카카오 로그인 실패 - 인가코드 누락")
    void 카카오_로그인_실패_인가코드_누락() throws Exception {
        // Given - 인가코드 없이 요청

        // When & Then
        mockMvc.perform(post("/api/auth/kakao/login")
                        .contentType(MediaType.APPLICATION_JSON))
                .andDo(print())
                .andExpect(status().isBadRequest()) // HTTP 400 상태 확인
                .andExpect(jsonPath("$.error").exists())
                .andExpect(jsonPath("$.error").value(org.hamcrest.Matchers.containsString("인가코드가 필요합니다")));

        // Mock 객체가 호출되지 않았는지 확인
        verify(kakaoService, never()).processKakaoLogin(anyString());
    }

    @Test
    @DisplayName("카카오 로그인 실패 - 서비스에서 예외 발생")
    void 카카오_로그인_실패_서비스_예외() throws Exception {
        // Given
        String invalidCode = "invalid_code";

        // Mock 객체가 예외를 던지도록 설정
        when(kakaoService.processKakaoLogin(invalidCode))
                .thenThrow(new RuntimeException("카카오 로그인 실패: 잘못된 인가코드"));

        // When & Then
        mockMvc.perform(post("/api/auth/kakao/login")
                        .param("code", invalidCode)
                        .contentType(MediaType.APPLICATION_JSON))
                .andDo(print())
                .andExpect(status().isBadRequest()) // HTTP 400 상태 확인
                .andExpect(jsonPath("$.error").exists()) // 에러 메시지 확인
                .andExpect(jsonPath("$.error").value(org.hamcrest.Matchers.containsString("카카오 로그인 실패")));

        verify(kakaoService, times(1)).processKakaoLogin(invalidCode);
    }

    @Test
    @DisplayName("카카오 콜백 성공 - 정상적인 인가코드로 처리")
    void 카카오_콜백_성공() throws Exception {
        // Given
        String authorizationCode = "callback_auth_code";

        when(kakaoService.processKakaoLogin(authorizationCode))
                .thenReturn(mockTokenResponse);

        // When & Then
        mockMvc.perform(get("/api/auth/kakao/callback")
                        .param("code", authorizationCode)
                        .contentType(MediaType.APPLICATION_JSON))
                .andDo(print())
                .andExpect(status().isFound()) // 302 리다이렉트 상태 확인
                .andExpect(header().string("Location", org.hamcrest.Matchers.containsString("158.179.169.48")))
                .andExpect(header().string("Location", org.hamcrest.Matchers.containsString("accessToken=mock_access_token")))
                .andExpect(header().string("Location", org.hamcrest.Matchers.containsString("userId=12345")));

        verify(kakaoService, times(1)).processKakaoLogin(authorizationCode);
    }

    @Test
    @DisplayName("카카오 콜백 실패 - 카카오에서 에러 반환")
    void 카카오_콜백_실패_카카오_에러() throws Exception {
        // Given
        String errorCode = "access_denied";

        // When & Then
        mockMvc.perform(get("/api/auth/kakao/callback")
                        .param("error", errorCode)
                        .contentType(MediaType.APPLICATION_JSON))
                .andDo(print())
                .andExpect(status().isFound()) // 302 리다이렉트 상태 확인
                .andExpect(header().string("Location", org.hamcrest.Matchers.containsString("158.179.169.48")))
                .andExpect(header().string("Location", org.hamcrest.Matchers.containsString("error=" + errorCode)));

        // 에러가 있으면 서비스 호출하지 않음
        verify(kakaoService, never()).processKakaoLogin(anyString());
    }

    @Test
    @DisplayName("카카오 콜백 실패 - 인가코드와 에러 모두 누락")
    void 카카오_콜백_실패_파라미터_누락() throws Exception {
        // Given - code도 error도 없는 상태

        // When & Then
        mockMvc.perform(get("/api/auth/kakao/callback")
                        .contentType(MediaType.APPLICATION_JSON))
                .andDo(print())
                .andExpect(status().isFound()) // 302 리다이렉트 상태 확인
                .andExpect(header().string("Location", org.hamcrest.Matchers.containsString("error=missing_authorization_code")));

        verify(kakaoService, never()).processKakaoLogin(anyString());
    }
}