package com.example.service;

import com.example.dto.UserDto;
import com.example.entity.Account;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

/**
 * 사용자 관련 공통 서비스
 * Account 엔티티와 UserDto 간의 변환을 담당합니다.
 */
@Service
@RequiredArgsConstructor
public class UserService {
    
    /**
     * Account 엔티티를 UserDto로 변환
     * 필요한 필드만 노출하여 보안을 강화합니다.
     * 
     * @param account 변환할 Account 엔티티
     * @return UserDto 객체
     */
    public UserDto convertToUserDto(Account account) {
        if (account == null) {
            throw new IllegalArgumentException("Account는 null일 수 없습니다");
        }
        
        return new UserDto(
            account.getId(),
            account.getEmail(),
            account.getRole(),
            account.getUserName(),
            account.getStatus()
        );
    }
}
