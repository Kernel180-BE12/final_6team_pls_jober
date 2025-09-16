package com.example.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

/**
 * Account 응답용 DTO
 * 보안상 민감한 정보(passwordHash, bizRegNo 등)는 제외하고
 * 클라이언트에게 안전하게 노출할 수 있는 정보만 포함
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AccountResponseDto {
    
    private Long id;
    private String userName;
    private String email;
    private String role;
    private String status;
    private String companyName;
    private String phoneNumber;
    private LocalDateTime createdAt;
    
    /**
     * Account 엔티티를 AccountResponseDto로 변환하는 정적 팩토리 메서드
     * 
     * @param account 변환할 Account 엔티티
     * @return AccountResponseDto
     */
    public static AccountResponseDto fromEntity(com.example.entity.Account account) {
        if (account == null) {
            return null;
        }
        
        return AccountResponseDto.builder()
                .id(account.getId())
                .userName(account.getUserName())
                .email(account.getEmail())
                .role(account.getRole())
                .status(account.getStatus())
                .companyName(account.getCompanyName())
                .phoneNumber(account.getPhoneNumber())
                .createdAt(account.getCreatedAt())
                .build();
    }
    
    /**
     * Account 엔티티 리스트를 AccountResponseDto 리스트로 변환
     * 
     * @param accounts 변환할 Account 엔티티 리스트
     * @return AccountResponseDto 리스트
     */
    public static java.util.List<AccountResponseDto> fromEntityList(java.util.List<com.example.entity.Account> accounts) {
        if (accounts == null) {
            return java.util.Collections.emptyList();
        }
        
        return accounts.stream()
                .map(AccountResponseDto::fromEntity)
                .collect(java.util.stream.Collectors.toList());
    }
}
