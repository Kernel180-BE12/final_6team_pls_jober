package com.example.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;
import java.util.Map;

@Getter
@Setter
@NoArgsConstructor
public class FastAPIResponseDto {

    @JsonProperty("template_text")
    private String templateText;

    @JsonProperty("template_title")
    private String templateTitle;

    @JsonProperty("generation_method")
    private String generationMethod;

    @JsonProperty("reference_template_id")
    private String referenceTemplateId;

    @JsonProperty("metadata")
    private MetadataDto metadata;

    @Getter
    @Setter
    @NoArgsConstructor
    public static class MetadataDto {
        @JsonProperty("request_info")
        private RequestInfoDto requestInfo;

        @JsonProperty("reference_templates")
        private List<Map<String, Object>> referenceTemplates;

        @JsonProperty("generation_flow")
        private String generationFlow;

        @JsonProperty("variables_detected")
        private List<String> variablesDetected;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    public static class RequestInfoDto {
        @JsonProperty("category_sub")
        private String categorySub;
    }
}