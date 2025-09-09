package com.example.dto;

import lombok.Getter;
import lombok.Setter;
import java.util.List;
import java.util.Map;

@Getter
@Setter
public class TemplateValidationResponseDto {
    private boolean success;
    private String message;
    private List<String> rejectedVariables;
    private Map<String, List<String>> alternatives;
    private String templateId;
    
    public static TemplateValidationResponseDto success(String templateId) {
        TemplateValidationResponseDto response = new TemplateValidationResponseDto();
        response.setSuccess(true);
        response.setMessage("템플릿 검증이 완료되었습니다.");
        response.setTemplateId(templateId);
        return response;
    }
    
    public static TemplateValidationResponseDto rejection(List<String> rejectedVariables, Map<String, List<String>> alternatives) {
        TemplateValidationResponseDto response = new TemplateValidationResponseDto();
        response.setSuccess(false);
        response.setMessage("템플릿 검증에서 문제가 발견되었습니다.");
        response.setRejectedVariables(rejectedVariables);
        response.setAlternatives(alternatives);
        return response;
    }
}
