package com.example.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.*;
import org.hibernate.annotations.OnDelete;
import org.hibernate.annotations.OnDeleteAction;

@Getter
@Entity
@Table(name = "policy_refs")
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PolicyRef {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "policy_refs_id", nullable = false)
    private Long id;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @OnDelete(action = OnDeleteAction.CASCADE)
    @JoinColumn(name = "template_id", nullable = false)
    @Setter
    private Template template;

    @Size(max = 100)
    @NotNull
    @Column(name = "doc_id", nullable = false, length = 100)
    private String docId;

}