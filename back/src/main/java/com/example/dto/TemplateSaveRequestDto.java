package com.example.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;

@Getter
@Setter
public class TemplateSaveRequestDto {
    @JsonProperty("templateContent")
    private String templateContent;
    
    @JsonProperty("templateTitle")
    private String templateTitle;
    
    @JsonProperty("variableList")
    private List<Map<String, String>> variableList = new ArrayList<>();
    
    @JsonProperty("category")
    private String category;
    
    @JsonProperty("buttonText")
    private String buttonText;
    
    @JsonProperty("userMessage")
    private String userMessage;
    
    // Jackson이 Object를 받을 때 Map 배열로 변환하는 메서드
    @JsonProperty("variableList")
    public void setVariableList(Object variableListObj) {
        this.variableList = new ArrayList<>();
        
        if (variableListObj instanceof List) {
            List<?> list = (List<?>) variableListObj;
            for (Object item : list) {
                if (item instanceof Map) {
                    Map<String, String> map = new java.util.HashMap<>();
                    ((Map<?, ?>) item).forEach((key, value) -> {
                        map.put(key.toString(), value != null ? value.toString() : "");
                    });
                    this.variableList.add(map);
                } else if (item != null) {
                    // 문자열인 경우 딕셔너리로 변환
                    Map<String, String> map = new java.util.HashMap<>();
                    map.put("variableKey", item.toString());
                    map.put("variableValue", "");
                    this.variableList.add(map);
                }
            }
        } else if (variableListObj instanceof String[]) {
            String[] array = (String[]) variableListObj;
            for (String item : array) {
                if (item != null) {
                    Map<String, String> map = new java.util.HashMap<>();
                    map.put("variableKey", item);
                    map.put("variableValue", "");
                    this.variableList.add(map);
                }
            }
        } else if (variableListObj != null) {
            // 단일 값인 경우
            Map<String, String> map = new java.util.HashMap<>();
            map.put("variableKey", variableListObj.toString());
            map.put("variableValue", "");
            this.variableList.add(map);
        }
    }
}
