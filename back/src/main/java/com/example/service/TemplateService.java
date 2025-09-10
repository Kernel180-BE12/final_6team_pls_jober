package com.example.service;

import com.example.dto.FastAPIResponseDto;
import com.example.dto.TemplateRequestDto;
import com.example.dto.TemplateResponseDto;
import com.example.dto.TemplateValidationRequestDto;
import com.example.dto.TemplateValidationResponseDto;
import com.example.entity.*;
import com.example.exception.ResourceNotFoundException;
import com.example.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.*;

/**
 * 템플릿 생성 및 관리를 위한 비즈니스 로직을 처리하는 서비스입니다.
 */
@Slf4j
@Service
@RequiredArgsConstructor
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
     * 템플릿을 검증합니다.
     */
    @Transactional
    public TemplateValidationResponseDto validateTemplate(TemplateValidationRequestDto requestDto, Account account) {
        try {
            log.info("템플릿 검증 시작: {}", requestDto.getTemplateContent().substring(0, Math.min(50, requestDto.getTemplateContent().length())));
            
            // AI 서버로 검증 요청
            Map<String, Object> validationRequest = new HashMap<>();
            validationRequest.put("user_input", requestDto.getTemplateContent());
            validationRequest.put("variables", requestDto.getVariables());
            
            // AI 서버 검증 호출 (실제로는 AIService를 통해 호출)
            Map<String, Object> aiValidationResult = aiService.validateTemplateWithFastAPI(validationRequest);
            
            // AI 서버 응답에서 success 필드 확인
            boolean isValid = false;
            if (aiValidationResult.containsKey("success")) {
                isValid = (Boolean) aiValidationResult.get("success");
            } else if (aiValidationResult.containsKey("is_valid")) {
                isValid = (Boolean) aiValidationResult.get("is_valid");
            }
            
            log.info("AI 검증 결과 - 성공 여부: {}", isValid);
            
            if (isValid) {
                // 검증 성공 시 템플릿 저장
                Template template = Template.builder()
                        .account(account)
                        .templateContent(requestDto.getTemplateContent())
                        .category2(findCategory2ByName(requestDto.getCategory()))
                        .status("APPROVED")
                        .build();
                
                // 변수 정보 저장
                if (requestDto.getVariableList() != null && !requestDto.getVariableList().isEmpty()) {
                    for (TemplateValidationRequestDto.VariableDto variableDto : requestDto.getVariableList()) {
                        Var variable = Var.builder()
                                .variableKey(variableDto.getVariableKey())
                                .variableValue(variableDto.getVariableValue())
                                .build();
                        template.addVariable(variable);
                    }
                }
                
                Template savedTemplate = templateRepository.save(template);
                log.info("검증 성공, 템플릿 및 변수 저장 완료: {}", savedTemplate.getTemplateId());
                
                return TemplateValidationResponseDto.success(savedTemplate.getTemplateId().toString());
            } else {
                // 검증 실패 시 반려 사유와 대안 제공
                List<String> rejectedVariables = new ArrayList<>();
                Map<String, List<String>> alternatives = new HashMap<>();
                List<TemplateValidationResponseDto.ValidationError> validationErrors = new ArrayList<>();
                
                log.info("AI 검증 실패 응답 전체: {}", aiValidationResult);
                
                // AI 서버 응답에서 반려된 변수들 추출
                if (aiValidationResult.containsKey("rejected_variables")) {
                    @SuppressWarnings("unchecked")
                    List<String> rejectedVars = (List<String>) aiValidationResult.get("rejected_variables");
                    rejectedVariables.addAll(rejectedVars);
                } else if (aiValidationResult.containsKey("failed_validations")) {
                    // failed_validations에서 변수명과 오류 메시지 추출
                    @SuppressWarnings("unchecked")
                    List<Map<String, Object>> failedValidations = (List<Map<String, Object>>) aiValidationResult.get("failed_validations");
                    for (Map<String, Object> validation : failedValidations) {
                        String errorType = (String) validation.getOrDefault("validator_name", "unknown");
                        @SuppressWarnings("unchecked")
                        List<String> errors = (List<String>) validation.getOrDefault("errors", new ArrayList<>());
                        
                        if (validation.containsKey("details") && validation.get("details") instanceof Map) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> details = (Map<String, Object>) validation.get("details");
                            if (details.containsKey("variables")) {
                                Object variables = details.get("variables");
                                if (variables instanceof List) {
                                    @SuppressWarnings("unchecked")
                                    List<String> varList = (List<String>) variables;
                                    rejectedVariables.addAll(varList);
                                    
                                    // 각 변수에 대한 오류 정보 생성
                                    for (String varName : varList) {
                                        for (String error : errors) {
                                            validationErrors.add(new TemplateValidationResponseDto.ValidationError(
                                                varName, error, errorType
                                            ));
                                        }
                                    }
                                } else if (variables instanceof String) {
                                    String varName = (String) variables;
                                    rejectedVariables.add(varName);
                                    
                                    // 변수에 대한 오류 정보 생성
                                    for (String error : errors) {
                                        validationErrors.add(new TemplateValidationResponseDto.ValidationError(
                                            varName, error, errorType
                                        ));
                                    }
                                }
                            }
                        }
                    }
                } else if (aiValidationResult.containsKey("validation_results")) {
                    // validation_results에서 오류 정보 추출
                    @SuppressWarnings("unchecked")
                    List<Map<String, Object>> validationResults = (List<Map<String, Object>>) aiValidationResult.get("validation_results");
                    for (Map<String, Object> result : validationResults) {
                        boolean resultIsValid = (Boolean) result.getOrDefault("is_valid", true);
                        if (!resultIsValid) {
                            String validatorName = (String) result.getOrDefault("validator_name", "unknown");
                            @SuppressWarnings("unchecked")
                            List<String> errors = (List<String>) result.getOrDefault("errors", new ArrayList<>());
                            
                            if (result.containsKey("details") && result.get("details") instanceof Map) {
                                @SuppressWarnings("unchecked")
                                Map<String, Object> details = (Map<String, Object>) result.get("details");
                                if (details.containsKey("variables")) {
                                    Object variables = details.get("variables");
                                    if (variables instanceof List) {
                                        @SuppressWarnings("unchecked")
                                        List<String> varList = (List<String>) variables;
                                        rejectedVariables.addAll(varList);
                                        
                                        for (String varName : varList) {
                                            for (String error : errors) {
                                                validationErrors.add(new TemplateValidationResponseDto.ValidationError(
                                                    varName, error, validatorName
                                                ));
                                            }
                                        }
                                    } else if (variables instanceof String) {
                                        String varName = (String) variables;
                                        rejectedVariables.add(varName);
                                        
                                        for (String error : errors) {
                                            validationErrors.add(new TemplateValidationResponseDto.ValidationError(
                                                varName, error, validatorName
                                            ));
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                
                // 대안 정보 추출
                if (aiValidationResult.containsKey("alternatives")) {
                    @SuppressWarnings("unchecked")
                    Map<String, List<String>> altMap = (Map<String, List<String>>) aiValidationResult.get("alternatives");
                    alternatives.putAll(altMap);
                }
                
                log.info("검증 실패, 반려된 변수: {}, 오류 정보: {}", rejectedVariables, validationErrors);
                return TemplateValidationResponseDto.rejectionWithDetails(rejectedVariables, alternatives, validationErrors);
            }
            
        } catch (Exception e) {
            log.error("템플릿 검증 중 오류 발생", e);
            throw new RuntimeException("템플릿 검증 중 오류가 발생했습니다: " + e.getMessage());
        }
    }

    /**
     * 주어진 ID로 Category2 엔티티를 조회합니다.
     *
     * @param category2Id 조회할 Category2의 ID
     * @return 조회된 Category2 엔티티
     * @throws ResourceNotFoundException 해당 ID의 Category2가 존재하지 않을 경우
     */
    @Transactional(readOnly = true)
    public Category2 findCategory2ById(Long category2Id) {
        return category2Repository.findById(category2Id)
                .orElseThrow(() -> new ResourceNotFoundException("Category2 not found with id: " + category2Id));
    }
    
    /**
     * 주어진 이름으로 Category2 엔티티를 조회합니다.
     */
    @Transactional(readOnly = true)
    public Category2 findCategory2ByName(String categoryName) {
        return category2Repository.findByName(categoryName)
                .orElseThrow(() -> new ResourceNotFoundException("Category2 not found with name: " + categoryName));
    }
}