package com.example.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "category")
public class Category {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "category_id", nullable = false)
    private Long id;

    @Size(max = 100)
    @NotNull
    @Column(name = "name", nullable = false, length = 100)
    private String name;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive = true;

    @Column(name = "usage_count", nullable = false)
    private Integer usageCount = 0;

    @Size(max = 20)
    @NotNull
    @Column(name = "created_by", nullable = false, length = 20)
    private String createdBy;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    // Builder 패턴을 위한 생성자들
    
    @Builder
    public Category(String name, Boolean isActive, String createdBy) {
        this.name = name;
        this.isActive = isActive != null ? isActive : true;
        this.createdBy = createdBy;  // null 체크 제거, 명시적으로 받은 값 사용
        // usageCount, createdAt은 필드 기본값 사용
    }
}