package com.example.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

/**
 * Account 생성/수정 요청용 DTO
 * 클라이언트로부터 받을 수 있는 안전한 정보만 포함
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class AccountRequestDto {
    
    @NotBlank(message = "사용자 이름은 필수 입력 값입니다.")
    @Size(max = 50, message = "사용자 이름은 50자를 초과할 수 없습니다.")
    private String userName;
    
    @Email(message = "올바른 이메일 형식이 아닙니다.")
    @NotBlank(message = "이메일은 필수 입력 값입니다.")
    @Size(max = 255, message = "이메일은 255자를 초과할 수 없습니다.")
    private String email;
    
    @NotBlank(message = "비밀번호는 필수 입력 값입니다.")
    @Size(min = 8, max = 255, message = "비밀번호는 8자 이상 255자 이하여야 합니다.")
    private String password;
    
    @Size(max = 20, message = "전화번호는 20자를 초과할 수 없습니다.")
    private String phoneNumber;
    
    @Size(max = 100, message = "회사명은 100자를 초과할 수 없습니다.")
    private String companyName;
    
    @Size(max = 12, message = "사업자등록번호는 12자를 초과할 수 없습니다.")
    private String bizRegNo;
    
    /**
     * AccountRequestDto를 Account 엔티티로 변환
     * 
     * @return Account 엔티티
     */
    public com.example.entity.Account toEntity() {
        com.example.entity.Account account = new com.example.entity.Account();
        account.setUserName(this.userName);
        account.setEmail(this.email);
        account.setPasswordHash(this.password); // 서비스에서 암호화 처리
        account.setPhoneNumber(this.phoneNumber);
        account.setCompanyName(this.companyName);
        account.setBizRegNo(this.bizRegNo);
        // role, status는 서비스에서 기본값 설정
        return account;
    }
}
