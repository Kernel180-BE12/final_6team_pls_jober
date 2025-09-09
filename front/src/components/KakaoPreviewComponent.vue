<template>
  <div class="kakao-preview-container">
    
    <!-- 카카오톡 미리보기 -->
    <div class="kakao-preview">
      <div class="kakao-header">알림톡 도착</div>
      <div class="kakao-content">
        <div class="kakao-title">
          <span>쿠폰 발급 안내</span>
          <div class="coupon-icon">🎫</div>
        </div>
        
        <div 
          class="kakao-message" 
          v-html="formattedTemplateContent" 
          @click="handleVariableClick"
          @input="handleVariableChange"
          @blur="handleVariableBlur"
        >
        </div>
      </div>
    </div>
    
    <!-- 하단 컨트롤은 TemplateResultView에서 처리됨 -->
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'

interface KakaoPreviewProps {
  templateContent?: string
  showVariables: boolean
  variables: Record<string, string>
  isModifying: boolean
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
const editingField = ref<string | null>(null)
const originalValues = ref<Record<string, string>>({ ...props.variables })

// 템플릿 내용을 포맷팅하여 변수를 적절한 스타일로 렌더링
const formattedTemplateContent = computed(() => {
  if (!props.templateContent) {
    // 기본 템플릿 내용
    return `
      <p>안녕하세요, <span class="variable">${props.variables.recipient}</span> 회원님!</p>
      <p><span class="variable">${props.variables.sender}</span>입니다.</p>
      <p>회원님께 발급된 쿠폰을 안내드립니다.</p>
      <p>▶ 쿠폰명 : <span class="variable">${props.variables.couponName}</span></p>
      <p>▶ 사용기한 : <span class="variable">${props.variables.expiryDate}</span></p>
      <p><span class="variable">${props.variables.additionalMessage}</span></p>
      <p class="disclaimer">* 이 메시지는 이용약관(계약서) 동의에 따라 지급된 쿠폰 안내 메시지입니다.</p>
    `
  }
  
  let content = props.templateContent
  
  // 변수 목록 부분 제거 (AI가 생성한 템플릿에서 변수 목록이 포함된 경우)
  if (content) {
    // "변수 목록:" 또는 "변수:" 이후의 모든 내용을 제거
    const variableListPattern = /(변수\s*목록\s*:|변수\s*:).*$/s
    content = content.replace(variableListPattern, '').trim()
    
    // "알림톡 템플릿은..." 같은 설명 문구도 제거
    const disclaimerPattern = /알림톡\s*템플릿은.*$/s
    content = content.replace(disclaimerPattern, '').trim()
    
    // 빈 줄들 정리
    content = content.replace(/\n\s*\n\s*\n/g, '\n\n').trim()
  }
  
  console.log('원본 템플릿 내용:', props.templateContent)
  console.log('정리된 템플릿 내용:', content)
  console.log('사용 가능한 변수들:', Object.keys(props.variables))
  console.log('반려 상태:', props.isRejected)
  console.log('반려된 변수들:', props.rejectedVariables)
  
  // 변수들을 적절한 스타일로 교체
  Object.keys(props.variables).forEach(key => {
    const value = props.variables[key]
    
    // 여러 변수 패턴 지원: #{변수명}, {{변수명}}, {변수명}
    const patterns = [
      new RegExp(`#\\{${key}\\}`, 'g'),
      new RegExp(`\\{\\{${key}\\}\\}`, 'g'),
      new RegExp(`\\{${key}\\}`, 'g')
    ]
    
    let variableClass = 'variable'
    
    // 변수값 표시 토글에 따른 스타일 적용
    if (props.showVariables) {
      variableClass += ' highlighted'
    }
    
    // 수정 모드일 때 편집 가능한 스타일 추가
    if (props.isModifying && !props.isRejected) {
      variableClass += ' clickable editable'
    }
    
    // 반려된 변수 하이라이트
    if (props.isRejected && props.rejectedVariables.includes(key)) {
      variableClass += ' rejected-highlight'
      console.log(`변수 "${key}"가 반려되어 하이라이트 적용됨`)
    }
    
    // 모든 패턴에 대해 교체 수행
    patterns.forEach((pattern, index) => {
      const beforeReplace = content
      content = content.replace(pattern, 
        `<span class="${variableClass}" ${props.isModifying ? 'contenteditable="true"' : ''} data-variable="${key}">${value}</span>`
      )
      if (beforeReplace !== content) {
        console.log(`변수 "${key}" 패턴 ${index + 1}에서 교체됨:`, pattern)
      }
    })
  })
  
  // 버튼 처리: (버튼) 텍스트를 실제 버튼으로 변환
  content = content.replace(/\(버튼\)\s*([^\n]+)/g, '<div class="kakao-button">$1</div>')
  
  // 부가 정보/가이드라인 처리 (연한 색으로 표시)
  content = content.replace(/\*([^*]+)\*/g, '<span class="guide-text">$1</span>')
  
  // 쿠폰 사용방법, 이벤트 기간 등 부가 정보 처리
  content = content.replace(/(쿠폰\s*사용방법|이벤트\s*기간|고객센터|더욱\s*편리한).*$/gm, '<span class="guide-text">$&</span>')
  
  // 줄바꿈을 <p> 태그로 변환
  content = content.replace(/\n/g, '</p><p>')
  content = `<p>${content}</p>`
  
  console.log('최종 포맷된 템플릿:', content)
  return content
})

// props.variables가 변경될 때마다 editedVariables 업데이트
watch(() => props.variables, (newVariables) => {
  editedVariables.value = { ...newVariables }
  originalValues.value = { ...newVariables }
}, { deep: true })

// 특정 필드 편집 시작
const startEditing = (fieldName: string) => {
  if (!props.isModifying) return
  
  editingField.value = fieldName
  originalValues.value[fieldName] = editedVariables.value[fieldName]
  
  // 다음 tick에서 해당 요소에 포커스
  nextTick(() => {
    const element = document.querySelector(`[contenteditable="true"]`) as HTMLElement
    if (element) {
      element.focus()
      // 텍스트 전체 선택
      const range = document.createRange()
      range.selectNodeContents(element)
      const selection = window.getSelection()
      if (selection) {
        selection.removeAllRanges()
        selection.addRange(range)
      }
    }
  })
}

// 편집 완료
const finishEditing = (fieldName: string) => {
  const newValue = editedVariables.value[fieldName]
  
  // 빈 값이면 원래 값으로 복원
  if (!newValue || newValue.trim() === '') {
    editedVariables.value[fieldName] = originalValues.value[fieldName]
  }
  
  editingField.value = null
  
  // 변경된 변수들을 부모에게 전달
  emit('updateVariables', editedVariables.value)
}

// 편집 취소
const cancelEditing = () => {
  if (editingField.value) {
    editedVariables.value[editingField.value] = originalValues.value[editingField.value]
    editingField.value = null
  }
}

// 변수 클릭 이벤트 처리
const handleVariableClick = (event: Event) => {
  const target = event.target as HTMLElement
  const variableElement = target.closest('[data-variable]') as HTMLElement
  
  if (variableElement && props.isModifying) {
    const variableName = variableElement.getAttribute('data-variable')
    if (variableName) {
      // 변수 편집 시작
      startEditing(variableName)
    }
  } else if (variableElement && props.isRejected) {
    const variableName = variableElement.getAttribute('data-variable')
    if (variableName && props.rejectedVariables.includes(variableName)) {
      // 반려된 변수 클릭 시 부모 컴포넌트에 이벤트 전달
      emit('variableClick', variableName)
    }
  }
}

// 변수 값 변경 감지
const handleVariableChange = (event: Event) => {
  const target = event.target as HTMLElement
  const variableElement = target.closest('[data-variable]') as HTMLElement
  
  if (variableElement) {
    const variableName = variableElement.getAttribute('data-variable')
    if (variableName) {
      editedVariables.value[variableName] = variableElement.textContent || ''
    }
  }
}

// 변수 편집 완료 감지
const handleVariableBlur = (event: Event) => {
  const target = event.target as HTMLElement
  const variableElement = target.closest('[data-variable]') as HTMLElement
  
  if (variableElement) {
    const variableName = variableElement.getAttribute('data-variable')
    if (variableName) {
      finishEditing(variableName)
    }
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

.coupon-icon {
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

/* 카카오톡 메시지 스크롤바 스타일링 */
.kakao-message::-webkit-scrollbar {
  width: 0.3rem;
}

.kakao-message::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 0.15rem;
}

.kakao-message::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 0.15rem;
}

.kakao-message::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.variable {
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

.variable.highlighted {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffc107;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: 500;
}

.variable.clickable {
  cursor: pointer;
}

.variable.clickable:hover {
  background-color: #ffeaa7;
  transform: scale(1.02);
  box-shadow: 0 0.1rem 0.4rem rgba(0, 0, 0, 0.15);
}

.variable.editable {
  background-color: #e8f5e8;
  border: 0.1rem dashed #4caf50;
  position: relative;
}

.variable.editable:hover {
  background-color: #d4edda;
  border-color: #28a745;
  transform: scale(1.02);
  box-shadow: 0 0.1rem 0.4rem rgba(76, 175, 80, 0.3);
}

.variable.editable::after {
  content: '✏️';
  position: absolute;
  top: -0.2rem;
  right: -0.2rem;
  font-size: 0.7rem;
  opacity: 0.7;
}

.variable.editing {
  background-color: #e3f2fd;
  border: 0.1rem solid #2196f3;
  outline: none;
  cursor: text;
  box-shadow: 0 0 0 0.1rem rgba(33, 150, 243, 0.2);
}

.variable.editing:focus {
  background-color: #f5f5f5;
  border-color: #1976d2;
}

.variable.rejected-highlight {
  background-color: #ffebee;
  color: #c62828;
  border: 0.1rem solid #f44336;
  cursor: pointer;
  animation: pulse 2s infinite;
}

.variable.rejected-highlight:hover {
  background-color: #ffcdd2;
  transform: scale(1.05);
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

/* 카카오톡 버튼 스타일 */
.kakao-button {
  display: inline-block;
  background-color: #fee500;
  color: #3c1e1e;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.9rem;
  margin: 0.3rem 0;
  text-align: center;
  border: 1px solid #fdd835;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  cursor: pointer;
}

.kakao-button:hover {
  background-color: #fdd835;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* 가이드라인/부가 정보 텍스트 스타일 */
.guide-text {
  color: #888;
  font-size: 0.85rem;
  font-style: italic;
  opacity: 0.8;
}



/* contenteditable 요소 스타일링 */
.variable[contenteditable="true"] {
  cursor: text;
  user-select: text;
}

.variable[contenteditable="true"]:focus {
  outline: none;
}

/* 편집 중일 때 텍스트 선택 스타일 */
.variable.editing::selection {
  background-color: #bbdefb;
}

.variable.editing::-moz-selection {
  background-color: #bbdefb;
}
</style>