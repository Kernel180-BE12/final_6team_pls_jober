package com.example.controller;

import com.example.common.AuthSupport;
import com.example.dto.MyPageDto;
import com.example.service.MyPageService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/mypage")
@RequiredArgsConstructor
public class MyPageController {

    private final MyPageService myPageService;

    @GetMapping
    public ResponseEntity<MyPageDto.UserInfoResponse> me(){
        Long id = AuthSupport.currentUserId();
        return ResponseEntity.ok(myPageService.getMe(id));
    }
}
