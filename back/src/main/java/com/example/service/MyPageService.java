package com.example.service;

import com.example.dto.MyPageDto;
import com.example.entity.Account;
import com.example.repository.AccountRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class MyPageService {

    private final AccountRepository accountRepository;
    private final PasswordEncoder passwordEncoder;

    // Account 엔티티 객체를 MyPageDto.UserInfoResponse DTO로 변환
    @Transactional(readOnly = true)
    public MyPageDto.UserInfoResponse toUserInfoResponse(Long accountId) {
        Account user = accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalArgumentException("Account not found"));
        return new MyPageDto.UserInfoResponse(
                user.getId(),
                user.getUserName(),
                user.getEmail()
        );
    }

    // 이름 업데이트: 값이 있을 때만 반영
    @Transactional
    public MyPageDto.UserInfoResponse updateName(Long id, MyPageDto.UpdateNameRequest req) {
        Account user = accountRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Account not found"));

        if (req.getName() == null || req.getName().isBlank()) {
            throw new IllegalArgumentException("이름은 비어 있을 수 없습니다.");
        }

        user.setUserName(req.getName().trim());
        return toUserInfoResponse(user.getId());
    }

    // 이메일(=로그인 아이디) 변경: 현재 비번 재검증 + 중복 검사 + 버전 증가
    @Transactional
    public MyPageDto.UserInfoResponse updateEmail(Long id, MyPageDto.UpdateEmailRequest req) {
        Account user = accountRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Account not found"));

        // 1) 현재 비밀번호 재검증 (평문 vs 해시 → matches)
        if (!passwordEncoder.matches(req.getCurrentPassword(), user.getPasswordHash())) {
            throw new IllegalArgumentException("Current password is incorrect");
        }

        // 2) 이메일 정규화(정책에 따라 trim/lowercase)
        String newEmail = req.getEmail().trim().toLowerCase();

        // 3) 본인 제외 중복 검사
        if (accountRepository.existsByEmailAndIdNot(newEmail, id)) {
            throw new IllegalArgumentException("Email already exists");
        }

        // 4) 반영 + 자격증명 버전 증가(기존 토큰 무효화 용도)
        user.setEmail(newEmail);
        // ToDo: 자격증명 버전 증가

        return toUserInfoResponse(user.getId());
    }

    // 비밀번호 변경: 현재 비번 검증 + 새/확인 일치(Validator) + 해시 저장 + 버전 증가
    @Transactional
    public void updatePassword(Long id, MyPageDto.UpdatePasswordRequest req) {
        Account user = accountRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Account not found"));

        // 현재 비밀번호 검증 (절대 평문과 해시를 equals 비교하지 말 것!)
        if (!passwordEncoder.matches(req.getCurrentPassword(), user.getPasswordHash())) {
            throw new IllegalArgumentException("Current password is incorrect");
        }

        // @PasswordMatch가 DTO 레벨에서 new == confirm을 이미 검증하므로 여기선 새 비번만 인코딩 저장
        user.setPasswordHash(passwordEncoder.encode(req.getNewPassword()));

        // 비밀번호 변경 후에도 기존 토큰 무효화를 위해 버전 증가
        // ToDo: 자격증명 버전 증가
    }

    // 내 정보 조회
    public MyPageDto.UserInfoResponse getMe(Long id) {
        Account user = accountRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Account not found"));
        return toUserInfoResponse(user.getId());
    }
}
