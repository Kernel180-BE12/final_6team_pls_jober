/**
 * 비밀번호 재설정
 */

package com.example.controller;

import com.example.dto.ForgotPasswordRequest;
import com.example.dto.ResetPasswordRequest;
import com.example.service.PasswordResetService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth/pw")
@RequiredArgsConstructor
public class PasswordResetController {

    private final PasswordResetService passwordResetService;

    // 토큰 발급
    @PostMapping("/request")
    public ResponseEntity<?> requestPasswordReset(@RequestBody ForgotPasswordRequest request) {
        String token = passwordResetService.createPasswordResetToken(request);
        return ResponseEntity.ok(
                Map.of(
                        "message", "비밀번호 재설정 토큰이 발급되었습니다.",
                        "token", token
                )
        );
    }

    // 비밀번호 재설정
    @PostMapping("/reset")
    public ResponseEntity<?> resetPassword(@RequestBody ResetPasswordRequest request) {
        passwordResetService.resetPassword(request);
        return ResponseEntity.ok(
                Map.of(
                        "message", "비밀번호가 성공적으로 변경되었습니다."
                )
        );
    }
}

