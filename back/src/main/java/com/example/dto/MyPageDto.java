package com.example.dto;

import com.example.common.Validation.PasswordMatch;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.*;

public class MyPageDto {

    // 마이페이지 조회 응답
    @NoArgsConstructor @AllArgsConstructor
    @Getter @Builder
    public static class UserInfoResponse {
        private Long id;
        private String name;
        private String email;
    }

    // 프로필 수정 (이름/전화)
    @Getter @Setter
    public static class UpdateNameRequest {
        private String name;
    }

    // 이메일 변경 (로그인 아이디)
    @Getter @Setter
    public static class UpdateEmailRequest {
        @NotBlank @Email
        private String email;
        @NotBlank
        private String currentPassword; // 재검증
    }

    // 비밀번호 변경
    @Getter @Setter
    @PasswordMatch  // new == confirm 인지 확인
    public static class UpdatePasswordRequest {
        @NotBlank
        private String currentPassword;
        @NotBlank
        private String newPassword;
        @NotBlank
        private String confirmPassword;
    }

}
