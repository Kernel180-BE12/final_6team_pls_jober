package com.example.dto;

import lombok.Getter;

import java.util.List;

@Getter
public class TemplateSaveRequestDto {
    private String templateContent;
    private String templateTitle;
    private List<String> variableList;  // 단순 문자열 배열로 변경
    private String category;
    private String buttonText;
    private String userMessage;
}
