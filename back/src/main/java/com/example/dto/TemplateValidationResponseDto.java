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
    private List<ValidationError> validationErrors;
    
    @Getter
    @Setter
    public static class ValidationError {
        private String variableName;
        private String errorMessage;
        private String errorType;
        
        public ValidationError(String variableName, String errorMessage, String errorType) {
            this.variableName = variableName;
            this.errorMessage = errorMessage;
            this.errorType = errorType;
        }
    }
    
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
    
    public static TemplateValidationResponseDto rejectionWithDetails(List<String> rejectedVariables, Map<String, List<String>> alternatives, List<ValidationError> validationErrors) {
        TemplateValidationResponseDto response = new TemplateValidationResponseDto();
        response.setSuccess(false);
        response.setMessage("템플릿 검증에서 문제가 발견되었습니다.");
        response.setRejectedVariables(rejectedVariables);
        response.setAlternatives(alternatives);
        response.setValidationErrors(validationErrors);
        return response;
    }
}
