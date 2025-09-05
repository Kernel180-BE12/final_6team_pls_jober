package com.example.service;

import com.example.entity.Account;
import com.example.repository.AccountRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class AccountService {

    private final AccountRepository accountRepository;
    private final PasswordEncoder passwordEncoder;

    // 모든 사용자 조회
    public List<Account> getAllAccounts() {
        return accountRepository.findAll();
    }

    // ID로 사용자 조회
    public Optional<Account> getAccountById(Long id) {
        return accountRepository.findById(id);
    }

    // username으로 사용자 조회
    public Optional<Account> getAccountByUsername(String username) {
        return accountRepository.findByUsername(username);
    }

    // 사용자 생성
    public Account createAccount(Account account) {
        // 비밀번호 해시화
        account.setPassword(passwordEncoder.encode(account.getPassword()));
        // 기본값 설정
        account.setRole("USER");
        account.setStatus("ACTIVE");
        return accountRepository.save(account);
    }

    // 사용자 수정
    public Account updateAccount(Long id, Account accountDetails) {
        return accountRepository.findById(id)
                .map(account -> {
                    account.setUsername(accountDetails.getUsername());
                    account.setEmail(accountDetails.getEmail());
                    if (accountDetails.getPassword() != null && !accountDetails.getPassword().isEmpty()) {
                        account.setPassword(passwordEncoder.encode(accountDetails.getPassword()));
                    }
                    return accountRepository.save(account);
                })
                .orElseThrow(() -> new RuntimeException("Account not found"));
    }

    // 사용자 삭제
    public void deleteAccount(Long id) {
        accountRepository.deleteById(id);
    }

    // username 중복 확인
    public boolean existsByUsername(String username) {
        return accountRepository.existsByUsername(username);
    }

    // email 중복 확인
    public boolean existsByEmail(String email) {
        return accountRepository.existsByEmail(email);
    }
}
