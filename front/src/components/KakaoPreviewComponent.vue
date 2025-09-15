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
const modifiedVariables = ref<Set<string>>(new Set())
const cachedTemplateContent = ref('')

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
    // editedVariables를 우선적으로 사용하여 최신 수정된 값 반영
    const variablesToUse = { ...props.variables, ...editedVariables.value }
    
    const variablePattern = /\{[^}]+\}/g
    content = content.replace(variablePattern, (match) => {
      // 중괄호를 제거하여 변수명만 추출
      const variableName = match.replace(/[{}]/g, '')
      
      // 수정된 변수인지 확인
      const isModified = modifiedVariables.value.has(variableName)
      const isEditing = false
      
      let variableClass = 'variable highlighted'
      
      // 편집 기능 제거
      
      // 편집 중인 변수 표시 (연두색 배경)
      // 편집 기능 제거
            
      // 반려된 변수 하이라이트
      if (props.isRejected && props.rejectedVariables.includes(variableName)) {
        variableClass += ' rejected-highlight'
      }
      
      // 수정 모드일 때는 중괄호 없이 표시, 수정 완료 후에는 중괄호와 함께 표시
      const displayValue = variablesToUse[variableName] ? `{${variablesToUse[variableName]}}` : match
      
      return `<span class="${variableClass}" data-variable="${variableName}">${displayValue}</span>`
    })
  }
  
  // props.variables에 있는 변수들을 적절한 스타일로 교체
  // showVariables가 false일 때는 실제 값으로 교체, true일 때는 변수명을 하이라이트
  if (!props.showVariables) {
    // editedVariables를 우선적으로 사용하여 최신 수정된 값 반영
    const variablesToUse = { ...props.variables, ...editedVariables.value }
    
    Object.keys(variablesToUse).forEach(key => {
      const value = variablesToUse[key]
      
      // 여러 변수 패턴 지원: #{변수명}, {{변수명}}, {변수명}
      const patterns = [
        new RegExp(`#\\{${key}\\}`, 'g'),
        new RegExp(`\\{\\{${key}\\}\\}`, 'g'),
        new RegExp(`\\{${key}\\}`, 'g')
      ]
      
      let variableClass = 'variable'
      
      // 편집 중인 변수 표시
      // 편집 기능 제거
    
      // 반려된 변수 하이라이트
      if (props.isRejected && props.rejectedVariables.includes(key)) {
        variableClass += ' rejected-highlight'
        console.log(`변수 "${key}"가 반려되어 하이라이트 적용됨`)
      }
      
      // 모든 패턴에 대해 교체 수행 - 중괄호 유지
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
        
        const displayValue = `{${escapedValue}}`
        
        content = content.replace(pattern, `<span class="${variableClass}" data-variable="${key}">${displayValue}</span>`)
      })
    })
  }
  
  // 편집 기능 제거
  
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
  
  // 편집 중이 아닐 때만 로그 출력 및 캐시 업데이트
  if (true) {
    console.log('최종 포맷된 템플릿 (텍스트만):', textContent)
    cachedTemplateContent.value = content
  }
  
  return content
})

// props.variables가 변경될 때마다 editedVariables 업데이트
watch(() => props.variables, (newVariables) => {
  editedVariables.value = { ...newVariables }
}, { deep: true })

// editedVariables가 변경될 때마다 미리보기 업데이트
watch(editedVariables, (newVariables) => {
  // 로그 제거 - 필요시에만 활성화
  // console.log('editedVariables 변경됨:', newVariables)
}, { deep: true })

// 변수 클릭 이벤트 처리
const handleVariableClick = (event: Event) => {
  event.preventDefault()
  event.stopPropagation()
  
  const target = event.target as HTMLElement
  const variableElement = target.closest('[data-variable]') as HTMLElement
  
  console.log('변수 클릭 감지:', { target: target.tagName, variableElement: !!variableElement })
  
  if (variableElement && props.isRejected) {
    const variableName = variableElement.getAttribute('data-variable')
    if (variableName && props.rejectedVariables.includes(variableName)) {
      // 반려된 변수 클릭 시 부모 컴포넌트에 이벤트 전달
      emit('variableClick', variableName)
    }
  }
}
// 편집 관련 이벤트 및 노출 제거

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

/* 수정 모드일 때 모든 변수를 연두색으로 표시 */
:deep(.variable.highlighted.clickable) {
  background-color: #d4edda !important;
  border: 1px solid #28a745 !important;
  color: #155724 !important;
}

/* 수정 모드일 때 모든 변수를 연두색으로 표시 (showVariables가 false일 때도) */
:deep(.variable.clickable) {
  background-color: #d4edda !important;
  border: 1px solid #28a745 !important;
  color: #155724 !important;
  cursor: pointer;
}

:deep(.variable.clickable:hover) {
  background-color: #c3e6cb !important;
  /* transform과 box-shadow 제거하여 스크롤 깜빡임 방지 */
  /* transform: scale(1.02); */
  /* box-shadow: 0 0.1rem 0.4rem rgba(40, 167, 69, 0.3); */
}

:deep(.variable.editable) {
  background-color: #e8f5e8;
  border: 0.1rem dashed #4caf50;
  position: relative;
}

:deep(.variable.editable:hover) {
  background-color: #d4edda;
  border-color: #28a745;
  /* transform과 box-shadow 제거하여 스크롤 깜빡임 방지 */
  /* transform: scale(1.02); */
  /* box-shadow: 0 0.1rem 0.4rem rgba(76, 175, 80, 0.3); */
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
  background-color: #d4edda !important;
  border: 0.1rem solid #28a745 !important;
  outline: none;
  cursor: text;
  /* box-shadow 제거하여 스크롤 깜빡임 방지 */
  /* box-shadow: 0 0 0 0.1rem rgba(40, 167, 69, 0.2); */
}

:deep(.variable.editing:focus) {
  background-color: #c3e6cb !important;
  border-color: #28a745 !important;
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
  /* transform 제거하여 스크롤 깜빡임 방지 */
  /* transform: scale(1.05); */
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