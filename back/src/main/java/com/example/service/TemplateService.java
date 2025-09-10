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
            
            boolean isValid = isValidationSuccessful(aiValidationResult);
            log.info("AI 검증 결과 - 성공 여부: {}", isValid);
            
            if (isValid) {
                return handleApproval(requestDto, account);
            }
            
            RejectionDetails rejectionDetails = extractRejectionDetails(aiValidationResult);
            log.info("검증 실패, 반려된 변수: {}, 오류 정보: {}", rejectionDetails.rejectedVariables, rejectionDetails.validationErrors);
            return TemplateValidationResponseDto.rejectionWithDetails(
                    rejectionDetails.rejectedVariables,
                    rejectionDetails.alternatives,
                    rejectionDetails.validationErrors
            );
            
        } catch (Exception e) {
            log.error("템플릿 검증 중 오류 발생", e);
            throw new RuntimeException("템플릿 검증 중 오류가 발생했습니다: " + e.getMessage());
        }
    }

    private boolean isValidationSuccessful(Map<String, Object> aiValidationResult) {
        Object success = aiValidationResult.get("success");
        if (success instanceof Boolean) {
            return (Boolean) success;
        }
        Object isValid = aiValidationResult.get("is_valid");
        if (isValid instanceof Boolean) {
            return (Boolean) isValid;
        }
        return false;
    }

    private TemplateValidationResponseDto handleApproval(TemplateValidationRequestDto requestDto, Account account) {
        Template template = Template.builder()
                .account(account)
                .templateContent(requestDto.getTemplateContent())
                .category2(findCategory2ByName(requestDto.getCategory()))
                .status("APPROVED")
                .build();
        
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
    }

    private RejectionDetails extractRejectionDetails(Map<String, Object> aiValidationResult) {
        log.info("AI 검증 실패 응답 전체: {}", aiValidationResult);
        RejectionDetails details = new RejectionDetails();
        
        if (aiValidationResult.containsKey("rejected_variables")) {
            @SuppressWarnings("unchecked")
            List<String> rejectedVars = (List<String>) aiValidationResult.get("rejected_variables");
            if (rejectedVars != null) {
                details.rejectedVariables.addAll(rejectedVars);
            }
        } else if (aiValidationResult.containsKey("failed_validations")) {
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> failedValidations = (List<Map<String, Object>>) aiValidationResult.get("failed_validations");
            if (failedValidations != null) {
                for (Map<String, Object> validation : failedValidations) {
                    String validatorName = (String) validation.getOrDefault("validator_name", "unknown");
                    @SuppressWarnings("unchecked")
                    List<String> errors = (List<String>) validation.getOrDefault("errors", new ArrayList<>());
                    addErrorsFromDetailsVariable(validation.get("details"), validatorName, errors, details);
                }
            }
        } else if (aiValidationResult.containsKey("validation_results")) {
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> validationResults = (List<Map<String, Object>>) aiValidationResult.get("validation_results");
            if (validationResults != null) {
                for (Map<String, Object> result : validationResults) {
                    boolean resultIsValid = (Boolean) result.getOrDefault("is_valid", true);
                    if (resultIsValid) {
                        continue;
                    }
                    String validatorName = (String) result.getOrDefault("validator_name", "unknown");
                    @SuppressWarnings("unchecked")
                    List<String> errors = (List<String>) result.getOrDefault("errors", new ArrayList<>());
                    addErrorsFromDetailsVariable(result.get("details"), validatorName, errors, details);
                }
            }
        }
        
        if (aiValidationResult.containsKey("alternatives")) {
            @SuppressWarnings("unchecked")
            Map<String, List<String>> altMap = (Map<String, List<String>>) aiValidationResult.get("alternatives");
            if (altMap != null) {
                details.alternatives.putAll(altMap);
            }
        }
        
        return details;
    }

    private void addErrorsFromDetailsVariable(Object detailsObject,
                                              String validatorName,
                                              List<String> errors,
                                              RejectionDetails aggregate) {
        if (!(detailsObject instanceof Map)) {
            return;
        }
        @SuppressWarnings("unchecked")
        Map<String, Object> details = (Map<String, Object>) detailsObject;
        if (!details.containsKey("variables")) {
            return;
        }
        Object variables = details.get("variables");
        if (variables instanceof List) {
            @SuppressWarnings("unchecked")
            List<String> variableNames = (List<String>) variables;
            aggregate.rejectedVariables.addAll(variableNames);
            for (String variableName : variableNames) {
                for (String error : errors) {
                    aggregate.validationErrors.add(new TemplateValidationResponseDto.ValidationError(
                            variableName, error, validatorName
                    ));
                }
            }
        } else if (variables instanceof String) {
            String variableName = (String) variables;
            aggregate.rejectedVariables.add(variableName);
            for (String error : errors) {
                aggregate.validationErrors.add(new TemplateValidationResponseDto.ValidationError(
                        variableName, error, validatorName
                ));
            }
        }
    }

    private static class RejectionDetails {
        private final List<String> rejectedVariables = new ArrayList<>();
        private final Map<String, List<String>> alternatives = new HashMap<>();
        private final List<TemplateValidationResponseDto.ValidationError> validationErrors = new ArrayList<>();
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