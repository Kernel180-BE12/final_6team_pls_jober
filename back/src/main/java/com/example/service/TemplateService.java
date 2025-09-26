package com.example.service;

import com.example.dto.*;
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
    private final CategoryRepository categoryRepository;
    private final AccountRepository accountRepository;
    private final AIService aiService; // FastAPI 통신을 전담할 서비스 주입


    // 수정에서 제출하기 버튼 클릭 시 템플릿 저장
    @Transactional
    public TemplateSaveResponseDto saveTemplate(TemplateSaveRequestDto requestDto, UserDto currentUser) {
        try {
            // 사용자 계정 조회
            Account account = accountRepository.findById(currentUser.getAccountId())
                    .orElseThrow(() -> new ResourceNotFoundException("사용자를 찾을 수 없습니다."));

            // 카테고리 조회
            Category category = findCategoryByName(requestDto.getCategory());

            // Template 생성
            Template template = Template.builder()
                    .account(account)
                    .templateContent(requestDto.getTemplateContent())
                    .category(category)
                    .userMessage(requestDto.getUserMessage()) // 사용자 원본 요청 저장
                    .autoTitle(requestDto.getTemplateTitle()) // 템플릿 제목 저장
                    .status("검증 중")
                    .build();

            if (requestDto.getVariableList() != null && !requestDto.getVariableList().isEmpty()) {
                // 유효한 변수만 필터링 (null이 아니고, 공백이 아닌 변수만)
                List<String> validVariables = requestDto.getVariableList().stream()
                        .filter(variableName -> variableName != null && !variableName.trim().isEmpty())
                        .toList();
                
                if (!validVariables.isEmpty()) {
                    for (String variableName : validVariables) {
                        Var variable = Var.builder()
                            .variableKey(variableName.trim()) // 앞뒤 공백 제거
                            .build();
                        template.addVariable(variable);
                    }
                }
            }

            // DB 저장
            Template savedTemplate = templateRepository.save(template);
            
            // 카테고리 사용량 증가
            incrementCategoryUsageCount(requestDto.getCategory());
            

            return TemplateSaveResponseDto.success(savedTemplate.getTemplateId().toString());
        } catch (Exception e) {
            log.error("템플릿 저장 중 오류 발생", e);
            return TemplateSaveResponseDto.failure("템플릿 저장 중 오류가 발생했습니다: "+e.getMessage());
        }
    }



    /**
     * 템플릿을 검증합니다.
     */
    @Transactional
    public TemplateValidationResponseDto validateTemplate(TemplateValidationRequestDto requestDto, UserDto currentUser) {
        try {

            // AI 서버로 검증 요청
            Map<String, Object> validationRequest = new HashMap<>();
            validationRequest.put("user_input", requestDto.getTemplateContent());
            validationRequest.put("variableList", requestDto.getVariableList());
            validationRequest.put("category", requestDto.getCategory());
            validationRequest.put("userMessage", requestDto.getUserMessage());
            validationRequest.put("templateTitle", requestDto.getTemplateTitle());
            if (requestDto.getTemplateId() != null) {
                validationRequest.put("templateId", requestDto.getTemplateId());
            }

            // AI 서버 검증 호출 (실제로는 AIService를 통해 호출)
            Map<String, Object> aiValidationResult = aiService.validateTemplateWithFastAPI(validationRequest);

            // 검증 성공 시에도 저장하지 않음 - 수정에서만 저장
            // boolean isValid = isValidationSuccessful(aiValidationResult);
            // if (isValid) {
            //     return handleApproval(requestDto, currentUser);
            // }

            RejectionDetails rejectionDetails = extractRejectionDetails(aiValidationResult);

            TemplateValidationResponseDto response = TemplateValidationResponseDto.rejectionWithDetails(
                    rejectionDetails.rejectedVariables,
                    rejectionDetails.alternatives,
                    rejectionDetails.validationErrors
            );
            response.setValidationStage(rejectionDetails.validationStage);
            
            // AI 서비스의 상세 검증 결과 전달
            Object validationResults = aiValidationResult.get("validation_results");
            if (validationResults instanceof List) {
                @SuppressWarnings("unchecked")
                List<Object> validationResultsList = (List<Object>) validationResults;
                response.setValidation_results(validationResultsList);
            }
            
            // problem_areas 정보를 validationErrors에 추가
            Object problemAreas = aiValidationResult.get("problem_areas");
            if (problemAreas instanceof List) {
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> problemAreasList = (List<Map<String, Object>>) problemAreas;
                List<TemplateValidationResponseDto.ValidationError> validationErrors = new ArrayList<>();
                
                for (Map<String, Object> problemArea : problemAreasList) {
                    String reason = (String) problemArea.getOrDefault("reason", "알 수 없는 오류");
                    String errorType = (String) problemArea.getOrDefault("error_type", "unknown");
                    // String severity = (String) problemArea.getOrDefault("severity", "error");
                    Integer startPosition = (Integer) problemArea.get("start_position");
                    Integer endPosition = (Integer) problemArea.get("end_position");
                    
                    TemplateValidationResponseDto.ValidationError validationError = 
                        new TemplateValidationResponseDto.ValidationError(
                            reason, reason, errorType, rejectionDetails.validationStage, startPosition, endPosition
                        );
                    validationErrors.add(validationError);
                }
                
                response.setValidationErrors(validationErrors);
            }
            
            return response;

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

    // 검증에서 저장 기능 제거됨 - 수정에서만 저장
    // private TemplateValidationResponseDto handleApproval(TemplateValidationRequestDto requestDto, UserDto currentUser) {
    //     // UserDto에서 가져온 accountId로 기존 Account 엔티티 참조
    //     Account account = accountRepository.findById(currentUser.getAccountId())
    //             .orElseThrow(() -> new ResourceNotFoundException("사용자를 찾을 수 없습니다: " + currentUser.getAccountId()));
    //
    //     Template template = Template.builder()
    //             .account(account)
    //             .templateContent(requestDto.getTemplateContent())
    //             .category(findCategoryByName(requestDto.getCategory()))
    //             .status("APPROVED")
    //             .build();
    //
    //     if (requestDto.getVariableList() != null && !requestDto.getVariableList().isEmpty()) {
    //         for (String variableKey : requestDto.getVariableList()) {
    //             Var variable = Var.builder()
    //                     .variableKey(variableKey)
    //                     .build();
    //             template.addVariable(variable);
    //         }
    //     }
    //
    //     Template savedTemplate = templateRepository.save(template);
    //     log.info("검증 성공, 템플릿 및 변수 저장 완료: {}", savedTemplate.getTemplateId());
    //     return TemplateValidationResponseDto.success(savedTemplate.getTemplateId().toString());
    // }

    private RejectionDetails extractRejectionDetails(Map<String, Object> aiValidationResult) {
        log.info("AI 검증 실패 응답 전체: {}", aiValidationResult);
        RejectionDetails details = new RejectionDetails();

        // 검증 단계 정보 추출
        String validationStage = extractValidationStage(aiValidationResult);
        details.validationStage = validationStage;
        log.info("추출된 검증 단계: {}", validationStage);

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
                    String stage = (String) result.getOrDefault("stage", validationStage);
                    @SuppressWarnings("unchecked")
                    List<String> errors = (List<String>) result.getOrDefault("errors", new ArrayList<>());
                    addErrorsFromDetailsVariable(result.get("details"), validatorName, errors, details, stage);
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

    /**
     * AI 응답에서 검증 단계 정보를 추출합니다.
     */
    private String extractValidationStage(Map<String, Object> aiValidationResult) {
        // validation_results에서 stage 정보 추출
        if (aiValidationResult.containsKey("validation_results")) {
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> validationResults = (List<Map<String, Object>>) aiValidationResult.get("validation_results");
            if (validationResults != null && !validationResults.isEmpty()) {
                for (Map<String, Object> result : validationResults) {
                    boolean resultIsValid = (Boolean) result.getOrDefault("is_valid", true);
                    if (!resultIsValid) {
                        String stage = (String) result.getOrDefault("stage", "unknown");
                        return convertStageToKorean(stage);
                    }
                }
            }
        }

        // 기본값 반환
        return "알 수 없음";
    }

    /**
     * 영어 단계명을 한국어로 변환합니다.
     */
    private String convertStageToKorean(String stage) {
        switch (stage.toLowerCase()) {
            case "constraint":
                return "1차 검증";
            case "semantic":
                return "2차 검증";
            case "final":
                return "최종 검증";
            default:
                return "알 수 없음";
        }
    }

    private void addErrorsFromDetailsVariable(Object detailsObject,
                                              String validatorName,
                                              List<String> errors,
                                              RejectionDetails aggregate) {
        addErrorsFromDetailsVariable(detailsObject, validatorName, errors, aggregate, null);
    }

    private void addErrorsFromDetailsVariable(Object detailsObject,
                                              String validatorName,
                                              List<String> errors,
                                              RejectionDetails aggregate,
                                              String validationStage) {
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
                            variableName, error, validatorName, validationStage
                    ));
                }
            }
        } else if (variables instanceof String) {
            String variableName = (String) variables;
            aggregate.rejectedVariables.add(variableName);
            for (String error : errors) {
                aggregate.validationErrors.add(new TemplateValidationResponseDto.ValidationError(
                        variableName, error, validatorName, validationStage
                ));
            }
        }
    }

    private static class RejectionDetails {
        private final List<String> rejectedVariables = new ArrayList<>();
        private final Map<String, List<String>> alternatives = new HashMap<>();
        private final List<TemplateValidationResponseDto.ValidationError> validationErrors = new ArrayList<>();
        private String validationStage; // 검증 단계 정보 추가
    }

    /**
     * 주어진 ID로 Category 엔티티를 조회합니다.
     * @param categoryId 조회할 Category의 ID
     * @return 조회된 Category 엔티티
     * @throws ResourceNotFoundException 해당 ID의 Category가 존재하지 않을 경우
     */
    @Transactional(readOnly = true)
    public Category findCategoryById(Long categoryId) {
        return categoryRepository.findById(categoryId)
                .orElseThrow(() -> new ResourceNotFoundException("Category not found with id: " + categoryId));
    }

    /**
     * 주어진 이름으로 Category 엔티티를 조회합니다.
     * 카테고리가 존재하지 않으면 자동으로 생성합니다.
     */
    @Transactional
    public Category findCategoryByName(String categoryName) {
        // 카테고리 이름 유효성 검사
        if (categoryName == null || categoryName.trim().isEmpty()) {
            throw new IllegalArgumentException("카테고리 이름이 비어있습니다.");
        }
        
        // 앞뒤 공백 제거하여 정규화
        String trimmedCategoryName = categoryName.trim();
        
        return categoryRepository.findByName(trimmedCategoryName)
                .orElseGet(() -> {
                    try {
                        log.info("새로운 카테고리 생성: {}", trimmedCategoryName);
                        Category newCategory = Category.builder()
                                .name(trimmedCategoryName)
                                .isActive(true)
                                .createdBy("AI")
                                .build();
                        Category savedCategory = categoryRepository.save(newCategory);
                        log.info("새로운 카테고리 생성 완료: {} (ID: {})", trimmedCategoryName, savedCategory.getId());
                        return savedCategory;
                    } catch (Exception e) {
                        log.error("새로운 카테고리 생성 실패: {}", trimmedCategoryName, e);
                        throw new RuntimeException("카테고리 생성 중 오류가 발생했습니다: " + e.getMessage(), e);
                    }
                });
    }

    /**
     * 카테고리 사용량을 증가시킵니다.
     */
    @Transactional
    public void incrementCategoryUsageCount(String categoryName) {
        try {
            Category category = findCategoryByName(categoryName);
            category.setUsageCount(category.getUsageCount() + 1);
            categoryRepository.save(category);
            log.info("카테고리 사용량 증가: {} (현재 사용량: {})", categoryName, category.getUsageCount());
        } catch (Exception e) {
            log.error("카테고리 사용량 증가 실패: {}", categoryName, e);
        }
    }

    /**
     * AI를 활용하여 템플릿을 수정합니다.
     */
    public FastAPIResponseDto modifyTemplateWithAi(TemplateRequestDto requestDto) {
        log.info("AI 템플릿 수정 요청을 AI 서버로 전달합니다. 현재 템플릿: {}, 사용자 메시지: {}", 
                requestDto.getTemplateContent() != null ? requestDto.getTemplateContent().substring(0, Math.min(50, requestDto.getTemplateContent().length())) : "null", 
                requestDto.getUserMessage());
        
        // AI 서버에 템플릿 수정을 요청하고, 받은 응답을 그대로 반환합니다.
        return aiService.modifyTemplateWithFastAPI(requestDto);
    }
}