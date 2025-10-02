<template>
  <div v-if="show" class="rejection-sidebar" style="height: 30rem;">
    <div class="sidebar-header">
      <button v-if="showingAlternatives" class="back-btn" @click="goBack">←</button>
      <h3>{{ showingAlternatives ? '수정이 필요한 내용' : '반려 사유 및 대안' }}</h3>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>
    
    <!-- 대안 선택 화면 -->
    <div class="alternatives-selection" v-if="showingAlternatives && selectedError">
      <div class="error-detail">
        <div class="error-description">
          <p class="error-reason">{{ selectedError.reason }}</p>
        </div>
      </div>
      
      <h4>대안 선택 ({{ currentAlternatives.length }}개)</h4>
      <div class="alternatives-list">
        <!-- 대안이 있을 때 -->
        <div 
          v-for="(alternative, index) in currentAlternatives" 
          :key="index"
          :class="['alternative-item', { 'selected': alternative.selected }]"
          @click="selectAlternative(alternative)"
        >
          <div class="alternative-content">
            <div class="alternative-text">
              <p v-html="formatProblemText(alternative.text)"></p>
            </div>
            <div v-if="alternative.preview" class="alternative-preview">
              <div class="preview-label">미리보기:</div>
              <div class="preview-content" v-html="formatProblemText(alternative.preview)"></div>
            </div>
          </div>
          <div class="alternative-status">
            <span v-if="alternative.selected" class="selected-mark">✓</span>
          </div>
        </div>
        
        <!-- 대안이 없을 때 -->
        <div v-if="currentAlternatives.length === 0" class="no-alternatives-message">
          <div class="no-alternatives-icon">⚠️</div>
          <p>대안을 찾을 수 없습니다.</p>
          <p class="no-alternatives-hint">수동으로 템플릿을 수정해주세요.</p>
        </div>
      </div>
      
      <div class="alternatives-actions">
        <button 
          class="btn-apply" 
          @click="applySelectedAlternative"
          :disabled="!hasSelectedAlternative"
        >
          선택한 대안 적용하기
        </button>
      </div>
    </div>

    <!-- 문제 영역 목록 (기본 화면) -->
    <div class="problem-areas-summary" v-if="!showingAlternatives">
      <div class="summary-stats">
        <span class="error-count">❌ 오류 {{ totalErrors }}개</span>
        <span class="warning-count">⚠️ 경고 {{ totalWarnings }}개</span>
      </div>
      
      <!-- 문제 영역 목록 -->
      <div class="problem-areas-section">
        <div class="problem-area-list">
          <div 
            v-for="(area, index) in problemAreas" 
            :key="area.area_id"
            class="problem-area-item clickable-area"
            :class="getSeverityClass(area.severity)"
            @click="showAlternativesForProblemArea(area)"
          >
            <div class="area-header">
              <span class="area-type-badge">{{ getAreaTypeDisplay(area.area_type) }}</span>
              <span class="severity-badge" :class="getSeverityClass(area.severity)">
                {{ getSeverityDisplay(area.severity) }}
              </span>
            </div>
            <div class="area-content">
              <p class="area-location">📍 {{ area.location }}</p>
              <p class="area-problem-text" v-html="formatProblemText(area.problem_text)"></p>
              <p class="click-hint">클릭하여 대안 확인 →</p>
            </div>
          </div>
          
          <!-- 문제 영역이 없을 때 표시할 메시지 -->
          <div v-if="problemAreas.length === 0" class="no-problems-message">
            <p>현재 발견된 문제 영역이 없습니다.</p>
            <p>검증 결과를 다시 확인해주세요.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'

interface Alternative {
  text: string
  selected: boolean
  preview?: string // 수정 결과 미리보기
  validationGuaranteed?: boolean // LLM 생성 대안은 검증 규칙 준수
}

interface ProblemArea {
  area_id: string
  area_type: string
  location: string
  problem_text: string
  error_type: string
  severity: string
  reason: string
  suggestion: string
  alternatives: string[]
}

interface RejectionSidebarProps {
  show: boolean
  currentProblemArea: ProblemArea | null
  alternatives: Alternative[]
  problemAreas: ProblemArea[]
  totalErrors: number
  totalWarnings: number
}

const props = defineProps<RejectionSidebarProps>()
const emit = defineEmits<{
  close: []
  problemAreaClick: [problemArea: ProblemArea]
  applyAlternative: [alternative: Alternative, problemArea: ProblemArea]
}>()


const currentAlternatives = ref<Alternative[]>([])
const showingAlternatives = ref(false)
const selectedError = ref<ProblemArea | null>(null)

watch(() => props.alternatives, (newAlternatives) => {
  currentAlternatives.value = JSON.parse(JSON.stringify(newAlternatives))
}, { immediate: true })

// 대안 선택
const selectAlternative = (alternative: Alternative) => {
  console.log('대안 클릭됨:', alternative.text, '현재 선택 상태:', alternative.selected)
  
  // 다른 대안들의 선택 해제
  currentAlternatives.value.forEach(alt => {
    if (alt !== alternative) {
      alt.selected = false
    }
  })
  // 현재 대안 선택 (토글하지 않고 항상 선택)
  alternative.selected = true
  
  console.log('선택 후 상태:', currentAlternatives.value.map(alt => ({ text: alt.text, selected: alt.selected })))
}

// 선택한 대안 적용
const applySelectedAlternative = () => {
  console.log('=== 대안 적용 버튼 클릭 ===')
  console.log('현재 대안들:', currentAlternatives.value)
  console.log('선택된 오류:', selectedError.value)
  console.log('hasSelectedAlternative 값:', hasSelectedAlternative.value)
  
  const selectedAlternative = currentAlternatives.value.find(alt => alt.selected)
  console.log('선택된 대안:', selectedAlternative)
  
  if (selectedAlternative && selectedError.value) {
    console.log('이벤트 emit 시작')
    // LLM 생성 대안인 경우 검증 규칙 준수 정보 추가
    const alternativeWithGuarantee = {
      ...selectedAlternative,
      validationGuaranteed: selectedAlternative.validationGuaranteed || false,
      problemAreaId: selectedError.value.area_id,
      appliedAt: new Date().toISOString()
    }
    
    console.log('emit할 데이터:', alternativeWithGuarantee, selectedError.value)
    emit('applyAlternative', alternativeWithGuarantee, selectedError.value)
    console.log('이벤트 emit 완료')
    // 적용 후 메인 화면으로 돌아가기
    goBack()
  } else {
    console.log('선택된 대안이 없거나 오류 정보가 없음')
  }
}

// 선택된 대안이 있는지 확인
const hasSelectedAlternative = computed(() => {
  const hasSelected = currentAlternatives.value.some(alt => alt.selected)
  console.log('hasSelectedAlternative 계산:', hasSelected, '대안들:', currentAlternatives.value.map(alt => ({ text: alt.text, selected: alt.selected })))
  return hasSelected
})

// 뒤로가기
const goBack = () => {
  showingAlternatives.value = false
  selectedError.value = null
  currentAlternatives.value = []
}

// 문제 영역에 대한 대안 표시
const showAlternativesForProblemArea = (area: ProblemArea) => {
  selectedError.value = area
  showingAlternatives.value = true
  
  // 문제 영역 클릭 이벤트 발생 - 부모 컴포넌트에서 하이라이트 처리
  emit('problemAreaClick', area)
  
  // 백엔드에서 받은 LLM 생성 대안 사용
  if (area.alternatives && area.alternatives.length > 0) {
    currentAlternatives.value = area.alternatives.map((alt: string) => {
      // 대안 텍스트를 그대로 사용 (백엔드에서 구체적인 대안 제공)
      return {
        text: alt,
        selected: false
      }
    })
  } else {
    // 백엔드에서 대안이 없는 경우에만 기본 메시지
    currentAlternatives.value = [{
      text: '대안이 생성되지 않았습니다. 수동으로 수정해주세요.',
      selected: false
    }]
  }
}

// 하드코딩된 대안 생성 함수들은 제거 - 백엔드 LLM이 생성한 대안 사용

// 영역 타입 표시명 변환
const getAreaTypeDisplay = (areaType: string) => {
  const typeMap: Record<string, string> = {
    'specific_text': '특정 문구',
    'paragraph': '문단',
    'entire_template': '전체 템플릿'
  }
  return typeMap[areaType] || areaType
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

// 문제 텍스트를 사용자 친화적으로 포맷팅
const formatProblemText = (text: string) => {
  if (!text) return ''
  
  // #{변수명} 형식을 {변수명}으로 변환
  let formattedText = text
    .replace(/#\{([^}]+)\}/g, '<span class="variable-display">{$1}</span>')
    .replace(/\{\{([^}]+)\}\}/g, '<span class="variable-display">{$1}</span>')
    .replace(/\[([^\]]+)\]/g, '<span class="variable-display">{$1}</span>')
  
  return formattedText
}

</script>

<style scoped>
.rejection-sidebar {
  width: 20rem;
  min-width: 20rem;
  max-width: 20rem;
  background: white;
  border-radius: 0.6rem;
  padding: 1rem;
  box-shadow: 0 0.1rem 0.4rem rgba(0, 0, 0, 0.1);
  border: 0.05rem solid #e0e0e0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  height: 30rem; /* 고정 높이 */
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.2rem;
  border-bottom: 0.1rem solid #e0e0e0;
  flex-shrink: 0; /* 헤더 고정 */
}



.sidebar-header h3 {
  margin: 0;
  color: #1a1a1a;
  font-size: 1rem;
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

.back-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #666;
  padding: 0.2rem 0.4rem;
  margin-right: 0.5rem;
  border-radius: 0.3rem;
  transition: background-color 0.2s ease;
}

.back-btn:hover {
  background: #f5f5f5;
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


.alternatives-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-bottom: 0.8rem;
  flex: 1;
  overflow-y: auto;
  padding-right: 0.3rem;
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

.alternative-content {
  flex: 1;
}

.alternative-text p {
  margin: 0;
  color: #333;
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1.4;
  word-wrap: break-word;
}

.alternative-preview {
  margin-top: 0.5rem;
  padding: 0.4rem;
  background: #f8f9fa;
  border-radius: 0.3rem;
  border-left: 0.2rem solid #4caf50;
}

.preview-label {
  font-size: 0.8rem;
  color: #666;
  font-weight: 600;
  margin-bottom: 0.3rem;
}

.preview-content {
  font-size: 0.85rem;
  color: #333;
  line-height: 1.4;
  font-style: italic;
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
  flex-shrink: 0;
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

.problem-areas-summary {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0; /* flex item이 내용에 맞춰 축소되도록 */
}

.problem-areas-summary h4 {
  margin: 0 0 0.2rem 0;
  color: #333;
  font-size: 1rem;
  font-weight: 600;
  flex-shrink: 0;
}

.summary-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 0.6rem;
  background: #f8f9fa;
  border-radius: 0.4rem;
  flex-shrink: 0;
}

.error-count {
  color: #d32f2f;
  font-weight: 600;
  font-size: 0.9rem;
}

.warning-count {
  color: #f57c00;
  font-weight: 600;
  font-size: 0.9rem;
}

/* 사용되지 않는 rejected 관련 CSS 제거 */

.problem-areas-section {
  margin-bottom: 0.8rem;
  flex: 1;
  overflow-y: auto;
  padding-right: 0.3rem;
}

.problem-area-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.problem-area-item {
  padding: 0.6rem;
  border-radius: 0.4rem;
  border: 0.1rem solid #e0e0e0;
  background: #fafafa;
}

.problem-area-item.severity-error {
  border-color: #ffcdd2;
  background: #ffeaee;
}

.problem-area-item.severity-warning {
  border-color: #ffe0b2;
  background: #fff8e1;
}

.area-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.4rem;
}

.area-type-badge {
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

.area-content {
  margin-top: 0.4rem;
}

.area-location {
  margin: 0 0 0.3rem 0;
  font-size: 0.8rem;
  color: #666;
  font-weight: 500;
}

.area-problem-text {
  margin: 0 0 0.3rem 0;
  font-size: 0.85rem;
  color: #333;
  font-weight: 600;
  background: #f5f5f5;
  padding: 0.3rem;
  border-radius: 0.2rem;
  border-left: 0.2rem solid #1976d2;
}



.error-reason {
  margin: 0 0 0.3rem 0;
  font-size: 0.85rem;
  color: #333;
  font-weight: 500;
}



.click-hint {
  font-size: 0.8rem;
  color: #666;
  font-style: italic;
  margin-top: 0.3rem;
}

/* 변수 표시 스타일 */
:deep(.variable-display) {
  color: #6b7280;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 0.85em;
  font-weight: 500;
  display: inline-block;
  margin: 0 1px;
}

.clickable-area {
  cursor: pointer;
  transition: all 0.2s ease;
}

.clickable-area:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}


.alternatives-selection {
  margin-top: 0.8rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0; /* flex item이 내용에 맞춰 축소되도록 */
}

.error-detail {
  margin-bottom: 0.6rem;
  padding: 0.6rem;
  background: #fff3e0;
  border-radius: 0.4rem;
  border-left: 0.3rem solid #ff9800;
  flex-shrink: 0;
}

.error-detail h4 {
  margin: 0 0 0.5rem 0;
  color: #e65100;
  font-size: 0.9rem;
}

.error-description {
  margin-top: 0;
}

.error-description .error-reason {
  padding: 0.5rem;
  margin-bottom: 0.3rem;
  font-weight: 500;
}

.error-description .error-suggestion {
  color: #4caf50;
  font-size: 0.85rem;
  font-weight: 500;
}

.no-problems-message {
  text-align: center;
  padding: 2rem 1rem;
  color: #666;
  background: #f8f9fa;
  border-radius: 0.4rem;
  border: 0.1rem dashed #ddd;
}

.no-problems-message p {
  margin: 0.5rem 0;
  font-size: 0.9rem;
}

/* 스크롤바 스타일 */
.alternatives-list::-webkit-scrollbar,
.problem-areas-section::-webkit-scrollbar {
  width: 0.3rem;
}

.alternatives-list::-webkit-scrollbar-track,
.problem-areas-section::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 0.15rem;
}

.alternatives-list::-webkit-scrollbar-thumb,
.problem-areas-section::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 0.15rem;
}

.alternatives-list::-webkit-scrollbar-thumb:hover,
.problem-areas-section::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
