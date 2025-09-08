<template>
  <div class="variable-edit-section">
    <h4>변수 값 직접 수정</h4>
    <div class="variable-inputs">
      <div class="variable-input-group">
        <label>수신자:</label>
        <input 
          v-model="editedVariables.recipient" 
          type="text" 
          placeholder="수신자 이름 입력"
          class="variable-input"
        />
      </div>
      <div class="variable-input-group">
        <label>발신 스페이스:</label>
        <input 
          v-model="editedVariables.sender" 
          type="text" 
          placeholder="발신자 정보 입력"
          class="variable-input"
        />
      </div>
      <div class="variable-input-group">
        <label>쿠폰명:</label>
        <input 
          v-model="editedVariables.couponName" 
          type="text" 
          placeholder="쿠폰명 입력"
          class="variable-input"
        />
      </div>
      <div class="variable-input-group">
        <label>사용기한:</label>
        <input 
          v-model="editedVariables.expiryDate" 
          type="text" 
          placeholder="사용기한 입력"
          class="variable-input"
        />
      </div>
      <div class="variable-input-group">
        <label>추가 메시지:</label>
        <textarea 
          v-model="editedVariables.additionalMessage" 
          placeholder="추가 메시지 입력"
          class="variable-textarea"
          rows="3"
        ></textarea>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface VariableEditProps {
  variables: {
    recipient: string
    sender: string
    couponName: string
    expiryDate: string
    additionalMessage: string
  }
}

const props = defineProps<VariableEditProps>()
const emit = defineEmits<{
  update: [variables: any]
}>()

const editedVariables = ref({ ...props.variables })

watch(editedVariables, (newValues) => {
  emit('update', newValues)
}, { deep: true })
</script>

<style scoped>
.variable-edit-section {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  margin-top: 20px;
}

.variable-edit-section h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 1.1rem;
  font-weight: 600;
}

.variable-inputs {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.variable-input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.variable-input-group label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #555;
}

.variable-input,
.variable-textarea {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: border-color 0.2s ease;
}

.variable-input:focus,
.variable-textarea:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.variable-textarea {
  resize: vertical;
  min-height: 60px;
}
</style>
