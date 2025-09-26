package com.example.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;
import java.util.List;

@Getter
@Setter
public class TemplateValidationRequestDto {
    @NotBlank(message = "템플릿 내용은 비어 있을 수 없습니다.")
    private String templateContent;
    
    private String category;
    private String userMessage;
    private String templateTitle;
    private String templateId; // 템플릿 ID 추가
    
    // 변수 정보를 저장하기 위한 필드
    @NotNull(message = "변수 정보는 필수입니다.")
    private List<VariableDto> variableList;
    
    @Getter
    @Setter
    public static class VariableDto {
        private String variableKey;
        private String variableValue;
    }
}
