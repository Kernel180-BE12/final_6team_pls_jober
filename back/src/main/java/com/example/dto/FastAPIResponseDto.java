package com.example.dto;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;

import java.util.*;
import java.util.Map;

@Getter
public final class FastAPIResponseDto {

    private final String templateTitle; // AI가 생성한 제목
    private final String body;          // AI가 생성한 본문 ({{var}} 포함)
    private final Map<String, String> variables; // AI가 추출한 변수 키-값 맵
    private final String links;  // AI가 추출한 URL
    private final List<String> policyRefs; // AI가 참조한 정책/템플릿 ID 목록

    @JsonCreator
    public FastAPIResponseDto(
            @JsonProperty("template_title") String templateTitle,
            @JsonProperty("body") String body,
            @JsonProperty("variables") Map<String, String> variables,
            @JsonProperty("links") String links,
            @JsonProperty("policy_refs") List<String> policyRefs
    ) {
        this.templateTitle = templateTitle;
        this.body = body;
        this.links = links; // AI가 제공하는 단일 URL
        this.policyRefs = (policyRefs != null) ? policyRefs : Collections.emptyList();
        this.variables = (variables != null) ? variables : Collections.emptyMap();
    }
}