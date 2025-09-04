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
        
        <div class="kakao-message">
          <p>안녕하세요, 
            <span v-if="props.showVariables && !isRejected" 
                  :class="['variable', { 'clickable': isModifying, 'editing': editingField === 'recipient' }]" 
                  :contenteditable="isModifying && editingField === 'recipient'"
                  @click="isModifying && startEditing('recipient')"
                  @blur="finishEditing('recipient')"
                  @keydown.enter.prevent="finishEditing('recipient')"
                  @keydown.esc="cancelEditing">{{ variables.recipient }}</span>
            <span v-else-if="isRejected && rejectedVariables.includes('수신자')" 
                  :class="['variable', 'rejected-highlight']"
                  @click="$emit('variableClick', '수신자')">{{ variables.recipient }}</span>
            <span v-else>{{ variables.recipient }}</span> 회원님!</p>
          
          <p>
            <span v-if="props.showVariables && !isRejected" 
                  :class="['variable', { 'clickable': isModifying, 'editing': editingField === 'sender' }]" 
                  :contenteditable="isModifying && editingField === 'sender'"
                  @click="isModifying && startEditing('sender')"
                  @blur="finishEditing('sender')"
                  @keydown.enter.prevent="finishEditing('sender')"
                  @keydown.esc="cancelEditing">{{ variables.sender }}</span>
            <span v-else-if="isRejected && rejectedVariables.includes('발신 스페이스')" 
                  :class="['variable', 'rejected-highlight']"
                  @click="$emit('variableClick', '발신 스페이스')">{{ variables.sender }}</span>
            <span v-else>{{ variables.sender }}</span>입니다.</p>
          
          <p>회원님께 발급된 쿠폰을 안내드립니다.</p>
          
          <p>▶ 쿠폰명 : 
            <span v-if="props.showVariables && !isRejected" 
                  :class="['variable', { 'clickable': isModifying, 'editing': editingField === 'couponName' }]" 
                  :contenteditable="isModifying && editingField === 'couponName'"
                  @click="isModifying && startEditing('couponName')"
                  @blur="finishEditing('couponName')"
                  @keydown.enter.prevent="finishEditing('couponName')"
                  @keydown.esc="cancelEditing">{{ variables.couponName }}</span>
            <span v-else-if="isRejected && rejectedVariables.includes('쿠폰명')" 
                  :class="['variable', 'rejected-highlight']"
                  @click="$emit('variableClick', '쿠폰명')">{{ variables.couponName }}</span>
            <span v-else>{{ variables.couponName }}</span></p>
          
          <p>▶ 사용기한 : 
            <span v-if="props.showVariables && !isRejected" 
                  :class="['variable', { 'clickable': isModifying, 'editing': editingField === 'expiryDate' }]" 
                  :contenteditable="isModifying && editingField === 'expiryDate'"
                  @click="isModifying && startEditing('expiryDate')"
                  @blur="finishEditing('expiryDate')"
                  @keydown.enter.prevent="finishEditing('expiryDate')"
                  @keydown.esc="cancelEditing">{{ variables.expiryDate }}</span>
            <span v-else-if="isRejected && rejectedVariables.includes('사용기한')" 
                  :class="['variable', 'rejected-highlight']"
                  @click="$emit('variableClick', '사용기한')">{{ variables.expiryDate }}</span>
            <span v-else>{{ variables.expiryDate }}</span></p>
          
          <p>
            <span v-if="props.showVariables && !isRejected" 
                  :class="['variable', { 'clickable': isModifying, 'editing': editingField === 'additionalMessage' }]" 
                  :contenteditable="isModifying && editingField === 'additionalMessage'"
                  @click="isModifying && startEditing('additionalMessage')"
                  @blur="finishEditing('additionalMessage')"
                  @keydown.enter.prevent="finishEditing('additionalMessage')"
                  @keydown.esc="cancelEditing">{{ variables.additionalMessage }}</span>
            <span v-else-if="isRejected && rejectedVariables.includes('추가 메시지')" 
                  :class="['variable', 'rejected-highlight']"
                  @click="$emit('variableClick', '추가 메시지')">{{ variables.additionalMessage }}</span>
            <span v-else>{{ variables.additionalMessage }}</span></p>
          
          <p class="disclaimer">* 이 메시지는 이용약관(계약서) 동의에 따라 지급된 쿠폰 안내 메시지입니다.</p>
        </div>
      </div>
    </div>
    
    <!-- 하단 컨트롤은 TemplateResultView에서 처리됨 -->
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

interface Variables {
  recipient: string
  sender: string
  couponName: string
  expiryDate: string
  additionalMessage: string
}

interface KakaoPreviewProps {
  showVariables: boolean
  variables: Variables
  isModifying: boolean
  isRejected: boolean
  rejectedVariables: string[]
}

const props = defineProps<KakaoPreviewProps>()
const emit = defineEmits<{
  variableClick: [variableName: string]

  rejectTemplate: []
  submitTemplate: []
  updateVariables: [variables: Variables]
}>()

const editedVariables = ref({ ...props.variables })
const editingField = ref<string | null>(null)
const originalValues = ref<Variables>({ ...props.variables })

// props.variables가 변경될 때마다 editedVariables 업데이트
watch(() => props.variables, (newVariables) => {
  editedVariables.value = { ...newVariables }
  originalValues.value = { ...newVariables }
}, { deep: true })

// 특정 필드 편집 시작
const startEditing = (fieldName: string) => {
  if (!props.isModifying) return
  
  editingField.value = fieldName
  originalValues.value[fieldName as keyof Variables] = editedVariables.value[fieldName as keyof Variables]
  
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
  const newValue = editedVariables.value[fieldName as keyof Variables]
  
  // 빈 값이면 원래 값으로 복원
  if (!newValue || newValue.trim() === '') {
    editedVariables.value[fieldName as keyof Variables] = originalValues.value[fieldName as keyof Variables]
  }
  
  editingField.value = null
  
  // 변경된 변수들을 부모에게 전달
  emit('updateVariables', editedVariables.value)
}

// 편집 취소
const cancelEditing = () => {
  if (editingField.value) {
    editedVariables.value[editingField.value as keyof Variables] = originalValues.value[editingField.value as keyof Variables]
    editingField.value = null
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
  width: 16rem;
  max-width: 16rem;
  flex-shrink: 0;
  align-self: center;
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
}

.kakao-message p {
  margin: 0.4rem 0;
}

.variable {
  background-color: #fff3cd;
  padding: 0.1rem 0.3rem;
  border-radius: 0.2rem;
  color: #856404;
  transition: all 0.2s ease;
  min-width: 1rem;
  display: inline-block;
}

.variable.clickable {
  cursor: pointer;
}

.variable.clickable:hover {
  background-color: #ffeaa7;
  transform: scale(1.02);
  box-shadow: 0 0.1rem 0.4rem rgba(0, 0, 0, 0.15);
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