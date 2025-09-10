package com.example.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;
import java.util.List;
import java.util.Map;

@Getter
@Setter
public class TemplateValidationRequestDto {
    @NotBlank(message = "템플릿 내용은 비어 있을 수 없습니다.")
    private String templateContent;
    
    @NotNull(message = "변수 정보는 필수입니다.")
    private Map<String, Object> variables;
    
    private String category;
    private String userMessage;
    
    // 변수 정보를 저장하기 위한 추가 필드
    private List<VariableDto> variableList;
    
    @Getter
    @Setter
    public static class VariableDto {
        private String variableKey;
        private String variableValue;
    }
}
