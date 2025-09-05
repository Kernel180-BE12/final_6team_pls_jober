package com.example.controller;

import com.example.config.JwtTokenProvider;
import com.example.dto.LoginRequest;
import com.example.dto.SignupRequest;
import com.example.entity.Account;
import com.example.repository.AccountRepository;
import com.example.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;
    private final JwtTokenProvider jwtTokenProvider;
    private final PasswordEncoder passwordEncoder;
    private final AccountRepository accountRepository;

    // 회원가입
    @PostMapping("/signup")
    public ResponseEntity<?> signup(@RequestBody SignupRequest request) {
        Account account = authService.registerUser(request);
        return ResponseEntity.ok(Map.of(
                "message", "회원가입 성공",
                "username", account.getUsername()
        ));
    }

    // 로그인 → JWT 반환
    @PostMapping("/login")
    public Map<String, String> login(@RequestBody LoginRequest request) {
        Account account = accountRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new IllegalArgumentException("이메일 또는 비밀번호가 올바르지 않습니다."));

        System.out.println("입력 비밀번호: " + request.getPassword());
        System.out.println("DB 비밀번호 해시: " + account.getPassword());
        System.out.println("매칭 결과: " + passwordEncoder.matches(request.getPassword(), account.getPassword()));

        if (!passwordEncoder.matches(request.getPassword(), account.getPassword())) {
            throw new IllegalArgumentException("이메일 또는 비밀번호가 올바르지 않습니다.");
        }

        // AccessToken + RefreshToken 발급
        String accessToken = jwtTokenProvider.createAccessToken(account.getEmail(), account.getRole());
        String refreshToken = jwtTokenProvider.createRefreshToken();

        Map<String, String> tokens = new HashMap<>();
        tokens.put("accessToken", accessToken);
        tokens.put("refreshToken", refreshToken);

        return tokens;
    }
}
