package com.example.service;

import com.example.dto.FastAPIResponseDto;
import com.example.dto.TemplateRequestDto;
import com.example.dto.TemplateResponseDto;
import com.example.entity.*;
import com.example.exception.ResourceNotFoundException;
import com.example.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 템플릿 생성 및 관리를 위한 비즈니스 로직을 처리하는 서비스입니다.
 */
@Slf4j
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class TemplateService {

    private final TemplateRepository templateRepository;
    private final Category2Repository category2Repository;
    private final AIService aiService; // FastAPI 통신을 전담할 서비스 주입

    /**
     * AI를 활용하여 새로운 템플릿을 생성하고 연관된 변수들을 함께 저장합니다.
     */
    @Transactional
    public TemplateResponseDto createTemplateWithAi(TemplateRequestDto requestDto, Account account) {
        Category2 category2 = findCategory2ById(requestDto.getCategory2Id());
        FastAPIResponseDto aiResponse = aiService.generateTemplateDataFromFastAPI(requestDto.getUserMessage(), category2.getName());
        Template newTemplate = Template.createFromAi(account, category2, aiResponse);
        Template savedTemplate = templateRepository.save(newTemplate);
        log.info("AI 템플릿 및 변수 저장 완료. Template ID: {}", savedTemplate.getTemplateId());

        return TemplateResponseDto.fromEntity(savedTemplate);
    }


    /**
     * 주어진 ID로 Category2 엔티티를 조회합니다.
     *
     * @param category2Id 조회할 Category2의 ID
     * @return 조회된 Category2 엔티티
     * @throws ResourceNotFoundException 해당 ID의 Category2가 존재하지 않을 경우
     */
    private Category2 findCategory2ById(Long category2Id) {
        return category2Repository.findById(category2Id)
                .orElseThrow(() -> new ResourceNotFoundException("Category2 not found with id: " + category2Id));
    }
}