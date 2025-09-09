package com.example.repository;

import com.example.entity.Category2;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface Category2Repository extends JpaRepository<Category2, Long> {
    Optional<Category2> findByName(String name);
}