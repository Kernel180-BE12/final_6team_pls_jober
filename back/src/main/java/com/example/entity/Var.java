package com.example.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.*;

@Getter
@Entity
@Table(name = "var")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Var {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "variable_id", nullable = false)
    private Long varId;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "template_id", nullable = false)
    @Setter
    private Template template;

    @Size(max = 100)
    @NotNull
    @Column(name = "variable_key", nullable = false, length = 100)
    private String variableKey;

    @Size(max = 1000)
    @Column(name = "variable_value", length = 1000)
    private String variableValue;


    @Builder
    public Var(String variableKey, String variableValue) {
        this.variableKey = variableKey;
        this.variableValue = variableValue;
    }
}