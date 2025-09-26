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
              @click="handleVariableClick"
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

interface KakaoPreviewProps {
  templateContent?: string
  templateTitle?: string
  showVariables: boolean
  variables: string[]
  isRejected: boolean
  rejectedVariables: string[]
  validationErrors?: any[]
}

const props = defineProps<KakaoPreviewProps>()
const emit = defineEmits<{
  variableClick: [variableName: string]
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

  // 2) 텍스트 정리
  let content = props.templateContent ?? ''
  
  // 디버깅을 위한 로그
  console.log('=== KakaoPreviewComponent 템플릿 처리 ===')
  console.log('원본 템플릿:', content)
  
  // 더 정확한 텍스트 정리
  content = content
    .replace(/(변수\s*목록\s*:|변수\s*:).*$/s, '')      // 변수 목록 제거
    .replace(/알림톡\s*템플릿은.*$/s, '')               // 설명 문구 제거
    .replace(/\n\s*\n\s*\n/g, '\n\n')                   // 빈 줄 정리
    .trim()
  
  console.log('정리된 템플릿:', content)
  console.log('================================')

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
      return `<span class="variable-gray">#{${variableName}}</span>`
    })
  })

  // 4) 스마트 포맷팅 - 의미 있는 구조로 변환
  content = formatTemplateContent(content)

  // 검증 오류가 있을 때 문제 영역 하이라이트
  if (props.isRejected && props.validationErrors && props.validationErrors.length > 0) {
    // 템플릿 전체 문제가 있는 경우 전체 하이라이트
    const hasTemplateErrors = props.validationErrors.some((error: any) =>
      error.reason.includes('제목') ||
      error.reason.includes('내용') ||
      error.reason.includes('광고성') ||
      error.reason.includes('정형화') ||
      error.reason.includes('변수가 전혀 사용되지 않음')
    )

    if (hasTemplateErrors) {
      content = `<div class="template-error-highlight">${content}</div>`
    }
  }

  return content
})

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

// 변수 클릭 이벤트 처리
const handleVariableClick = (event: Event) => {
  event.preventDefault()
  event.stopPropagation()
  
  const target = event.target as HTMLElement
  const variableElement = target.closest('[data-variable]') as HTMLElement | null
  const variableName = variableElement?.getAttribute('data-variable') ?? ''

  if (variableName && props.isRejected && props.rejectedVariables.includes(variableName)) {
    emit('variableClick', variableName)
  }
}
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



.template-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #000000;
  display: block;
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
}

:deep(.variable.highlighted) {
  color: #888888 !important;
  background-color: transparent !important;
  font-weight: normal !important;
}

:deep(.variable.rejected-highlight) {
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #f44336;
  cursor: pointer;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.7); }
  70% { box-shadow: 0 0 0 0.5rem rgba(244, 67, 54, 0); }
  100% { box-shadow: 0 0 0 0 rgba(244, 67, 54, 0); }
}

:deep(.template-error-highlight) {
  border: 2px solid #ff5252;
  border-radius: 0.4rem;
  background: rgba(255, 82, 82, 0.05);
  padding: 0.3rem;
  margin: -0.3rem;
  animation: pulse-red 2s ease-in-out infinite;
}

@keyframes pulse-red {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 82, 82, 0.4);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(255, 82, 82, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 82, 82, 0);
  }
}

.disclaimer {
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.8rem;
  line-height: 1.4;
}
</style>
