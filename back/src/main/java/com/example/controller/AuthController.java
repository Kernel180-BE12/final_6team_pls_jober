package com.example.controller;

import com.example.dto.LoginRequest;
import com.example.dto.SignupRequest;
import com.example.entity.User;
import com.example.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final AuthService authService;

    /**
     * 회원가입
     */
    @PostMapping("/signup")
    public ResponseEntity<String> signup(@RequestBody SignupRequest request) {
        User user = authService.registerUser(request);
        return ResponseEntity.ok("회원가입 성공: " + user.getUsername());
    }

    /**
     * 로그인
     */
    @PostMapping("/login")
    public ResponseEntity<String> login(@RequestBody LoginRequest request) {
        try {
            User user = authService.login(request);
            return ResponseEntity.ok("로그인 성공: " + user.getEmail());
        } catch (IllegalArgumentException e) {

            // 에러 출력
            System.out.println("오류 : " + e.getMessage());
            return ResponseEntity.badRequest().body("회원가입 실패 : " + e.getMessage());
        }
    }
}
