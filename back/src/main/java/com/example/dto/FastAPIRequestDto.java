package com.example.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;


@Getter
public final class FastAPIRequestDto {
    @JsonProperty("text")
    private final String text;

    @JsonProperty("category")
    private final String category;

    public FastAPIRequestDto(String text, String category) {
        this.text = text;
        this.category = category;
    }
}