package com.example.common.Validation;

import com.example.dto.MyPageDto;
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

// 비밀번호 검증 구현
public class PasswordMatchValidator implements ConstraintValidator<PasswordMatch, MyPageDto.UpdatePasswordRequest> {
    @Override
    public boolean isValid(MyPageDto.UpdatePasswordRequest dto, ConstraintValidatorContext ctx) {
        if (dto == null) return true;

        String np = dto.getNewPassword();
        String cp = dto.getConfirmPassword();

        // 하나라도 null이면 실패 (필드에 @NotBlank 있으니 거의 안 걸림)
        if (np == null || cp == null) {
            return false;
        }

        // 값이 있으면 반드시 일치해야 함
        return np.equals(cp);
    }
}