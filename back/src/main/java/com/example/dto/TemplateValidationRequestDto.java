package com.example.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.core.JsonParser;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.io.IOException;

@Getter
@Setter
@JsonIgnoreProperties(ignoreUnknown = true)
public class TemplateValidationRequestDto {
    @NotBlank(message = "템플릿 내용은 비어 있을 수 없습니다.")
    private String templateContent;
    
    private String category;
    private String userMessage;
    private String templateTitle;
    private String templateId; // 템플릿 ID 추가
    
    // 변수 정보를 저장하기 위한 필드
    @NotNull(message = "변수 정보는 필수입니다.")
    @JsonDeserialize(using = VariableListDeserializer.class)
    private List<Map<String, String>> variableList = new ArrayList<>();
    
    // VariableList용 커스텀 디시리얼라이저
    public static class VariableListDeserializer extends JsonDeserializer<List<Map<String, String>>> {
        @Override
        public List<Map<String, String>> deserialize(JsonParser p, DeserializationContext ctxt) throws IOException {
            JsonNode node = p.getCodec().readTree(p);
            List<Map<String, String>> result = new ArrayList<>();
            
            if (node.isArray()) {
                for (JsonNode item : node) {
                    if (item.isObject()) {
                        Map<String, String> map = new java.util.HashMap<>();
                        item.fields().forEachRemaining(entry -> {
                            map.put(entry.getKey(), entry.getValue().asText());
                        });
                        result.add(map);
                    } else if (item.isTextual()) {
                        // 문자열인 경우 딕셔너리로 변환
                        Map<String, String> map = new java.util.HashMap<>();
                        map.put("variableKey", item.asText());
                        map.put("variableValue", "");
                        result.add(map);
                    }
                }
            }
            return result;
        }
    }
}
