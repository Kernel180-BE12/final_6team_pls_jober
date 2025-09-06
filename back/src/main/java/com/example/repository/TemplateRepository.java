package com.example.repository;

import com.example.entity.Template;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Optional;

/**
 * Template 엔티티에 대한 데이터베이스 작업을 처리하는 JPA 리포지토리입니다.
 */
public interface TemplateRepository extends JpaRepository<Template, Long> {
    /**
     * ID로 템플릿을 조회할 때 연관된 모든 엔티티를 JOIN FETCH하여 N+1 문제를 해결합니다.
     */
    @Query("SELECT t FROM Template t " +
           "LEFT JOIN FETCH t.account " +
           "LEFT JOIN FETCH t.category2 " +
           "LEFT JOIN FETCH t.industry " +
           "LEFT JOIN FETCH t.variables " +
           "WHERE t.templateId = :id")
    Optional<Template> findByIdWithDetails(@Param("id") Long id);
}