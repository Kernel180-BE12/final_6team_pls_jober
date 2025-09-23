package com.example.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * 카카오 사용자 정보 DTO
 */
@Getter
@Setter
@NoArgsConstructor
public class KakaoUserInfo {
    
    private Long id;
    
    @JsonProperty("connected_at")
    private String connectedAt;
    
    private Properties properties;
    
    @JsonProperty("kakao_account")
    private KakaoAccount kakaoAccount;
    
    @Getter
    @Setter
    @NoArgsConstructor
    public static class Properties {
        private String nickname;
    }
    
    @Getter
    @Setter
    @NoArgsConstructor
    public static class KakaoAccount {
        @JsonProperty("profile_nickname_needs_agreement")
        private Boolean profileNicknameNeedsAgreement;
        
        private Profile profile;
        
        @JsonProperty("has_email")
        private Boolean hasEmail;
        
        @JsonProperty("email_needs_agreement")
        private Boolean emailNeedsAgreement;
        
        @JsonProperty("is_email_valid")
        private Boolean isEmailValid;
        
        @JsonProperty("is_email_verified")
        private Boolean isEmailVerified;
        
        private String email;
    }
    
    @Getter
    @Setter
    @NoArgsConstructor
    public static class Profile {
        private String nickname;
    }
}