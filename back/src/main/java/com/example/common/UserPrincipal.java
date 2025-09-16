package com.example.common;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * JWT 토큰에서 추출한 사용자 정보를 담는 클래스
 * DB 조회 없이 토큰에서 사용자 정보를 가져올 수 있도록 함
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class UserPrincipal {
    private Long accountId;
    private String email;
    private String role;
    private String userName;

    /**
     * 사용자 이름 반환 (null 체크 포함)
     */
    public String getUserName() {
        return userName != null ? userName : "";
    }


    /**
     * 역할 반환 (null 체크 포함)
     */
    public String getRole() {
        return role != null ? role : "ROLE_USER";
    }

    /**
     * 관리자 여부 확인
     */
    public boolean isAdmin() {
        return "ROLE_ADMIN".equals(role);
    }
}
