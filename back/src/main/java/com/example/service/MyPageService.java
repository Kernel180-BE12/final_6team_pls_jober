package com.example.service;

import com.example.dto.MyPageDto;
import com.example.entity.Account;
import com.example.repository.AccountRepository;
import com.example.common.UserPrincipal;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class MyPageService {

    private final AccountRepository accountRepository;
    private final PasswordEncoder passwordEncoder;

    // JWT 토큰에서 가져온 사용자 정보를 DTO로 변환 (DB 조회 없이)
    @Transactional(readOnly = true)
    public MyPageDto.UserInfoResponse toUserInfoResponse(UserPrincipal currentUser) {
        return new MyPageDto.UserInfoResponse(
                currentUser.getAccountId(),
                currentUser.getUserName(),
                currentUser.getEmail()
        );
    }

    // 이름 업데이트: 값이 있을 때만 반영
    @Transactional
    public MyPageDto.UserInfoResponse updateName(UserPrincipal currentUser, MyPageDto.UpdateNameRequest req) {
        if (req.getName() == null || req.getName().isBlank()) {
            throw new IllegalArgumentException("이름은 비어 있을 수 없습니다.");
        }

        // DB에서 사용자 정보 업데이트
        Account user = accountRepository.findById(currentUser.getAccountId())
                .orElseThrow(() -> new IllegalArgumentException("Account not found"));
        user.setUserName(req.getName().trim());
        accountRepository.save(user);

        // JWT 토큰 정보로 응답 생성
        return toUserInfoResponse(currentUser);
    }

    // 이메일(=로그인 아이디) 변경: 현재 비번 재검증 + 중복 검사 + 버전 증가
    @Transactional
    public MyPageDto.UserInfoResponse updateEmail(UserPrincipal currentUser, MyPageDto.UpdateEmailRequest req) {
        Account user = accountRepository.findById(currentUser.getAccountId())
                .orElseThrow(() -> new IllegalArgumentException("Account not found"));

        // 1) 현재 비밀번호 재검증 (평문 vs 해시 → matches)
        if (!passwordEncoder.matches(req.getCurrentPassword(), user.getPasswordHash())) {
            throw new IllegalArgumentException("Current password is incorrect");
        }

        // 2) 이메일 정규화(정책에 따라 trim/lowercase)
        String newEmail = req.getEmail().trim().toLowerCase();

        // 3) 본인 제외 중복 검사
        if (accountRepository.existsByEmailAndIdNot(newEmail, currentUser.getAccountId())) {
            throw new IllegalArgumentException("Email already exists");
        }

        // 4) 반영 + 자격증명 버전 증가(기존 토큰 무효화 용도)
        user.setEmail(newEmail);
        accountRepository.save(user);
        // ToDo: 자격증명 버전 증가

        return toUserInfoResponse(currentUser);
    }

    // 비밀번호 변경: 현재 비번 검증 + 새/확인 일치(Validator) + 해시 저장 + 버전 증가
    @Transactional
    public void updatePassword(UserPrincipal currentUser, MyPageDto.UpdatePasswordRequest req) {
        Account user = accountRepository.findById(currentUser.getAccountId())
                .orElseThrow(() -> new IllegalArgumentException("Account not found"));

        // 현재 비밀번호 검증 (절대 평문과 해시를 equals 비교하지 말 것!)
        if (!passwordEncoder.matches(req.getCurrentPassword(), user.getPasswordHash())) {
            throw new IllegalArgumentException("Current password is incorrect");
        }

        // @PasswordMatch가 DTO 레벨에서 new == confirm을 이미 검증하므로 여기선 새 비번만 인코딩 저장
        user.setPasswordHash(passwordEncoder.encode(req.getNewPassword()));
        accountRepository.save(user);

        // 비밀번호 변경 후에도 기존 토큰 무효화를 위해 버전 증가
        // ToDo: 자격증명 버전 증가
    }

    // 내 정보 조회 (JWT 토큰에서 가져온 정보 사용)
    public MyPageDto.UserInfoResponse getMe(UserPrincipal currentUser) {
        return toUserInfoResponse(currentUser);
    }
}
