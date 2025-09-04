package com.example.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

public class MyPageDto {

    @NoArgsConstructor @AllArgsConstructor
    @Getter @Builder
    public static class UserInfoResponse {
        private Long id;
        private String name;
        private String email;
        private String password;
    }
}
