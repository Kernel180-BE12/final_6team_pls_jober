package com.example.controller;

import com.example.entity.Account;
import com.example.dto.MyPageDto;
import com.example.dto.UserDto;
import com.example.service.MyPageService;
import com.example.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/mypage")
@RequiredArgsConstructor
public class MyPageController {

    private final MyPageService myPageService;
    private final UserService userService;

    // 내 정보 조회
    @GetMapping
    public ResponseEntity<MyPageDto.UserInfoResponse> me(@AuthenticationPrincipal Account currentUser){
        UserDto userDto = userService.convertToUserDto(currentUser);
        return ResponseEntity.ok(myPageService.getMe(userDto));
    }


    // 이름 수정: 값이 있을 때만 반영
    @PutMapping("/name")
    public ResponseEntity<MyPageDto.UserInfoResponse> updateName(
            @Valid @RequestBody MyPageDto.UpdateNameRequest request,
            @AuthenticationPrincipal Account currentUser) {
        UserDto userDto = userService.convertToUserDto(currentUser);
        return ResponseEntity.ok(myPageService.updateName(userDto, request));
    }

    // 이메일(=로그인 아이디) 변경: 현재 비밀번호 재검증 + 중복 검사
    @PutMapping("/email")
    public ResponseEntity<MyPageDto.UserInfoResponse> updateEmail(
            @Valid @RequestBody MyPageDto.UpdateEmailRequest request,
            @AuthenticationPrincipal Account currentUser) {
        UserDto userDto = userService.convertToUserDto(currentUser);
        return ResponseEntity.ok(myPageService.updateEmail(userDto, request));
    }

    // 비밀번호 변경: 현재 비번 검증 + 새/확인 일치
    @PutMapping("/password")
    public ResponseEntity<Void> updatePassword(
            @Valid @RequestBody MyPageDto.UpdatePasswordRequest request,
            @AuthenticationPrincipal Account currentUser) {
        UserDto userDto = userService.convertToUserDto(currentUser);
        myPageService.updatePassword(userDto, request);
        return ResponseEntity.noContent().build();
        // 비번 변경 후 노출하지 않기 위해서 noContent(204처리)
    }
}
