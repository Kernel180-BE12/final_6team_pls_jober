package com.example.controller;

import com.example.common.AuthSupport;
import com.example.dto.TemplateRequestDto;
import com.example.dto.TemplateResponseDto;
import com.example.dto.TemplateValidationRequestDto;
import com.example.dto.TemplateValidationResponseDto;
import jakarta.validation.Valid;
import com.example.service.TemplateService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class TemplateController {

    private final TemplateService templateService;

    /**
     * AI를 사용하여 새로운 템플릿을 생성합니다. (POST /api/ai-generation)
     */
    @PostMapping("/ai-generation")
    public ResponseEntity<TemplateResponseDto> createTemplateWithAi(
            @Valid @RequestBody TemplateRequestDto requestDto
    ) {
        // 로그인 없이도 사용 가능하도록 기본값 사용 (accountId = 1L)
        Long accountId = getCurrentUserIdOrDefault();
        TemplateResponseDto response = templateService.createTemplateWithAi(requestDto, accountId);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * 템플릿을 검증합니다. (POST /api/template/validate)
     */
    @PostMapping("/template/validate")
    public ResponseEntity<?> validateTemplate(
            @Valid @RequestBody TemplateValidationRequestDto requestDto
    ) {
        try {
            Long accountId = getCurrentUserIdOrDefault(); // 로그인 없이도 사용 가능하도록 기본값 사용
            TemplateValidationResponseDto response = templateService.validateTemplate(requestDto, accountId);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "템플릿 검증 중 오류가 발생했습니다: " + e.getMessage()));
        }
    }

    /**
     * 최종 템플릿을 저장합니다. (POST /api/template)
     * - 프론트에서 검증 성공 후 호출
     */
    @PostMapping("/template")
    public ResponseEntity<Map<String, Object>> finalizeTemplate(
            @Valid @RequestBody TemplateValidationRequestDto requestDto
    ) {
        try {
            Long accountId = getCurrentUserIdOrDefault(); // 로그인 없이도 사용 가능하도록 기본값 사용
            var saved = templateService.saveFinalTemplate(requestDto, accountId);
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(Map.of(
                            "success", true,
                            "templateId", saved.getTemplateId()
                    ));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "최종 저장 중 오류가 발생했습니다: " + e.getMessage()));
        }
    }

    /**
     * 현재 사용자 ID를 가져오거나 기본값을 반환합니다.
     * 로그인하지 않은 사용자도 템플릿 생성이 가능하도록 합니다.
     */
    private Long getCurrentUserIdOrDefault() {
        try {
            return AuthSupport.currentUserId();
        } catch (Exception e) {
            // 로그인하지 않은 경우 기본 사용자 ID 사용 (1L)
            return 1L;
        }
    }
}