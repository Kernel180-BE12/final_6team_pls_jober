package com.example.service;

import com.example.dto.FastAPIRequestDto;
import com.example.dto.FastAPIResponseDto;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import java.util.Map;


/**
 * FastAPI AI 서버와의 통신을 전담하는 서비스입니다.
 */
@Slf4j
@Service
public class AIService {
    private final WebClient webClient;
    private final String apiPath;

    /**
     * AIService의 생성자입니다.
     * application.yml에 설정된 FastAPI 서버 URL과 경로를 주입받아 WebClient 인스턴스를 초기화합니다.
     *
     * @param webClientBuilder Spring이 제공하는 WebClient 빌더
     * @param fastapiUrl       application.yml에서 주입받는 FastAPI 서버의 기본 URL
     * @param apiPath          application.yml에서 주입받는 FastAPI 서버의 API 경로
     */
    public AIService(WebClient.Builder webClientBuilder,
                     @Value("${ai.fastapi.url}") String fastapiUrl,
                     @Value("${ai.fastapi.path}") String apiPath) {
        this.webClient = webClientBuilder.baseUrl(fastapiUrl).build();
        this.apiPath = apiPath;
    }


    /**
     * FastAPI 서버에 텍스트 생성을 요청하고 결과를 받아옵니다.
     *
     * @param userMessage 사용자가 입력한 원본 텍스트
     * @param categoryName 템플릿이 속할 카테고리 이름
     * @return AI가 생성한 구조화된 템플릿 데이터 DTO
     * @throws RuntimeException AI 서버 통신 실패 시
     */
    public FastAPIResponseDto generateTemplateDataFromFastAPI(String userMessage, String categoryName) {
        log.info("FastAPI 서버 호출 시작. 내용: '{}', 카테고리: '{}'", userMessage, categoryName);
        FastAPIRequestDto request = new FastAPIRequestDto(userMessage, categoryName);

        return webClient.post()
                .uri(apiPath)
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(request)
                .retrieve()
                .bodyToMono(FastAPIResponseDto.class)
                .block();
    }

    /**
     * FastAPI 서버에 템플릿 검증을 요청하고 결과를 받아옵니다.
     *
     * @param validationRequest 검증 요청 데이터
     * @return AI 검증 결과
     * @throws RuntimeException AI 서버 통신 실패 시
     */
    public Map<String, Object> validateTemplateWithFastAPI(Map<String, Object> validationRequest) {
        log.info("FastAPI 템플릿 검증 요청 시작");
        
        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> result = webClient.post()
                    .uri("/alimtalk/validate")
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(validationRequest)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
            return result;
        } catch (Exception e) {
            log.error("FastAPI 템플릿 검증 요청 실패", e);
            // 검증 실패 시 기본 반려 응답 반환
            return Map.of(
                "success", false,
                "rejected_variables", java.util.List.of("템플릿 내용"),
                "alternatives", Map.of("템플릿 내용", java.util.List.of("더 적절한 표현으로 수정해주세요"))
            );
        }
    }
}