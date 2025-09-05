package com.example.controller;

import com.example.common.AuthSupport;
import com.example.dto.MyPageDto;
import com.example.service.MyPageService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/mypage")
@RequiredArgsConstructor
public class MyPageController {

    private final MyPageService myPageService;
    private final PasswordEncoder passwordEncoder; // spring security bean 사용

    // 내 정보 조회
    @GetMapping
    public ResponseEntity<MyPageDto.UserInfoResponse> me(){
        Long id = AuthSupport.currentUserId();
        return ResponseEntity.ok(myPageService.getMe(id));
    }

    // 이름 수정: 값이 있을 때만 반영
    @PutMapping("/name")
    public ResponseEntity<MyPageDto.UserInfoResponse> updateName(
            @Valid @RequestBody MyPageDto.UpdateNameRequest request) {
        Long id = AuthSupport.currentUserId();
        return ResponseEntity.ok(myPageService.updateName(id, request));
    }

    // 이메일(=로그인 아이디) 변경: 현재 비밀번호 재검증 + 중복 검사
    @PutMapping("/email")
    public ResponseEntity<MyPageDto.UserInfoResponse> updateEmail(
            @Valid @RequestBody MyPageDto.UpdateEmailRequest request) {
        Long id = AuthSupport.currentUserId();
        return ResponseEntity.ok(myPageService.updateEmail(id, request));
    }

    // 비밀번호 변경: 현재 비번 검증 + 새/확인 일치
    @PutMapping("/password")
    public ResponseEntity<Void> updatePassword(
            @Valid @RequestBody MyPageDto.UpdatePasswordRequest request) {
        Long id = AuthSupport.currentUserId();
        myPageService.updatePassword(id, request);
        return ResponseEntity.noContent().build();
        // 비번 변경 후 노출하지 않기 위해서 noContent(204처리)
    }
}
