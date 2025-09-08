package com.example.dto;

import com.example.entity.*;
import lombok.Builder;
import lombok.Getter;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Getter
@Builder
public class TemplateResponseDto {
    private Long templateId;
    private String autoTitle;
    private String templateContent;
    private Map<String, String> variables;
    private String imageUrl;
    private String status;


    // 관계 데이터
    private String accountName;
    private String categoryName;
    private String buttonText;
    private String buttonUrl;
    private String templateAddon;
    private List<String> policyRefs;

    public static TemplateResponseDto fromEntity(Template template) {
        // Var 리스트를 <Key, Value> 형태의 Map으로 변환합니다.
        Map<String, String> variablesMap = template.getVariables().stream()
                .collect(Collectors.toMap(Var::getVariableKey, var -> var.getVariableValue() != null ? var.getVariableValue() : ""));

        // PolicyRef 리스트를 docId 문자열 리스트로 변환합니다.
        List<String> docIds = template.getPolicyRefs().stream()
                .map(PolicyRef::getDocId)
                .collect(Collectors.toList());

        return TemplateResponseDto.builder()
                .templateId(template.getTemplateId())
                .autoTitle(template.getAutoTitle())
                .templateContent(template.getTemplateContent())
                .variables(variablesMap)
                .imageUrl(template.getImageUrl())
                .status(template.getStatus())
                .accountName(template.getAccount() != null ? template.getAccount().getUserName() : null)
                .categoryName(template.getCategory2() != null ? template.getCategory2().getName() : null)
                .buttonText(template.getButtonText())
                .buttonUrl(template.getButtonUrl())
                .templateAddon(template.getTemplateAddon())
                .policyRefs(docIds)
                .build();
    }
}