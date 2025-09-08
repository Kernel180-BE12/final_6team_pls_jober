package com.example.repository;

import com.example.entity.Account;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AccountRepository extends JpaRepository<Account, Long> {
    // 이메일 수정 시 중복 체크를 하기위함
    boolean existsByEmailAndIdNot(String email, Long accountId);

    Optional<Account> findByUserName(String username);

    Optional<Account> findByEmail(String email);

    boolean existsByUserName(String username);

    boolean existsByEmail(String email);
}
