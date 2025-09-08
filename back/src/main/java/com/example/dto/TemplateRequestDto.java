package com.example.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class TemplateRequestDto {
    @NotNull(message = "카테고리 ID는 필수입니다.")
    private Long category2Id;

    @NotBlank(message = "사용자 메시지는 비어 있을 수 없습니다.")
    private String userMessage;
}