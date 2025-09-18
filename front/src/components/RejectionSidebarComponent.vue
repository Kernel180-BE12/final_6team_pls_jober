<template>
  <div v-if="show" class="rejection-sidebar">
    <div class="sidebar-header">
      <h3>반려 사유 및 대안</h3>
      <div v-if="validationStage" class="validation-stage">
        <span class="stage-badge">{{ validationStage }}</span>
      </div>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>
    
    <!-- 반려 사유 -->
    <div class="rejection-reason" v-if="currentVariable">
      <h4>• 반려 사유</h4>
      <div v-if="validationErrors" class="error-details">
        <div class="rule-info">
          <p><strong>위반 규칙:</strong> {{ validationErrors.rule || '알 수 없는 규칙' }}</p>
          <p><strong>규칙 유형:</strong> {{ getRuleTypeDisplay(validationErrors.errorType) }}</p>
          <p v-if="validationErrors.validationStage"><strong>검증 단계:</strong> {{ validationErrors.validationStage }}</p>
          <p><strong>심각도:</strong> 
            <span :class="getSeverityClass(validationErrors.severity)">
              {{ getSeverityDisplay(validationErrors.severity) }}
            </span>
          </p>
        </div>
        <div class="error-message">
          <p><strong>상세 사유:</strong></p>
          <p class="reason-text">{{ validationErrors.errorMessage }}</p>
        </div>
        <div class="suggestion-box" v-if="validationErrors.suggestion">
          <p><strong>개선 방안:</strong></p>
          <p class="suggestion-text">{{ validationErrors.suggestion }}</p>
        </div>
        <p class="variable-instruction">변수 "<strong>{{ currentVariable }}</strong>"에 대한 대안을 선택하세요.</p>
      </div>
      <div v-else>
        <p>변수 "<strong>{{ currentVariable }}</strong>"에 대한 대안을 선택하세요.</p>
      </div>
    </div>
    
    <!-- 대안 목록 -->
    <div class="alternatives-section" v-if="currentVariable">
      <h4>대안 선택</h4>
      <div class="alternatives-list">
        <div 
          v-for="(alt, index) in currentAlternatives" 
          :key="index"
          :class="['alternative-item', { 'selected': alt.selected }]"
          @click="selectAlternative(alt)"
        >
          <div class="alternative-content">
            <p>{{ alt.text }}</p>
          </div>
          <div class="alternative-status">
            <span v-if="alt.selected" class="selected-mark">✓</span>
          </div>
        </div>
      </div>
      
      <div class="alternatives-actions">
        <button class="btn-apply" @click="applySelectedAlternative">
          선택한 대안 적용하기
        </button>
      </div>
    </div>
    
    <!-- 반려된 모든 항목 요약 -->
    <div class="rejected-summary" v-if="!currentVariable">
      <h4>반려 사유 목록</h4>
      
      <!-- 변수 관련 반려 항목 -->
      <div v-if="rejectedVariables.length > 0" class="rejected-variables-section">
        <h5>• 반려된 변수들</h5>
        <div class="rejected-items">
          <div 
            v-for="variable in rejectedVariables" 
            :key="variable"
            class="rejected-item variable-item"
            @click="$emit('variableClick', variable)"
          >
            <div class="variable-info">
              <span class="variable-name">{{ variable }}</span>
              <span class="click-hint">클릭하여 상세 확인</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 전체 반려 사유 목록 -->
      <div v-if="getAllValidationErrors().length > 0" class="all-errors-section">
        <h5>• 모든 반려 사유</h5>
        <div class="error-list">
          <div 
            v-for="(error, index) in getAllValidationErrors()" 
            :key="index"
            class="error-item"
            :class="getSeverityClass(error.severity)"
          >
            <div class="error-header">
              <span class="rule-type-badge">{{ getRuleTypeDisplay(error.rule_type) }}</span>
              <span class="severity-badge" :class="getSeverityClass(error.severity)">
                {{ getSeverityDisplay(error.severity) }}
              </span>
            </div>
            <div class="error-content">
              <p class="error-reason">{{ error.reason }}</p>
              <p v-if="error.suggestion" class="error-suggestion">💡 {{ error.suggestion }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Alternative {
  text: string
  selected: boolean
}

interface ValidationError {
  variableName?: string
  errorMessage: string
  errorType: string
  validationStage?: string
  rule?: string
  suggestion?: string
  severity?: string
}

interface DetailedValidationError {
  rule_type: string
  rule: string
  reason: string
  suggestion: string
  severity: string
  variable_name?: string
  stage: string
}

interface RejectionSidebarProps {
  show: boolean
  currentVariable: string
  alternatives: Alternative[]
  rejectedVariables: string[]
  validationErrors?: ValidationError | DetailedValidationError[] | null
  validationStage?: string
}

const props = defineProps<RejectionSidebarProps>()
const emit = defineEmits<{
  close: []
  variableClick: [variableName: string]
  applyAlternative: [alternative: Alternative]
}>()

const currentAlternatives = ref<Alternative[]>([])

watch(() => props.alternatives, (newAlternatives) => {
  currentAlternatives.value = JSON.parse(JSON.stringify(newAlternatives))
}, { immediate: true })

// 대안 선택
const selectAlternative = (alternative: Alternative) => {
  // 다른 대안들의 선택 해제
  currentAlternatives.value.forEach(alt => {
    if (alt !== alternative) {
      alt.selected = false
    }
  })
  // 현재 대안 선택/해제
  alternative.selected = !alternative.selected
}

// 선택한 대안 적용
const applySelectedAlternative = () => {
  const selectedAlternative = currentAlternatives.value.find(alt => alt.selected)
  if (selectedAlternative) {
    emit('applyAlternative', selectedAlternative)
  }
}

// 규칙 유형 표시명 변환
const getRuleTypeDisplay = (ruleType: string) => {
  const typeMap: Record<string, string> = {
    'informational_message': '정보성 메시지 요건',
    'standardized_template': '정형화된 템플릿 요건',
    'variable_count': '변수 개수 제한',
    'variable_example': '변수 예시값',
    'variable_structure': '변수 구조',
    'template_writing': '템플릿 작성 규칙'
  }
  return typeMap[ruleType] || ruleType
}

// 심각도 표시명 변환
const getSeverityDisplay = (severity: string) => {
  const severityMap: Record<string, string> = {
    'error': '오류',
    'warning': '경고'
  }
  return severityMap[severity] || severity
}

// 심각도 CSS 클래스
const getSeverityClass = (severity: string) => {
  return severity === 'error' ? 'severity-error' : 'severity-warning'
}

// 모든 검증 오류 가져오기
const getAllValidationErrors = () => {
  if (!props.validationErrors) return []
  
  // TemplateResultView에서 전달된 상세한 검증 오류 배열
  if (Array.isArray(props.validationErrors)) {
    return props.validationErrors as DetailedValidationError[]
  }
  
  // 기존 형식의 단일 오류 객체
  const singleError = props.validationErrors as ValidationError
  return [{
    rule_type: singleError.errorType || 'unknown',
    rule: singleError.rule || '알 수 없는 규칙',
    reason: singleError.errorMessage || '알 수 없는 오류',
    suggestion: singleError.suggestion || '수정이 필요합니다',
    severity: singleError.severity || 'error',
    variable_name: singleError.variableName,
    stage: singleError.validationStage || '1차 검증'
  }] as DetailedValidationError[]
}
</script>

<style scoped>
.rejection-sidebar {
  width: 20rem;
  min-width: 20rem;
  max-width: 20rem;
  height: auto;
  max-height: 80vh; /* 카카오 미리보기와 동일한 최대 높이 */
  background: white;
  border-radius: 0.6rem;
  padding: 1rem;
  box-shadow: 0 0.1rem 0.4rem rgba(0, 0, 0, 0.1);
  border: 0.05rem solid #e0e0e0;
  overflow-y: auto;
  align-self: flex-start; /* 상단 정렬로 변경 */
  flex-shrink: 0;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
  padding-bottom: 0.6rem;
  border-bottom: 0.1rem solid #e0e0e0;
}

.validation-stage {
  margin-left: auto;
  margin-right: 0.5rem;
}

.stage-badge {
  background: #ff6b6b;
  color: white;
  padding: 0.2rem 0.6rem;
  border-radius: 0.3rem;
  font-size: 0.7rem;
  font-weight: bold;
  text-transform: uppercase;
}

.sidebar-header h3 {
  margin: 0;
  color: #1a1a1a;
  font-size: 1.1rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.close-btn:hover {
  background: #f5f5f5;
}

.rejection-reason {
  margin-bottom: 0.8rem;
  padding: 0.6rem;
  background: #fff3e0;
  border-radius: 0.4rem;
  border-left: 0.2rem solid #ff9800;
}

.rejection-reason h4 {
  margin: 0 0 0.3rem 0;
  color: #e65100;
  font-size: 0.9rem;
}

.rejection-reason p {
  margin: 0;
  color: #795548;
  font-size: 0.8rem;
}

.error-details {
  margin-top: 0.4rem;
}

.error-details p {
  margin: 0.2rem 0;
  font-size: 0.8rem;
}

.rule-info {
  background: #f8f9fa;
  padding: 0.6rem;
  border-radius: 0.3rem;
  margin-bottom: 0.6rem;
  border-left: 0.2rem solid #6c757d;
}

.error-message {
  margin-bottom: 0.6rem;
}

.reason-text {
  background: #fff3e0;
  padding: 0.4rem;
  border-radius: 0.3rem;
  color: #e65100;
  font-weight: 500;
  margin-top: 0.2rem;
}

.suggestion-box {
  background: #e8f5e8;
  padding: 0.6rem;
  border-radius: 0.3rem;
  border-left: 0.2rem solid #4caf50;
  margin-bottom: 0.6rem;
}

.suggestion-text {
  color: #2e7d32;
  font-weight: 500;
  margin-top: 0.2rem;
}

.variable-instruction {
  margin-top: 0.6rem;
  font-weight: 500;
  color: #1976d2;
}

.severity-error {
  color: #d32f2f;
  font-weight: bold;
  background: #ffebee;
  padding: 0.1rem 0.4rem;
  border-radius: 0.2rem;
}

.severity-warning {
  color: #f57c00;
  font-weight: bold;
  background: #fff3e0;
  padding: 0.1rem 0.4rem;
  border-radius: 0.2rem;
}

.alternatives-section {
  margin-bottom: 0.8rem;
}

.alternatives-section h4 {
  margin: 0 0 0.6rem 0;
  color: #333;
  font-size: 0.9rem;
}

.alternatives-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-bottom: 0.8rem;
}

.alternative-item {
  padding: 0.5rem;
  border: 0.1rem solid #e0e0e0;
  border-radius: 0.4rem;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.alternative-item:hover {
  border-color: #1976d2;
  background: #f8f9fa;
}

.alternative-item.selected {
  border-color: #4caf50;
  background: #e8f5e8;
}

.alternative-content p {
  margin: 0;
  color: #333;
  font-size: 0.95rem;
}

.alternative-status {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
}

.selected-mark {
  color: #4caf50;
  font-weight: bold;
  font-size: 1.2rem;
}

.alternatives-actions {
  padding-top: 0.6rem;
  border-top: 0.05rem solid #e0e0e0;
}

.btn-apply {
  width: 100%;
  background: #1976d2;
  color: white;
  border: none;
  padding: 0.6rem;
  border-radius: 0.3rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-apply:hover {
  background: #1565c0;
}

.btn-apply:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.rejected-summary {
  margin-top: 0.8rem;
}

.rejected-summary h4 {
  margin: 0 0 0.6rem 0;
  color: #333;
  font-size: 1rem;
  font-weight: 600;
}

.rejected-summary h5 {
  margin: 0.8rem 0 0.4rem 0;
  color: #555;
  font-size: 0.9rem;
  font-weight: 500;
}

.rejected-variables-section {
  margin-bottom: 1rem;
}

.all-errors-section {
  margin-bottom: 0.8rem;
}

.error-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.error-item {
  padding: 0.6rem;
  border-radius: 0.4rem;
  border: 0.1rem solid #e0e0e0;
  background: #fafafa;
}

.error-item.severity-error {
  border-color: #ffcdd2;
  background: #ffeaee;
}

.error-item.severity-warning {
  border-color: #ffe0b2;
  background: #fff8e1;
}

.error-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.4rem;
}

.rule-type-badge {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.2rem 0.5rem;
  border-radius: 0.3rem;
  font-size: 0.7rem;
  font-weight: 600;
}

.severity-badge {
  font-size: 0.7rem;
  font-weight: bold;
  padding: 0.1rem 0.4rem;
  border-radius: 0.2rem;
}

.error-content {
  margin-top: 0.4rem;
}

.error-reason {
  margin: 0 0 0.3rem 0;
  font-size: 0.85rem;
  color: #333;
  font-weight: 500;
}

.error-suggestion {
  margin: 0;
  font-size: 0.8rem;
  color: #4caf50;
  font-style: italic;
}

.rejected-items {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.rejected-item {
  padding: 0.5rem;
  border: 0.1rem solid #ffebee;
  border-radius: 0.4rem;
  background: #fff5f5;
  cursor: pointer;
  transition: all 0.2s ease;
}

.variable-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.rejected-item:hover {
  border-color: #f44336;
  background: #ffebee;
}

.variable-name {
  font-weight: 500;
  color: #c62828;
}

.click-hint {
  font-size: 0.8rem;
  color: #666;
  font-style: italic;
}
</style>
