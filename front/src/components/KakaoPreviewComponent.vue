<template>
  <div class="kakao-preview-container">
    
    <!-- 카카오톡 미리보기 -->
    <div class="kakao-preview">
      <div class="kakao-header">알림톡 도착</div>
      <div class="kakao-content">
        <div class="kakao-title">
          <span>쿠폰 발급 안내</span>
          <div class="template-icon">🎫</div>
        </div>
        
        <div 
          class="kakao-message" 
          v-html="formattedTemplateContent" 
          @click="handleVariableClick"
          @input="handleVariableChange"
          @blur="handleVariableBlur"
          @keydown="handleKeyDown"
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
  finishAllEditing: []
}>()

const editedVariables = ref({ ...props.variables })
const editingField = ref<string | null>(null)
const originalValues = ref<Record<string, string>>({ ...props.variables })
const modifiedVariables = ref<Set<string>>(new Set())
const isEditing = ref(false)

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
  
  // showVariables가 true일 때 모든 변수 패턴을 하이라이트
  if (props.showVariables) {
    const variablePattern = /\{[^}]+\}/g
    content = content.replace(variablePattern, (match) => {
      return `<span class="variable highlighted" data-variable="${match}">${match}</span>`
    })
  }
  
  // props.variables에 있는 변수들을 적절한 스타일로 교체 (showVariables가 false일 때만)
  if (!props.showVariables) {
    Object.keys(props.variables).forEach(key => {
      const value = props.variables[key]
      
      // 여러 변수 패턴 지원: #{변수명}, {{변수명}}, {변수명}
      const patterns = [
        new RegExp(`#\\{${key}\\}`, 'g'),
        new RegExp(`\\{\\{${key}\\}\\}`, 'g'),
        new RegExp(`\\{${key}\\}`, 'g')
      ]
      
      let variableClass = 'variable'
      
      // 수정 모드일 때 편집 가능한 스타일 추가
      if (props.isModifying && !props.isRejected) {
        variableClass += ' clickable editable'
      }
      
      // 편집 중인 변수 표시
      if (editingField.value === key) {
        variableClass += ' editing'
      }
      
      // 수정된 변수 표시
      if (modifiedVariables.value.has(key)) {
        variableClass += ' modified'
      }
      
      // 반려된 변수 하이라이트
      if (props.isRejected && props.rejectedVariables.includes(key)) {
        variableClass += ' rejected-highlight'
        console.log(`변수 "${key}"가 반려되어 하이라이트 적용됨`)
      }
      
      // 모든 패턴에 대해 교체 수행
      patterns.forEach((pattern, index) => {
        // HTML 태그를 이스케이프 처리
        const escapedValue = value.replace(/[<>&"']/g, (match) => {
          const escapeMap: { [key: string]: string } = {
            '<': '&lt;',
            '>': '&gt;',
            '&': '&amp;',
            '"': '&quot;',
            "'": '&#39;'
          }
          return escapeMap[match]
        })
        
        content = content.replace(pattern, 
          `<span class="${variableClass}" ${props.isModifying ? 'contenteditable="true"' : ''} data-variable="${key}">${escapedValue}</span>`
        )
      })
    })
  }
  
  // 수정 모드일 때 이미 하이라이트된 변수들을 편집 가능하게 만들기
  if (props.isModifying && !props.isRejected) {
    // 이미 하이라이트된 변수들을 편집 가능하게 변환
    content = content.replace(/<span class="variable highlighted" data-variable="\{([^}]+)\}">\{[^}]+\}<\/span>/g, (match, variableName) => {
      return `<span class="variable clickable editable" data-variable="${variableName}" data-original-text="{${variableName}}"><span class="editable-variable-name" contenteditable="true">${variableName}</span></span>`
    })
  }
  
  // 버튼 처리: (버튼) 텍스트를 실제 버튼으로 변환
  content = content.replace(/\(버튼\)\s*([^\n]+)/g, '<div class="kakao-button">$1</div>')
  
  // 부가 정보/가이드라인 처리 (연한 색으로 표시)
  content = content.replace(/\*([^*]+)\*/g, '<span class="guide-text">$1</span>')
  
  // 쿠폰 사용방법, 이벤트 기간 등 부가 정보 처리
  content = content.replace(/(쿠폰\s*사용방법|이벤트\s*기간|고객센터|더욱\s*편리한).*$/gm, '<span class="guide-text">$&</span>')
  
  // 줄바꿈을 <p> 태그로 변환
  content = content.replace(/\n/g, '</p><p>')
  content = `<p>${content}</p>`
  
  // HTML 태그를 제거한 순수 텍스트만 로그에 출력
  const textContent = content.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim()
  console.log('최종 포맷된 템플릿 (텍스트만):', textContent)
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
  isEditing.value = true
  originalValues.value[fieldName] = editedVariables.value[fieldName]
  
  // 다음 tick에서 편집 가능한 변수명 부분에 포커스
  nextTick(() => {
    const element = document.querySelector(`[data-variable="${fieldName}"] .editable-variable-name`) as HTMLElement
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
  } else {
    // 값이 변경되었으면 수정된 변수 목록에 추가
    if (newValue !== originalValues.value[fieldName]) {
      modifiedVariables.value.add(fieldName)
    }
  }
  
  editingField.value = null
  isEditing.value = false
  
  // 변경된 변수들을 부모에게 전달
  emit('updateVariables', editedVariables.value)
}

// 편집 취소
const cancelEditing = () => {
  if (editingField.value) {
    editedVariables.value[editingField.value] = originalValues.value[editingField.value]
    editingField.value = null
    isEditing.value = false
  }
}

// 모든 편집 완료 (수정 완료 버튼 클릭 시)
const finishAllEditing = () => {
  // 현재 편집 중인 필드가 있으면 완료 처리
  if (editingField.value) {
    finishEditing(editingField.value)
  }
  
  // 수정된 변수들을 부모에게 전달
  emit('updateVariables', editedVariables.value)
  emit('finishAllEditing')
  
  console.log('모든 편집 완료, 수정된 변수들:', Array.from(modifiedVariables.value))
}

// 변수 클릭 이벤트 처리
const handleVariableClick = (event: Event) => {
  const target = event.target as HTMLElement
  const variableElement = target.closest('[data-variable]') as HTMLElement
  
  if (variableElement && props.isModifying) {
    const variableName = variableElement.getAttribute('data-variable')
    if (variableName) {
      // 편집 가능한 변수명 부분을 클릭했을 때만 편집 시작
      const editableNameElement = variableElement.querySelector('.editable-variable-name')
      if (editableNameElement && (target === editableNameElement || editableNameElement.contains(target))) {
        startEditing(variableName)
      }
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
      // 편집 가능한 변수명 부분만 가져오기
      const editableNameElement = variableElement.querySelector('.editable-variable-name')
      if (editableNameElement) {
        const newVariableName = editableNameElement.textContent || ''
        // 중괄호를 제거하고 순수 변수명만 저장
        editedVariables.value[variableName] = newVariableName.replace(/[{}]/g, '')
      } else {
        // HTML 태그를 제거하고 순수 텍스트만 가져오기
        const textContent = variableElement.textContent || ''
        editedVariables.value[variableName] = textContent
      }
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

// 키보드 이벤트 처리
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    const target = event.target as HTMLElement
    const variableElement = target.closest('[data-variable]') as HTMLElement
    
    if (variableElement) {
      const variableName = variableElement.getAttribute('data-variable')
      if (variableName) {
        finishEditing(variableName)
      }
    }
  } else if (event.key === 'Escape') {
    event.preventDefault()
    cancelEditing()
  }
}

// 부모 컴포넌트에서 호출할 수 있도록 함수 노출
defineExpose({
  finishAllEditing
})

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

:deep(.variable.highlighted) {
  background-color: #fff3cd !important;
  padding: 2px 4px !important;
  border-radius: 3px !important;
  display: inline-block !important;
  border: 1px solid #ffeaa7 !important;
  color: #856404 !important;
  font-weight: 600 !important;
}

:deep(.variable.clickable) {
  cursor: pointer;
}

:deep(.variable.clickable:hover) {
  background-color: #ffeaa7;
  transform: scale(1.02);
  box-shadow: 0 0.1rem 0.4rem rgba(0, 0, 0, 0.15);
}

:deep(.variable.editable) {
  background-color: #e8f5e8;
  border: 0.1rem dashed #4caf50;
  position: relative;
}

:deep(.variable.editable:hover) {
  background-color: #d4edda;
  border-color: #28a745;
  transform: scale(1.02);
  box-shadow: 0 0.1rem 0.4rem rgba(76, 175, 80, 0.3);
}

:deep(.variable.editable::after) {
  content: '✏️';
  position: absolute;
  top: -0.2rem;
  right: -0.2rem;
  font-size: 0.7rem;
  opacity: 0.7;
}

:deep(.variable.editing) {
  background-color: #e3f2fd;
  border: 0.1rem solid #2196f3;
  outline: none;
  cursor: text;
  box-shadow: 0 0 0 0.1rem rgba(33, 150, 243, 0.2);
}

:deep(.variable.editing:focus) {
  background-color: #f5f5f5;
  border-color: #1976d2;
}

:deep(.variable.rejected-highlight) {
  background-color: #ffebee;
  color: #c62828;
  border: 0.1rem solid #f44336;
  cursor: pointer;
  animation: pulse 2s infinite;
}

:deep(.variable.rejected-highlight:hover) {
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

/* 수정된 변수 스타일 */
:deep(.variable.modified) {
  background-color: #d4edda !important;
  border-color: #28a745 !important;
  color: #155724 !important;
  position: relative;
}

:deep(.variable.modified::after) {
  content: '✓';
  position: absolute;
  top: -0.2rem;
  right: -0.2rem;
  font-size: 0.7rem;
  color: #28a745;
  font-weight: bold;
  background: white;
  border-radius: 50%;
  width: 1rem;
  height: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

/* 편집 가능한 변수명 스타일 */
:deep(.editable-variable-name) {
  background-color: transparent;
  border: none;
  outline: none;
  color: inherit;
  font-weight: inherit;
  display: inline;
  min-width: 1rem;
  padding: 0;
  margin: 0;
  cursor: text;
  width: 100%;
}

:deep(.editable-variable-name:focus) {
  background-color: #d4edda;
  border-radius: 2px;
  padding: 1px 2px;
  outline: 1px solid #28a745;
}

:deep(.editable-variable-name[contenteditable="true"]) {
  cursor: text;
  user-select: text;
}

:deep(.editable-variable-name[contenteditable="true"]:focus) {
  outline: none;
  background-color: #d4edda;
  border-radius: 2px;
  padding: 1px 2px;
}

/* 수정 모드에서 편집 가능한 변수 스타일 (중괄호 없음) */
:deep(.variable.editable) {
  position: relative;
  display: inline-block;
  background-color: #e8f5e8;
  border: 0.1rem dashed #4caf50;
  border-radius: 0.2rem;
  padding: 0.1rem 0.3rem;
  margin: 0 0.1rem;
}

/* 중괄호 표시 제거 */
:deep(.variable.editable::before),
:deep(.variable.editable::after) {
  display: none;
}

/* 편집 중일 때 중괄호 숨기기 */
:deep(.variable.editing::before),
:deep(.variable.editing::after) {
  display: none;
}

/* 편집 가능한 변수명이 편집 중일 때 */
:deep(.variable.editing .editable-variable-name) {
  background-color: #d4edda;
  border-radius: 2px;
  padding: 1px 2px;
  outline: 1px solid #28a745;
}

/* 편집 중인 변수 전체 스타일 */
:deep(.variable.editing) {
  background-color: #d4edda;
  border-color: #28a745;
  box-shadow: 0 0 0 0.1rem rgba(40, 167, 69, 0.2);
}
</style>