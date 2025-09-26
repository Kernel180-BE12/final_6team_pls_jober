package com.example.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class TemplateSaveResponseDto {
    private String templateId; // 저장된 템플릿 ID
    private boolean success; // 저장 성공 여부
    private String message; // 응답 메시지
    
    public static TemplateSaveResponseDto success(String templateId) {
        TemplateSaveResponseDto response = new TemplateSaveResponseDto();
        response.setSuccess(true);
        response.setMessage("템플릿 저장이 완료되었습니다.");
        response.setTemplateId(templateId);
        return response;
    }

    public static TemplateSaveResponseDto failure(String message) {
        TemplateSaveResponseDto response = new TemplateSaveResponseDto();
        response.setSuccess(false);
        response.setMessage(message);
        return response;
    }
}
