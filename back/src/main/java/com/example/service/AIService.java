package com.example.service;

import com.example.dto.FastAPIResponseDto;
import com.example.dto.TemplateRequestDto;
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

    /**
     * AIService의 생성자입니다.
     * application.yml에 설정된 FastAPI 서버 URL을 주입받아 WebClient 인스턴스를 초기화합니다.
     *
     * @param webClientBuilder Spring이 제공하는 WebClient 빌더
     * @param fastapiUrl       application.yml에서 주입받는 FastAPI 서버의 기본 URL
     */
    public AIService(WebClient.Builder webClientBuilder,
                     @Value("${ai.fastapi.url}") String fastapiUrl) {
        this.webClient = webClientBuilder.baseUrl(fastapiUrl).build();
    }



    /**
     * FastAPI 서버에 템플릿 검증을 요청하고 결과를 받아옵니다.
     *
     * @param validationRequest 검증 요청 데이터
     * @return AI 검증 결과
     * @throws RuntimeException AI 서버 통신 실패 시
     */
    public Map<String, Object> validateTemplateWithFastAPI(Map<String, Object> validationRequest) {
        log.info("FastAPI 템플릿 검증 요청 시작: {}", validationRequest);
        
        try {
            // AI 서버에 전송할 요청 형식으로 변환 (1차원 구조로 단순화)
            Map<String, Object> aiRequest = new java.util.HashMap<>();
            aiRequest.put("templateContent", validationRequest.get("user_input"));
            aiRequest.put("category", validationRequest.get("category"));
            aiRequest.put("userMessage", validationRequest.get("userMessage"));
            aiRequest.put("templateTitle", validationRequest.get("templateTitle"));
            aiRequest.put("variableList", validationRequest.get("variableList"));
            
            log.info("AI 서버로 전송할 요청: {}", aiRequest);
            
            @SuppressWarnings("unchecked")
            Map<String, Object> result = webClient.post()
                    .uri("/alimtalk/validate")
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(aiRequest)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
            
            log.info("AI 서버 검증 응답: {}", result);
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

    /**
     * FastAPI 서버에 템플릿 수정을 요청하고 결과를 받아옵니다.
     *
     * @param requestDto 템플릿 수정 요청 데이터
     * @return AI가 수정한 템플릿 데이터 DTO
     * @throws RuntimeException AI 서버 통신 실패 시
     */
    public FastAPIResponseDto modifyTemplateWithFastAPI(TemplateRequestDto requestDto) {
        log.info("FastAPI 템플릿 수정 요청 시작. 현재 템플릿: '{}', 사용자 메시지: '{}'", 
                requestDto.getTemplateContent() != null ? requestDto.getTemplateContent().substring(0, Math.min(50, requestDto.getTemplateContent().length())) : "null", 
                requestDto.getUserMessage());
        log.info("요청 DTO 전체 정보: {}", requestDto);
        
        try {
            // AI 서버에 전송할 요청 형식으로 변환
            Map<String, Object> aiRequest = Map.of(
                "current_template", requestDto.getTemplateContent(),
                "current_template_title", requestDto.getTemplateTitle(),
                "userMessage", requestDto.getUserMessage(),
                "chat_history", requestDto.getChatHistory() != null ? requestDto.getChatHistory() : java.util.List.of()
            );
            
            log.info("AI 서버로 전송할 템플릿 수정 요청: {}", aiRequest);
            log.info("AI 서버 URL: {}", webClient.mutate().build().toString());
            
            // AI 서버 응답을 Map으로 받아서 FastAPIResponseDto로 변환
            @SuppressWarnings("unchecked")
            Map<String, Object> aiResponse = webClient.post()
                    .uri("/ai/template/modify")
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(aiRequest)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
            
            log.info("AI 서버 템플릿 수정 응답: {}", aiResponse);
            
            // AI 서버 응답을 FastAPIResponseDto로 변환
            FastAPIResponseDto response = new FastAPIResponseDto();
            response.setTemplateText((String) aiResponse.get("modified_template"));
            response.setTemplateTitle((String) aiResponse.get("template_title"));
            response.setGenerationMethod("modification");
            response.setExplanation((String) aiResponse.get("explanation"));
            
            log.info("변환된 응답 DTO: {}", response);
            return response;
                    
        } catch (Exception e) {
            log.error("FastAPI 템플릿 수정 요청 실패", e);
            log.error("오류 상세 - 클래스: {}, 메시지: {}, 원인: {}", 
                    e.getClass().getSimpleName(), e.getMessage(), e.getCause());
            if (e.getCause() != null) {
                log.error("원인 오류 상세 - 클래스: {}, 메시지: {}", 
                        e.getCause().getClass().getSimpleName(), e.getCause().getMessage());
            }
            throw new RuntimeException("AI 서버 템플릿 수정 요청 중 오류가 발생했습니다: " + e.getMessage());
        }
    }
}