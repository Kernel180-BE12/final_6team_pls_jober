<template>
  <div class="kakao-preview-container">
    <!-- 카카오톡 미리보기 -->
    <div class="kakao-preview">
      <div class="kakao-header">알림톡 도착</div>
      <div class="kakao-content">
        <div class="kakao-title">
          <span>{{ templateTitle || '모임 일정을\n안내드립니다' }}</span>
          <div class="template-icon">🏠</div>
        </div>

        <div class="kakao-message">
          <div
            class="message-content"
            :class="{ 'expanded': isExpanded }"
            v-html="formattedTemplateContent"
            @click="handleVariableClick"
          ></div>

          <div
            v-if="shouldShowToggle"
            class="toggle-button"
            @click="toggleExpansion"
          >
            {{ isExpanded ? '접기' : '자세히 보기' }}
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
  variables: Record<string, string>
  isRejected: boolean
  rejectedVariables: string[]
  validationErrors?: any[]
}

const props = defineProps<KakaoPreviewProps>()
const emit = defineEmits<{
  variableClick: [variableName: string]
  rejectTemplate: []
  submitTemplate: []
  updateVariables: [variables: Record<string, string>]
}>()

const editedVariables = ref({ ...props.variables })
const isExpanded = ref(false)
const shouldShowToggle = ref(false)

// 템플릿 내용을 포맷팅하여 변수를 적절한 스타일로 렌더링
const formattedTemplateContent = computed(() => {
  // 1) 기본 템플릿
  if (!props.templateContent) {
    const defaultContent = `
안녕하세요, #[신청자님], 신청하신 #[모임명] 스터디 모임 일정을 안내드립니다.

다음과 같은 상세 정보입니다.

▶ 모임명: #[모임 내용을 여기에 입력하세요]
▶ 일시: #[시행 일자를 여기에 입력하세요]
▶ 장소: #[장소명]

자세한 사항은 홈페이지를 참고해 주시기 바랍니다.

많은 이용 부탁드립니다.

* 본 알림은 정보통신망법에 따라 발송되었습니다.
    `

    // 내용 길이 체크 및 토글 설정 (줄 수 기준)
    const lines = defaultContent.split('\n').filter(line => line.trim())
    shouldShowToggle.value = lines.length > 6

    return formatTemplateContent(defaultContent.trim())
  }

  // 2) 텍스트 정리
  let content = props.templateContent ?? ''
  content = content
    .replace(/(변수\s*목록\s*:|변수\s*:).*$/s, '')      // 변수 목록 제거
    .replace(/알림톡\s*템플릿은.*$/s, '')               // 설명 문구 제거
    .replace(/\n\s*\n\s*\n/g, '\n\n')                   // 빈 줄 정리
    .trim()

  // 내용 길이 체크 (줄 수 기준)
  const lines = content.split('\n').filter(line => line.trim())
  shouldShowToggle.value = lines.length > 6

  // 3) 변수 하이라이트
  if (props.showVariables) {
    const anyVarPattern = /\{\{([^}]+)\}\}|#\{([^}]+)\}|\{([^}]+)\}/g

    content = content.replace(anyVarPattern, (match, a, b, c) => {
      const variableName = (a || b || c || '').trim()
      let variableClass = 'variable highlighted'

      if (props.isRejected && props.rejectedVariables.includes(variableName)) {
        variableClass += ' rejected-highlight'
      }

      return `<span class="${variableClass}" data-variable="${variableName}">{${variableName}}</span>`
    })
  }

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
  // 변수를 회색으로 변환
  content = content.replace(/#\[([^\]]+)\]/g, '<span class="variable-gray">#[$1]</span>')

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
    // 기본 내용 - 모든 줄을 동일하게 처리
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
  editedVariables.value = { ...newVariables }
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
  background-color: white;
  border-radius: 0.6rem;
  overflow: hidden;
  box-shadow: 0 0.2rem 0.8rem rgba(0, 0, 0, 0.1);
  width: 20rem;
  flex-shrink: 0;
  align-self: center;
  max-height: 60vh;
  display: flex;
  flex-direction: column;
}

.kakao-header {
  background-color: #fee500;
  padding: 0.8rem 1rem;
  font-weight: 600;
  color: #333;
  text-align: center;
}

.kakao-content {
  padding: 1rem;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.kakao-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 1rem;
  font-weight: 600;
  color: #000000;
}
.template-icon {
  font-size: 1.2rem;
  background-color: #5865f2;
  color: white;
  width: 1.4rem;
  height: 1.4rem;
  border-radius: 0.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kakao-message {
  margin-bottom: 1rem;
  line-height: 1.6;
  flex: 1;
  overflow: hidden;
}

.message-content {
  max-height: none;
  overflow: visible;
  transition: max-height 0.3s ease;
}

.message-content:not(.expanded) {
  max-height: 6rem;
  overflow: hidden;
}

.message-content.expanded {
  max-height: none;
}

.toggle-button {
  background-color: #f5f5f5;
  color: #666;
  padding: 0.5rem 1rem;
  margin: 0.5rem -1rem -1rem -1rem;
  text-align: center;
  cursor: pointer;
  border-top: 1px solid #e0e0e0;
  font-size: 0.85rem;
  transition: background-color 0.2s ease;
}

.toggle-button:hover {
  background-color: #eeeeee;
}

.kakao-message p {
  margin: 0.4rem 0;
}

/* 메시지 라인 스타일 - 단순하고 깔끔하게 */
:deep(.message-line) {
  color: #000000;
  font-size: 0.9rem;
  margin: 0.2rem 0;
  line-height: 1.4;
  font-weight: normal;
}

/* 회색 변수 스타일 */
:deep(.variable-gray) {
  color: #888888;
  font-weight: normal;
}

:deep(.disclaimer) {
  color: #888888;
  font-size: 0.75rem;
  margin-top: 0.8rem;
  line-height: 1.3;
  font-weight: normal;
}

:deep(.empty-line) {
  height: 0.3rem;
}

/* 스크롤바 */
.kakao-message::-webkit-scrollbar { width: 0.3rem; }
.kakao-message::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 0.15rem; }
.kakao-message::-webkit-scrollbar-thumb { background: #c1c1c1; border-radius: 0.15rem; }
.kakao-message::-webkit-scrollbar-thumb:hover { background: #a8a8a8; }

/* 변수 스타일 */
:deep(.variable) {
  background-color: #f8f9fa;
  padding: 0.1rem 0.3rem;
  border-radius: 0.2rem;
  color: #495057;
  border: 1px solid #dee2e6;
  transition: all 0.2s ease;
  min-width: 1rem;
  display: inline-block;
  font-weight: 500;
}

:deep(.variable.highlighted) {
  background-color: #fff3cd !important;
  border: 1px solid #ffeaa7 !important;
  color: #856404 !important;
  font-weight: 600 !important;
}

:deep(.variable.rejected-highlight) {
  background-color: #ffebee;
  color: #c62828;
  border: 0.1rem solid #f44336;
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
