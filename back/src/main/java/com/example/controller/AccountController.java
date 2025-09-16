package com.example.controller;

import com.example.dto.AccountRequestDto;
import com.example.dto.AccountResponseDto;
import com.example.dto.AccountUpdateRequestDto;
import com.example.entity.Account;
import com.example.service.AccountService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("api/accounts")
@RequiredArgsConstructor
public class AccountController {

    private final AccountService accountService;

    // 모든 사용자 조회
    @GetMapping
    public ResponseEntity<List<AccountResponseDto>> getAllAccounts() {
        List<Account> accounts = accountService.getAllAccounts();
        List<AccountResponseDto> responseDtos = AccountResponseDto.fromEntityList(accounts);
        return ResponseEntity.ok(responseDtos);
    }

    // ID로 사용자 조회
    @GetMapping("/{id}")
    public ResponseEntity<AccountResponseDto> getAccountById(@PathVariable Long id) {
        return accountService.getAccountById(id)
                .map(AccountResponseDto::fromEntity)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // 사용자 생성
    @PostMapping
    public ResponseEntity<AccountResponseDto> createAccount(@Valid @RequestBody AccountRequestDto requestDto) {
        if (accountService.existsByUsername(requestDto.getUserName())) {
            return ResponseEntity.badRequest().build();
        }
        if (accountService.existsByEmail(requestDto.getEmail())) {
            return ResponseEntity.badRequest().build();
        }

        Account createdAccount = accountService.createAccount(requestDto.toEntity());
        AccountResponseDto responseDto = AccountResponseDto.fromEntity(createdAccount);
        return ResponseEntity.ok(responseDto);
    }

    // 사용자 수정
    @PutMapping("/{id}")
    public ResponseEntity<AccountResponseDto> updateAccount(@PathVariable Long id, @Valid @RequestBody AccountUpdateRequestDto requestDto) {
        try {
            Account existingAccount = accountService.getAccountById(id)
                    .orElseThrow(() -> new RuntimeException("Account not found"));
            
            // 이메일 중복 체크 (본인 제외)
            if (requestDto.getEmail() != null && !requestDto.getEmail().equals(existingAccount.getEmail())) {
                if (accountService.existsByEmail(requestDto.getEmail())) {
                    return ResponseEntity.badRequest().build();
                }
            }
            
            // 사용자명 중복 체크 (본인 제외)
            if (requestDto.getUserName() != null && !requestDto.getUserName().equals(existingAccount.getUserName())) {
                if (accountService.existsByUsername(requestDto.getUserName())) {
                    return ResponseEntity.badRequest().build();
                }
            }
            
            Account updatedAccount = accountService.updateAccount(id, requestDto.applyToEntity(existingAccount));
            AccountResponseDto responseDto = AccountResponseDto.fromEntity(updatedAccount);
            return ResponseEntity.ok(responseDto);
        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        }
    }

    // 사용자 삭제
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteAccount(@PathVariable Long id) {
        accountService.deleteAccount(id);
        return ResponseEntity.ok().build();
    }
}
