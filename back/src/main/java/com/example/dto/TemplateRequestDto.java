package com.example.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.Setter;
import java.util.List;

@Getter
@Setter
public class TemplateRequestDto {
    @NotBlank(message = "사용자 메시지는 비어 있을 수 없습니다.")
    private String userMessage;
    
    private String templateContent;
    private String templateTitle;
    private List<Object> chatHistory;
}