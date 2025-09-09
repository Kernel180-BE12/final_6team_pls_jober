package com.example.controller;

import com.example.dto.TemplateRequestDto;
import com.example.dto.TemplateResponseDto;
import com.example.dto.TemplateValidationRequestDto;
import com.example.dto.TemplateValidationResponseDto;
import com.example.entity.Account;
import jakarta.validation.Valid;
import com.example.service.TemplateService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
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
            @Valid @RequestBody TemplateRequestDto requestDto,
            @AuthenticationPrincipal Account authenticatedAccount
    ) {
        TemplateResponseDto response = templateService.createTemplateWithAi(requestDto, authenticatedAccount);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * 템플릿을 검증합니다. (POST /api/template/validate)
     */
    @PostMapping("/template/validate")
    public ResponseEntity<?> validateTemplate(
            @Valid @RequestBody TemplateValidationRequestDto requestDto,
            @AuthenticationPrincipal Account authenticatedAccount
    ) {
        try {
            TemplateValidationResponseDto response = templateService.validateTemplate(requestDto, authenticatedAccount);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "템플릿 검증 중 오류가 발생했습니다: " + e.getMessage()));
        }
    }
}