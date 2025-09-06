package com.example.controller;

import com.example.dto.TemplateRequestDto;
import com.example.dto.TemplateResponseDto;
import com.example.entity.Account;
import jakarta.validation.Valid;
import com.example.service.TemplateService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

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
}