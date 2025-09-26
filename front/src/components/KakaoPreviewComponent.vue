<template>
  <div class="kakao-preview-container">
    <!-- 알림톡 미리보기 -->
    <div class="kakao-preview">
      <div class="kakao-content">
        <div class="message-bubble">
          <div class="kakao-header">
            <span class="kakao-header-text">알림톡 도착</span>
          </div>
          <div class="bubble-body">
            <div
              class="message-text"
              :class="{ 'expanded': isExpanded }"
              v-html="formattedTemplateContent"
            ></div>
          </div>
          <div
            v-if="shouldShowToggle"
            class="toggle-button"
            @click="toggleExpansion"
          >
            <span class="toggle-icon" :class="{ expanded: isExpanded }">▶</span>
            <span class="toggle-text">{{ isExpanded ? '접기' : '자세히 보기' }}</span>
          </div>
        </div>
      </div>
    </div>
    <!-- 하단 컨트롤은 TemplateResultView에서 처리됨 -->
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'

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

interface KakaoPreviewProps {
  templateContent?: string
  showVariables: boolean
  variables: string[]
  isRejected: boolean
  problemAreas: ProblemArea[]
  highlightedProblemArea?: ProblemArea | null
  modifiedAreas?: string[]
}

const props = defineProps<KakaoPreviewProps>()
const emit = defineEmits<{
  problemAreaClick: [problemArea: ProblemArea]
  rejectTemplate: []
  submitTemplate: []
  updateVariables: [variables: string[]]
}>()

const editedVariables = ref({ ...props.variables })
const isExpanded = ref(false)
const shouldShowToggle = ref(false)

// 템플릿 내용을 포맷팅하여 변수를 적절한 스타일로 렌더링
const formattedTemplateContent = computed(() => {
  // 1) 기본 템플릿
  if (!props.templateContent) {
    const defaultContent = `
안녕하세요, #{고객명}님.

#{서비스명} 이용과 관련하여 안내드립니다.

• 처리일시: #{처리일시}
• 처리상태: #{처리상태}
• 담당자: #{담당자명}

문의사항이 있으신 경우 고객센터로 연락 부탁드립니다.

감사합니다.
`

    // 내용 길이 체크 및 토글 설정 (줄 수 기준)
    const lines = defaultContent.split('\n').filter(line => line.trim())
    shouldShowToggle.value = lines.length > 6

    return formatTemplateContent(defaultContent.trim())
  }

  // 2) 텍스트 정리 및 마커 제거 (미리보기에서는 마커를 보이지 않음)
  let content = props.templateContent ?? ''
  
  
  // 더 정확한 텍스트 정리
  content = content
    .replace(/(변수\s*목록\s*:|변수\s*:).*$/s, '')      // 변수 목록 제거
    .replace(/알림톡\s*템플릿은.*$/s, '')               // 설명 문구 제거
    .replace(/\n\s*\n\s*\n/g, '\n\n')                   // 빈 줄 정리
    // 마커 제거 (⟦ID⟧내용⟦/ID⟧ → 내용)
    .replace(/⟦([^⟦]+)⟧([^⟦]*)⟦\/\1⟧/g, '$2')
    // 고객에게 보이면 안 되는 내부 메시지 제거
    .replace(/할인율[:\s]*~[^.]*\./g, '')              // 할인율 관련 내부 메시지
    .replace(/할인율[:\s]*고객이[^.]*\./g, '')         // 할인율 관련 내부 메시지
    .replace(/할인율[:\s]*고객들에게[^.]*\./g, '')     // 할인율 관련 내부 메시지
    .replace(/할인율[:\s]*보이면[^.]*\./g, '')         // 할인율 관련 내부 메시지
    .replace(/할인율[:\s]*안되는[^.]*\./g, '')         // 할인율 관련 내부 메시지
    .replace(/할인율[:\s]*메시지가[^.]*\./g, '')       // 할인율 관련 내부 메시지
    .replace(/할인율[:\s]*구체적인[^.]*\./g, '')       // 할인율 관련 내부 메시지
    .replace(/할인율[:\s]*언급하지[^.]*\./g, '')       // 할인율 관련 내부 메시지
    .replace(/할인율[:\s]*강조하되[^.]*\./g, '')       // 할인율 관련 내부 메시지
    .replace(/할인율[:\s]*참여할[^.]*\./g, '')         // 할인율 관련 내부 메시지
    .replace(/할인율[:\s]*방법이나[^.]*\./g, '')       // 할인율 관련 내부 메시지
    .replace(/할인율[:\s]*혜택을[^.]*\./g, '')         // 할인율 관련 내부 메시지
    .replace(/고객이[^.]*\./g, '')                     // 기타 내부 지시사항
    .replace(/고객들에게[^.]*\./g, '')                 // 기타 내부 지시사항
    .replace(/보이면[^.]*\./g, '')                     // 기타 내부 지시사항
    .replace(/안되는[^.]*\./g, '')                     // 기타 내부 지시사항
    .replace(/메시지가[^.]*\./g, '')                   // 기타 내부 지시사항
    .replace(/구체적인[^.]*\./g, '')                   // 기타 내부 지시사항
    .replace(/언급하지[^.]*\./g, '')                   // 기타 내부 지시사항
    .replace(/강조하되[^.]*\./g, '')                   // 기타 내부 지시사항
    .replace(/참여할[^.]*\./g, '')                     // 기타 내부 지시사항
    .replace(/방법이나[^.]*\./g, '')                   // 기타 내부 지시사항
    .replace(/혜택을[^.]*\./g, '')                     // 기타 내부 지시사항
    .replace(/이\s*내용이[^.]*\./g, '')                // 기술적 설명
    .replace(/이\s*부분이[^.]*\./g, '')                // 기술적 설명
    .replace(/이\s*텍스트가[^.]*\./g, '')              // 기술적 설명
    .replace(/이\s*문장이[^.]*\./g, '')                // 기술적 설명
    .replace(/미리보기에[^.]*\./g, '')                 // 기술적 설명
    .replace(/사용자가\s*보는건[^.]*\./g, '')          // 기술적 설명
    .replace(/사용자에게\s*보이는[^.]*\./g, '')        // 기술적 설명
    .replace(/화면에\s*표시되는[^.]*\./g, '')          // 기술적 설명
    .replace(/잘하자\s*/g, '')                         // 작업 지시사항
    .replace(/주의하자\s*/g, '')                       // 작업 지시사항
    .replace(/기억하자\s*/g, '')                       // 작업 지시사항
    .replace(/명심하자\s*/g, '')                       // 작업 지시사항
    .replace(/주의\s*/g, '')                           // 작업 지시사항
    .replace(/기억\s*/g, '')                           // 작업 지시사항
    .replace(/명심\s*/g, '')                           // 작업 지시사항
    .replace(/\s+/g, ' ')                              // 연속된 공백 정리
    .replace(/\n\s*\n/g, '\n')                         // 연속된 줄바꿈 정리
    .trim()
  

  // 내용 길이 체크 (줄 수 기준)
  const lines = content.split('\n').filter(line => line.trim())
  shouldShowToggle.value = lines.length > 6

  // 3) 변수를 항상 회색으로 처리
  const varPatterns = [
    /\{\{([^}]+)\}\}/g,  // {{변수}}
    /#\{([^}]+)\}/g,      // #{변수}
    /\{([^}]+)\}/g,       // {변수}
    /\[([^\]]+)\]/g       // [변수] - 대괄호 형태도 변수로 처리
  ]

  varPatterns.forEach(pattern => {
    content = content.replace(pattern, (match, varName) => {
      const variableName = varName.trim()
      return `<span class="variable-gray" data-variable="${variableName}">#{${variableName}}</span>`
    })
  })

  // 4) 스마트 포맷팅 - 의미 있는 구조로 변환
  content = formatTemplateContent(content)


  // 특정 문제 영역 하이라이트
  if (props.highlightedProblemArea) {
    content = highlightProblemArea(content, props.highlightedProblemArea)
  }

  // 수정된 영역 하이라이트
  if (props.modifiedAreas && props.modifiedAreas.length > 0) {
    content = highlightModifiedAreas(content, props.modifiedAreas)
  }

  return content
})

// 문제 영역 하이라이트 함수 (개선된 버전)
const highlightProblemArea = (content: string, problemArea: ProblemArea): string => {
  if (!problemArea.problem_text) return content
  
  
  // 문제 텍스트를 찾아서 하이라이트
  const problemText = problemArea.problem_text.trim()
  if (!problemText) {
    return content
  }
  
  // 1. 정확한 텍스트 매칭 시도
  if (content.includes(problemText)) {
    const highlightedText = `<span class="problem-highlight" data-problem-id="${problemArea.area_id}">${problemText}</span>`
    content = content.replace(problemText, highlightedText)
    return content
  }
  
  // 2. 부분 매칭 시도 (공백 무시)
  const normalizedProblemText = problemText.replace(/\s+/g, ' ').trim()
  const normalizedContent = content.replace(/\s+/g, ' ')
  
  if (normalizedContent.includes(normalizedProblemText)) {
    // 원본 콘텐츠에서 해당 부분을 찾아서 하이라이트
    const regex = new RegExp(problemText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')
    content = content.replace(regex, `<span class="problem-highlight" data-problem-id="${problemArea.area_id}">${problemText}</span>`)
    return content
  }
  
  // 3. 키워드 기반 매칭 시도
  const keywords = problemText.split(/\s+/).filter(word => word.length > 1)
  if (keywords.length > 0) {
    keywords.forEach(keyword => {
      if (content.includes(keyword)) {
        const regex = new RegExp(`\\b${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'g')
        content = content.replace(regex, `<span class="problem-highlight" data-problem-id="${problemArea.area_id}">${keyword}</span>`)
      }
    })
  }
  return content
}

// 수정된 영역 하이라이트 함수
const highlightModifiedAreas = (content: string, modifiedAreaIds: string[]): string => {
  // ID 마커로 감싸진 수정된 영역을 찾아서 하이라이트
  modifiedAreaIds.forEach(areaId => {
    const markerPattern = new RegExp(`⟦${areaId}⟧([^⟦]*)⟦/${areaId}⟧`, 'g')
    content = content.replace(markerPattern, (match, text) => {
      return `<span class="modified-highlight" data-modified-id="${areaId}">${text}</span>`
    })
  })
  
  return content
}

// 템플릿 내용 포맷팅 함수
const formatTemplateContent = (content: string): string => {
  // 화살표를 제대로된 포인트로 변환
  content = content.replace(/▶\s*/g, '▶ ')
  content = content.replace(/→\s*/g, '▶ ')
  content = content.replace(/\-\s+/g, '▶ ')  // "- " 형식도 처리
  
  // 기본 줄바꿈을 먼저 처리
  let lines = content.split('\n')
  let formattedLines: string[] = []

  for (let line of lines) {
    line = line.trim()
    if (!line) {
      formattedLines.push('<div class="empty-line"></div>')
      continue
    }

    // 발송 근거 (* 로 시작)
    if (line.startsWith('*')) {
      formattedLines.push(`<div class="disclaimer">${line}</div>`)
    }
    // 포인트 항목 (• 로 시작)
    else if (line.startsWith('•')) {
      formattedLines.push(`<div class="point-item">${line}</div>`)
    }
    // 기본 내용
    else {
      formattedLines.push(`<div class="message-line">${line}</div>`)
    }
  }

  return formattedLines.join('')
}

// 토글 기능
const toggleExpansion = () => {
  isExpanded.value = !isExpanded.value
}

// props.variables가 변경될 때마다 editedVariables 업데이트
watch(() => props.variables, (newVariables) => {
  editedVariables.value = [...newVariables]
}, { deep: true })

</script>

<style scoped>
.kakao-preview-container {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  width: 100%;
}

.kakao-preview {
  background-color: transparent;
  border-radius: 0.8rem;
  overflow: hidden;
  box-shadow: 0 0.2rem 0.8rem rgba(0, 0, 0, 0.15);
  width: 400px;
  flex-shrink: 0;
  align-self: center;
  max-height: none;
  display: flex;
  flex-direction: column;
}

.kakao-content {
  padding: 0;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  background-color: transparent;
}

.message-bubble {
  background-color: #ffffff;
  border-radius: 0.8rem;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.kakao-header {
  background-color: #fee500;
  padding: 0.6rem 1rem;
  text-align: left;
  border-top-left-radius: 0.8rem;
  border-top-right-radius: 0.8rem;
}

.kakao-header-text {
  font-weight: 600;
  color: #3c1e1e;
  font-size: 0.9rem;
}




.bubble-body {
  padding: 0.8rem 1rem;
  background-color: white;
}

.message-text {
  font-size: 0.9rem;
  line-height: 1.6;
  color: #333;
  transition: max-height 0.3s ease;
}

.message-text:not(.expanded) {
  max-height: 8rem;
  overflow: hidden;
  position: relative;
}

.message-text.expanded {
  max-height: none;
  overflow: visible;
}

.toggle-button {
  background-color: #f7f7f7;
  padding: 0.7rem 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  cursor: pointer;
  border-top: 1px solid #e0e0e0;
  transition: background-color 0.2s ease;
}

.toggle-button:hover {
  background-color: #eeeeee;
}

.toggle-icon {
  color: #888;
  font-size: 0.7rem;
  transition: transform 0.2s ease;
  transform: rotate(0deg);
}

.toggle-icon.expanded {
  transform: rotate(90deg);
}

.toggle-text {
  color: #666;
  font-size: 0.85rem;
  font-weight: 500;
}

/* 메시지 라인 스타일 */
:deep(.message-line) {
  color: #333333;
  font-size: 0.9rem;
  margin: 0.3rem 0;
  line-height: 1.5;
  font-weight: normal;
}

/* 포인트 항목 스타일 */
:deep(.point-item) {
  color: #333333;
  font-size: 0.9rem;
  margin: 0.4rem 0;
  line-height: 1.5;
  padding-left: 0.3rem;
}

/* 회색 변수 스타일 */
:deep(.variable-gray) {
  color: #888888;
  background-color: transparent;
  font-weight: normal;
  display: inline;
}

:deep(.disclaimer) {
  color: #888888;
  font-size: 0.75rem;
  margin-top: 1rem;
  padding-top: 0.5rem;
  border-top: 1px solid #f0f0f0;
  line-height: 1.3;
  font-weight: normal;
}

:deep(.empty-line) {
  height: 0.5rem;
}

/* 스크롤바 */
.kakao-content::-webkit-scrollbar { width: 0.4rem; }
.kakao-content::-webkit-scrollbar-track { background: transparent; }
.kakao-content::-webkit-scrollbar-thumb { background: #94a3b1; border-radius: 0.2rem; }
.kakao-content::-webkit-scrollbar-thumb:hover { background: #7a8896; }

/* 변수 스타일 */
:deep(.variable) {
  color: #888888;
  background-color: transparent;
  font-weight: normal;
  display: inline;
  transition: all 0.2s ease;
  margin: 0 1px;
}

:deep(.variable-gray:hover) {
  background-color: #e5e7eb;
  border-color: #9ca3af;
}


/* 문제 영역 하이라이트 */
:deep(.problem-highlight) {
  background-color: #fff3cd;
  color: #856404;
  border: 2px solid #ffc107;
  border-radius: 4px;
  padding: 2px 4px;
  font-weight: bold;
  animation: highlight-pulse 2s infinite;
  cursor: pointer;
}

@keyframes highlight-pulse {
  0% { 
    background-color: #fff3cd;
    border-color: #ffc107;
  }
  50% { 
    background-color: #ffeaa7;
    border-color: #fdcb6e;
  }
  100% { 
    background-color: #fff3cd;
    border-color: #ffc107;
  }
}

/* 수정된 영역 하이라이트 */
:deep(.modified-highlight) {
  background-color: #d4edda;
  color: #155724;
  border: 2px solid #28a745;
  border-radius: 4px;
  padding: 2px 4px;
  font-weight: bold;
  animation: modified-pulse 3s infinite;
}

@keyframes modified-pulse {
  0% { 
    background-color: #d4edda;
    border-color: #28a745;
  }
  50% { 
    background-color: #c3e6cb;
    border-color: #20c997;
  }
  100% { 
    background-color: #d4edda;
    border-color: #28a745;
  }
}



.disclaimer {
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.8rem;
  line-height: 1.4;
}
</style>
