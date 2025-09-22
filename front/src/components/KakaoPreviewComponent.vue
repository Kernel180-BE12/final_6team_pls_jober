<template>
  <div class="kakao-preview-container">
    <!-- 카카오톡 미리보기 -->
    <div class="kakao-preview">
      <div class="kakao-header">알림톡 도착</div>
      <div class="kakao-content">
        <div class="kakao-title">
          <span>{{ templateTitle || '알림톡 템플릿' }}</span>
          <div class="template-icon">📱</div>
        </div>

        <div 
          class="kakao-message" 
          v-html="formattedTemplateContent"
          @click="handleVariableClick"
        ></div>
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
}

const props = defineProps<KakaoPreviewProps>()
const emit = defineEmits<{
  variableClick: [variableName: string]
  rejectTemplate: []
  submitTemplate: []
  updateVariables: [variables: Record<string, string>]
}>()

const editedVariables = ref({ ...props.variables })

// 템플릿 내용을 포맷팅하여 변수를 적절한 스타일로 렌더링
const formattedTemplateContent = computed(() => {
  // 1) 기본 템플릿
  if (!props.templateContent) {
    return `
      <p>안녕하세요, <span class="variable">${props.variables.recipient ?? ''}</span> 회원님!</p>
      <p><span class="variable">${props.variables.sender ?? ''}</span>입니다.</p>
      <p>회원님께 발급된 쿠폰을 안내드립니다.</p>
      <p>▶ 쿠폰명 : <span class="variable">${props.variables.couponName ?? ''}</span></p>
      <p>▶ 사용기한 : <span class="variable">${props.variables.expiryDate ?? ''}</span></p>
      <p><span class="variable">${props.variables.additionalMessage ?? ''}</span></p>
      <p class="disclaimer">* 이 메시지는 이용약관(계약서) 동의에 따라 지급된 쿠폰 안내 메시지입니다.</p>
    `
  }

  // 2) 텍스트 정리
  let content = props.templateContent ?? ''
  content = content
    .replace(/(변수\s*목록\s*:|변수\s*:).*$/s, '')      // 변수 목록 제거
    .replace(/알림톡\s*템플릿은.*$/s, '')               // 설명 문구 제거
    .replace(/\n\s*\n\s*\n/g, '\n\n')                   // 빈 줄 정리
    .trim()

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

  // 4) 줄바꿈을 <p> 태그로 변환
  content = content.replace(/\n/g, '</p><p>')
  content = `<p>${content}</p>`

  return content
})

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
  font-size: 1.2rem;
  font-weight: 600;
}
.template-icon {
  font-size: 1.5rem;
  background-color: #4caf50;
  color: white;
  width: 1.6rem;
  height: 1.6rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kakao-message {
  margin-bottom: 1rem;
  line-height: 1.6;
  flex: 1;
  overflow-y: auto;
}

.kakao-message p {
  margin: 0.4rem 0;
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

.disclaimer {
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.8rem;
  line-height: 1.4;
}
</style>
