package com.example.service;

import com.example.dto.MyPageDto;
import com.example.entity.Account;
import com.example.repository.AccountRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class MyPageService {

    private final AccountRepository accountRepository;

    @Transactional(readOnly = true)
    public MyPageDto.UserInfoResponse getMe(Long accountId) {
        Account account = accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalArgumentException("Account not found"));
        return new MyPageDto.UserInfoResponse(
                account.getAccountId(),
                account.getUserName(),
                account.getEmail(),
                account.getPasswordHash()
        );
    }
}
