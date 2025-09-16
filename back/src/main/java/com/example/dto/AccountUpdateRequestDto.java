package com.example.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

/**
 * Account 수정 요청용 DTO
 * 수정 시에만 필요한 필드들만 포함 (비밀번호 제외)
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class AccountUpdateRequestDto {
    
    @Size(max = 50, message = "사용자 이름은 50자를 초과할 수 없습니다.")
    private String userName;
    
    @Email(message = "올바른 이메일 형식이 아닙니다.")
    @Size(max = 255, message = "이메일은 255자를 초과할 수 없습니다.")
    private String email;
    
    @Size(max = 20, message = "전화번호는 20자를 초과할 수 없습니다.")
    private String phoneNumber;
    
    @Size(max = 100, message = "회사명은 100자를 초과할 수 없습니다.")
    private String companyName;
    
    @Size(max = 12, message = "사업자등록번호는 12자를 초과할 수 없습니다.")
    private String bizRegNo;
    
    /**
     * 기존 Account 엔티티에 수정 요청 내용을 적용
     * 
     * @param existingAccount 기존 Account 엔티티
     * @return 수정된 Account 엔티티
     */
    public com.example.entity.Account applyToEntity(com.example.entity.Account existingAccount) {
        if (this.userName != null) {
            existingAccount.setUserName(this.userName);
        }
        if (this.email != null) {
            existingAccount.setEmail(this.email);
        }
        if (this.phoneNumber != null) {
            existingAccount.setPhoneNumber(this.phoneNumber);
        }
        if (this.companyName != null) {
            existingAccount.setCompanyName(this.companyName);
        }
        if (this.bizRegNo != null) {
            existingAccount.setBizRegNo(this.bizRegNo);
        }
        return existingAccount;
    }
}
