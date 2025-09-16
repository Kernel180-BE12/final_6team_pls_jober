package com.example.controller;

import com.example.dto.FastAPIResponseDto;
import com.example.dto.TemplateRequestDto;
import com.example.dto.TemplateValidationRequestDto;
import com.example.dto.TemplateValidationResponseDto;
import com.example.common.UserPrincipal;
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
    public ResponseEntity<FastAPIResponseDto> createTemplateWithAi(
            @Valid @RequestBody TemplateRequestDto requestDto,
            @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        // 사용자 정보를 로그에 출력 (DB 조회 없이 토큰에서 가져온 정보)
        System.out.println("사용자 " + currentUser.getUserName() + "(" + currentUser.getEmail() + ")가 AI 템플릿 생성을 요청했습니다.");
        FastAPIResponseDto response = templateService.createTemplateWithAi(requestDto);
        return ResponseEntity.ok(response);
    }

    /**
     * 템플릿을 검증합니다. (POST /api/template/validate)
     */
    @PostMapping("/template/validate")
    public ResponseEntity<?> validateTemplate(
            @Valid @RequestBody TemplateValidationRequestDto requestDto,
            @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        try {
            // 사용자 정보를 로그에 출력 (DB 조회 없이 토큰에서 가져온 정보)
            System.out.println("사용자 " + currentUser.getUserName() + "(" + currentUser.getEmail() + ")가 템플릿 검증을 요청했습니다.");
            TemplateValidationResponseDto response = templateService.validateTemplate(requestDto, currentUser);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "템플릿 검증 중 오류가 발생했습니다: " + e.getMessage()));
        }
    }
}