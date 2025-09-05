package com.example.repository;

import com.example.entity.Account;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface AccountRepository extends JpaRepository<Account, Long> {
    // 이메일 수정 시 중복 체크를 하기위함
    boolean existsByEmailAndAccountIdNot(String email, Long accountId);
}
