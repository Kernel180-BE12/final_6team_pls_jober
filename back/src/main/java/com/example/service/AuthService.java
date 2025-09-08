/**
 * 실제 인증/회원가입 로직
 */
package com.example.service;

import com.example.dto.LoginRequest;
import com.example.dto.SignupRequest;
import com.example.entity.Account;
import com.example.repository.AccountRepository;
import com.example.config.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final AccountRepository accountRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;

    /**
     * 회원가입
     */
    @Transactional
    public Account registerUser(SignupRequest request) {
        if (accountRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("이미 사용 중인 이메일입니다.");
        }
        if (accountRepository.existsByUserName(request.getUsername())) {
            throw new IllegalArgumentException("이미 사용 중인 사용자 이름입니다.");
        }

        Account account = new Account();
        account.setUserName(request.getUsername());
        account.setEmail(request.getEmail());
        account.setPasswordHash(passwordEncoder.encode(request.getPassword()));

        // 기본값 세팅
        account.setRole("USER");
        account.setStatus("ACTIVE");

        return accountRepository.save(account);
    }

    /**
     * 로그인 - JWT 사용
     */
    @Transactional(readOnly = true)
    public Map<String, String> login(LoginRequest request) {
        Account account = accountRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new IllegalArgumentException("이메일 또는 비밀번호가 올바르지 않습니다."));

        if (!passwordEncoder.matches(request.getPassword(), account.getPasswordHash())) {
            throw new IllegalArgumentException("이메일 또는 비밀번호가 올바르지 않습니다.");
        }

        // JWT 발급
        String accessToken = jwtTokenProvider.createAccessToken(account.getEmail(), account.getRole());
        String refreshToken = jwtTokenProvider.createRefreshToken();

        Map<String, String> tokens = new HashMap<>();
        tokens.put("accessToken", accessToken);
        tokens.put("refreshToken", refreshToken);
        tokens.put("userId", account.getId().toString());
        return tokens;
    }
}
