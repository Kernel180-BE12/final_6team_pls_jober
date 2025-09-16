package com.example.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * 사용자 정보를 안전하게 전달하기 위한 DTO
 * 필요한 필드만 노출하여 보안을 강화합니다.
 */
@Getter
@AllArgsConstructor
public class UserDto {
    private final Long accountId;
    private final String email;
    private final String role;
    private final String userName;
    private final String status;
    
    /**
     * 관리자 여부 확인
     */
    public boolean isAdmin() {
        return "ROLE_ADMIN".equals(role);
    }
    
    /**
     * 계정이 활성 상태인지 확인
     */
    public boolean isActive() {
        return "ACTIVE".equals(status);
    }
    
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
}
