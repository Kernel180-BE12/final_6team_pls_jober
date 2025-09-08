package com.example.entity;

import com.example.dto.FastAPIResponseDto;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Getter
@NoArgsConstructor
public class  Template {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "template_id", columnDefinition = "bigint")
    private Long templateId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "account_id")
    private Account account;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category2_id")
    private Category2 category2;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "industry_id")
    private Industry industry;

    @Column(name = "template_content", columnDefinition = "TEXT")
    private String templateContent;

    @Column(name = "auto_title", length = 255)
    private String autoTitle;

    @Column(name = "image_url", length = 255)
    private String imageUrl;

    @Column(name = "status", length = 20)
    private String status;

    @Column(name = "button_text", length = 100)
    private String buttonText;

    @Column(name = "button_url", length = 1000)
    private String buttonUrl;

    @Column(name = "template_addon", length = 1000)
    private String templateAddon;

    // Template과 Var는 1:N 관계 (Template이 1, Var가 N)
    // mappedBy는 "Var" 엔티티에 있는 "template" 필드를 의미합니다.
    // CascadeType.ALL은 Template 저장/삭제 시 Var도 함께 처리하도록 합니다.
    @OneToMany(mappedBy = "template", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Var> variables = new ArrayList<>();

    // Template과 PolicyRef는 1:N 관계
    @OneToMany(mappedBy = "template", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<PolicyRef> policyRefs = new ArrayList<>();

    @CreationTimestamp
    @Column(name = "created_at")
    private LocalDateTime createdAt;


    @Builder
    private Template(Account account, Category2 category2, Industry industry, String templateContent, String autoTitle, String imageUrl, String status, String buttonText, String buttonUrl, String templateAddon) {
        this.account = account;
        this.category2 = category2;
        this.industry = industry;
        this.templateContent = templateContent;
        this.autoTitle = autoTitle;
        this.imageUrl = imageUrl;
        this.status = status;
        this.buttonText = buttonText;
        this.buttonUrl = buttonUrl;
        this.templateAddon = templateAddon;
    }

    // 연관관계 편의 메소드: Var를 추가할 때 Template도 함께 설정
    public void addVariable(Var variable) {
        this.variables.add(variable);
        variable.setTemplate(this);
    }

    // 연관관계 편의 메소드: PolicyRef를 추가할 때 Template도 함께 설정
    public void addPolicyRef(PolicyRef policyRef) {
        this.policyRefs.add(policyRef);
        policyRef.setTemplate(this);
    }

    /**
     * AI 응답 DTO를 기반으로 Template 엔티티와 하위 Var 엔티티들을 생성하는 정적 팩토리 메소드입니다.
     * @param account 연관 계정
     * @param category2 연관 카테고리
     * @param aiResponse AI 서비스로부터 받은 응답 DTO
     * @return 완전히 구성된 Template 인스턴스
     */

    public static Template createFromAi(Account account, Category2 category2, FastAPIResponseDto aiResponse) {
        Template template = Template.builder()
                .account(account)
                .category2(category2)
                .templateContent(aiResponse.getBody())
                .autoTitle(aiResponse.getTemplateTitle())
                .buttonUrl(aiResponse.getLinks())
                .status("CREATED")
                .build();

        aiResponse.getVariables().forEach((key, value) ->
                template.addVariable(Var.builder().variableKey(key).variableValue(value).build())
        );

        aiResponse.getPolicyRefs().forEach(docId ->
                template.addPolicyRef(PolicyRef.builder().docId(docId).build())
        );

        return template;
    }
}