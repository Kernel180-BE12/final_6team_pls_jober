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
            <!-- 생성된 제목 표시 -->
            <div v-if="props.templateTitle" class="message-title">
              {{ props.templateTitle }}
            </div>
            <div
              class="message-text"
              v-html="formattedTemplateContent"
            ></div>
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
  templateTitle?: string
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

    return formatTemplateContent(defaultContent.trim())
  }

  // 2) 최소한의 텍스트 정리만 수행 (원본 내용 보존)
  let content = props.templateContent ?? ''
  
  console.log('=== KakaoPreviewComponent 디버깅 ===')
  console.log('원본 templateContent:', content)
  console.log('templateContent 길이:', content.length)
  
  // 필수적인 정리만 수행
  content = content
    .replace(/\n\s*\n\s*\n/g, '\n\n')                   // 연속된 빈 줄을 2개로 제한
    .replace(/⟦([^⟦]+)⟧([^⟦]*)⟦\/\1⟧/g, '$2')         // 마커 제거만 (⟦ID⟧내용⟦/ID⟧ → 내용)
    .trim()
  
  console.log('정리된 content:', content)
  console.log('정리된 content 길이:', content.length)
  


  // 3) 변수 하이라이팅 처리 (showVariables prop에 따라)
  if (props.showVariables) {
    const varPatterns = [
      /\{\{([^}]+)\}\}/g,  // {{변수}}
      /#\{([^}]+)\}/g,      // #{변수}
      /\{([^}]+)\}/g,       // {변수}
      /\[([^\]]+)\]/g       // [변수] - 대괄호 형태도 변수로 처리
    ]

    varPatterns.forEach(pattern => {
      content = content.replace(pattern, (match, varName) => {
        const variableName = varName.trim()
        return `<span class="variable-highlight" data-variable="${variableName}">#{${variableName}}</span>`
      })
    })
  }

  // 4) 스마트 포맷팅 - 의미 있는 구조로 변환
  console.log('포맷팅 전 content:', content)
  content = formatTemplateContent(content)
  console.log('포맷팅 후 content:', content)


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
  console.log('formatTemplateContent 입력:', content)
  
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

  const result = formattedLines.join('')
  console.log('formatTemplateContent 출력:', result)
  return result
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
  width: 320px; /* 16글자 너비 (한글 1글자 = 20px, 공백 반칸 고려) */
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

.message-title {
  font-weight: 600;
  font-size: 1rem;
  color: #333;
  margin-bottom: 0.8rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #f0f0f0;
}

.message-text {
  font-size: 0.9rem;
  line-height: 1.6;
  color: #333;
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

/* 노란색 변수 하이라이트 스타일 */
:deep(.variable-highlight) {
  background-color: #FFE066;
  color: #333333;
  border: 1px solid #FFD700;
  border-radius: 3px;
  padding: 1px 3px;
  font-weight: 500;
  display: inline;
  transition: all 0.2s ease;
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

:deep(.variable-highlight:hover) {
  background-color: #FFD700;
  border-color: #FFA500;
  transform: scale(1.02);
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
