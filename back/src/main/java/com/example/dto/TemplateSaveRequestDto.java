package com.example.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;

import java.util.List;
import java.util.ArrayList;

@Getter
@Setter
public class TemplateSaveRequestDto {
    @JsonProperty("templateContent")
    private String templateContent;
    
    @JsonProperty("templateTitle")
    private String templateTitle;
    
    @JsonProperty("variableList")
    private List<String> variableList = new ArrayList<>();
    
    @JsonProperty("category")
    private String category;
    
    @JsonProperty("buttonText")
    private String buttonText;
    
    @JsonProperty("userMessage")
    private String userMessage;
    
    // Jackson이 Object를 받을 때 String 배열로 변환하는 메서드
    @JsonProperty("variableList")
    public void setVariableList(Object variableListObj) {
        this.variableList = new ArrayList<>();
        
        if (variableListObj instanceof List) {
            List<?> list = (List<?>) variableListObj;
            for (Object item : list) {
                if (item != null) {
                    this.variableList.add(item.toString());
                }
            }
        } else if (variableListObj instanceof String[]) {
            String[] array = (String[]) variableListObj;
            for (String item : array) {
                if (item != null) {
                    this.variableList.add(item);
                }
            }
        } else if (variableListObj != null) {
            // 단일 값인 경우
            this.variableList.add(variableListObj.toString());
        }
    }
}
