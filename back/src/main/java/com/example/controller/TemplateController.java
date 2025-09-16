package com.example.controller;

import com.example.dto.FastAPIResponseDto;
import com.example.dto.TemplateRequestDto;
import com.example.dto.TemplateValidationRequestDto;
import com.example.dto.TemplateValidationResponseDto;
import com.example.entity.Account;
import com.example.dto.UserDto;
import com.example.service.TemplateService;
import com.example.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
@Slf4j
public class TemplateController {

    private final TemplateService templateService;
    private final UserService userService;

    /**
     * AI를 사용하여 새로운 템플릿을 생성합니다. (POST /api/ai-generation)
     */
    @PostMapping("/ai-generation")
    public ResponseEntity<FastAPIResponseDto> createTemplateWithAi(
            @Valid @RequestBody TemplateRequestDto requestDto,
            @AuthenticationPrincipal Account currentUser
    ) {
        UserDto userDto = userService.convertToUserDto(currentUser);
        // 사용자 정보를 로그에 출력 (UserDto에서 가져온 정보)
        System.out.println("사용자 " + userDto.getUserName() + "(" + userDto.getEmail() + ")가 AI 템플릿 생성을 요청했습니다.");
        FastAPIResponseDto response = templateService.createTemplateWithAi(requestDto);
        return ResponseEntity.ok(response);
    }

    /**
     * 템플릿을 검증합니다. (POST /api/template/validate)
     */
    @PostMapping("/template/validate")
    public ResponseEntity<?> validateTemplate(
            @Valid @RequestBody TemplateValidationRequestDto requestDto,
            @AuthenticationPrincipal Account currentUser
    ) {
        try {
            UserDto userDto = userService.convertToUserDto(currentUser);
            // 사용자 정보를 로그에 출력 (UserDto에서 가져온 정보)
            System.out.println("사용자 " + userDto.getUserName() + "(" + userDto.getEmail() + ")가 템플릿 검증을 요청했습니다.");
            TemplateValidationResponseDto response = templateService.validateTemplate(requestDto, userDto);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "템플릿 검증 중 오류가 발생했습니다: " + e.getMessage()));
        }
    }

    /**
     * AI를 사용하여 템플릿을 수정합니다. (POST /api/template/modify)
     */
    @PostMapping("/template/modify")
    public ResponseEntity<FastAPIResponseDto> modifyTemplate(
            @Valid @RequestBody TemplateRequestDto requestDto
    ) {
        try {
            log.info("템플릿 수정 요청 시작 - 템플릿 내용: {}, 제목: {}, 사용자 메시지: {}",
                    requestDto.getTemplateContent() != null ? requestDto.getTemplateContent().substring(0, Math.min(50, requestDto.getTemplateContent().length())) : "null",
                    requestDto.getTemplateTitle(),
                    requestDto.getUserMessage());
            log.info("요청 데이터 전체: {}", requestDto);

            FastAPIResponseDto response = templateService.modifyTemplateWithAi(requestDto);
            log.info("템플릿 수정 성공 - 응답: {}", response);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("템플릿 수정 중 오류 발생", e);
            log.error("오류 상세 정보 - 메시지: {}, 원인: {}", e.getMessage(), e.getCause());

            // 실패 시 원본 템플릿을 반환
            FastAPIResponseDto errorResponse = new FastAPIResponseDto();
            errorResponse.setTemplateText(requestDto.getTemplateContent());
            errorResponse.setTemplateTitle(requestDto.getTemplateTitle());
            errorResponse.setGenerationMethod("error");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
}